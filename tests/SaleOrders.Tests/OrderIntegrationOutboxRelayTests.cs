using System.Collections;
using System.Data;
using System.Data.Common;
using System.Diagnostics.CodeAnalysis;
using System.Reflection;
using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using Microsoft.Extensions.DependencyInjection;
using NSubstitute;
using SaleOrders.Infrastructure.BuildingBlocks;
using Shouldly;
using Wolverine;

namespace SaleOrders.Tests;

/// <summary>Protects stable delivery identity across Orders outbox retries.</summary>
public sealed class OrderIntegrationOutboxRelayTests
{
    /// <summary>A failed publish must not replace the source row identity on retry.</summary>
    [Fact]
    public async Task given_the_same_claimed_row_when_publish_is_retried_then_delivery_identity_is_stable()
    {
        // Given
        var rowId = Guid.CreateVersion7();
        var aggregateId = Guid.CreateVersion7();
        var connection = new OutboxDbConnection(
            rowId,
            aggregateId,
            nameof(OrderCancelled),
            $$"""{"OrderId":"{{aggregateId}}","Reason":"customer request","OccurredOn":"2026-07-14T00:00:00Z"}""");
        var publisher = new RetryRecordingPublisher();
        var relay = CreateRelay(connection, publisher);

        // When
        await RelayBatchAsync(relay);
        await RelayBatchAsync(relay);

        // Then
        publisher.Deliveries.Count.ShouldBe(2);
        publisher.Deliveries.ShouldAllBe(delivery => delivery.MessageId == rowId);
        publisher.Deliveries.ShouldAllBe(delivery => delivery.PartitionKey == aggregateId.ToString("D"));
        connection.DeleteCount.ShouldBe(1);
    }

    /// <summary>The Wolverine adapter must preserve stable deduplication metadata.</summary>
    [Fact]
    public async Task given_the_same_delivery_when_published_twice_then_wolverine_metadata_is_stable()
    {
        // Given
        var messageId = Guid.CreateVersion7();
        var delivery = new IntegrationMessageDelivery(messageId, "order-42");
        var capturedOptions = new List<DeliveryOptions>();
        var messageBus = Substitute.For<IMessageBus>();
        messageBus.PublishAsync(
                      Arg.Any<IIntegrationEvent>(),
                      Arg.Do<DeliveryOptions>(options => capturedOptions.Add(options)))
                  .Returns(ValueTask.CompletedTask);
        var publisher = new IntegrationEventPublisher(
            messageBus,
            Substitute.For<Microsoft.Extensions.Logging.ILogger<IntegrationEventPublisher>>());
        var integrationEvent = new OrderCancelled(Guid.CreateVersion7(), "customer request");

        // When
        await publisher.PublishAsync(integrationEvent, delivery);
        await publisher.PublishAsync(integrationEvent, delivery);

        // Then
        capturedOptions.Count.ShouldBe(2);
        capturedOptions.ShouldAllBe(options => options.DeduplicationId == messageId.ToString("N"));
        capturedOptions.ShouldAllBe(options => options.PartitionKey == "order-42");
        capturedOptions.ShouldAllBe(options => options.Headers["lab-message-id"] == messageId.ToString("D"));
    }

    private static object CreateRelay(IDbConnection connection, IIntegrationEventPublisher publisher)
    {
        var relayType = typeof(IntegrationEventPublisher).Assembly.GetType(
            "SaleOrders.Infrastructure.BuildingBlocks.OrderIntegrationOutboxRelay",
            throwOnError: true)!;
        var services = new ServiceCollection()
            .AddSingleton(connection)
            .AddSingleton(publisher)
            .BuildServiceProvider();
        var scopeFactory = services.GetRequiredService<IServiceScopeFactory>();
        var loggerType = typeof(Microsoft.Extensions.Logging.Abstractions.NullLogger<>).MakeGenericType(relayType);
        var logger = loggerType.GetField("Instance", BindingFlags.Public | BindingFlags.Static)!.GetValue(null);

        return Activator.CreateInstance(relayType, scopeFactory, logger)!;
    }

    private static async Task RelayBatchAsync(object relay)
    {
        var method = relay.GetType().GetMethod("RelayBatchAsync", BindingFlags.Instance | BindingFlags.NonPublic)!;
        await (Task)method.Invoke(relay, [CancellationToken.None])!;
    }

    private sealed class RetryRecordingPublisher : IIntegrationEventPublisher
    {
        public List<IntegrationMessageDelivery> Deliveries { get; } = [];

        public Task PublishAsync(IIntegrationEvent integrationEvent)
            => throw new NotSupportedException();

        public Task PublishAsync(IIntegrationEvent integrationEvent, IntegrationMessageDelivery delivery)
        {
            this.Deliveries.Add(delivery);
            if (this.Deliveries.Count == 1)
            {
                throw new InvalidOperationException("Simulated transport failure.");
            }

            return Task.CompletedTask;
        }
    }

    private sealed class OutboxDbConnection(
        Guid rowId,
        Guid aggregateId,
        string messageType,
        string data) : DbConnection
    {
        private ConnectionState _state = ConnectionState.Closed;

        public int DeleteCount { get; private set; }

        [AllowNull]
        public override string ConnectionString { get; set; } = string.Empty;

        public override string Database => "orders-tests";

        public override string DataSource => "in-memory";

        public override string ServerVersion => "1.0";

        public override ConnectionState State => this._state;

        public override void ChangeDatabase(string databaseName)
        {
        }

        public override void Close() => this._state = ConnectionState.Closed;

        public override void Open() => this._state = ConnectionState.Open;

        protected override DbTransaction BeginDbTransaction(IsolationLevel isolationLevel)
            => throw new NotSupportedException();

        protected override DbCommand CreateDbCommand()
            => new OutboxDbCommand(this, CreateReader, RecordExecution);

        private DbDataReader CreateReader()
        {
            var table = new DataTable();
            table.Columns.Add("Id", typeof(Guid));
            table.Columns.Add("AggregateId", typeof(Guid));
            table.Columns.Add("MessageType", typeof(string));
            table.Columns.Add("Data", typeof(string));
            table.Columns.Add("Attempts", typeof(int));
            if (this.DeleteCount == 0)
            {
                table.Rows.Add(rowId, aggregateId, messageType, data, 1);
            }

            return table.CreateDataReader();
        }

        private int RecordExecution(string commandText)
        {
            if (commandText.TrimStart().StartsWith("DELETE", StringComparison.OrdinalIgnoreCase))
            {
                this.DeleteCount++;
            }

            return 1;
        }
    }

    private sealed class OutboxDbCommand(
        DbConnection connection,
        Func<DbDataReader> createReader,
        Func<string, int> recordExecution) : DbCommand
    {
        private readonly DbParameterCollection _parameters = new TestDbParameterCollection();

        [AllowNull]
        public override string CommandText { get; set; } = string.Empty;

        public override int CommandTimeout { get; set; }

        public override CommandType CommandType { get; set; }

        public override bool DesignTimeVisible { get; set; }

        public override UpdateRowSource UpdatedRowSource { get; set; }

        [AllowNull]
        protected override DbConnection DbConnection { get; set; } = connection;

        protected override DbParameterCollection DbParameterCollection => this._parameters;

        protected override DbTransaction? DbTransaction { get; set; }

        public override void Cancel()
        {
        }

        public override int ExecuteNonQuery() => recordExecution(this.CommandText);

        public override object? ExecuteScalar() => throw new NotSupportedException();

        public override void Prepare()
        {
        }

        protected override DbParameter CreateDbParameter() => new TestDbParameter();

        protected override DbDataReader ExecuteDbDataReader(CommandBehavior behavior) => createReader();

        public override Task<int> ExecuteNonQueryAsync(CancellationToken cancellationToken)
            => Task.FromResult(recordExecution(this.CommandText));

        protected override Task<DbDataReader> ExecuteDbDataReaderAsync(
            CommandBehavior behavior,
            CancellationToken cancellationToken)
            => Task.FromResult(createReader());
    }

    private sealed class TestDbParameter : DbParameter
    {
        public override DbType DbType { get; set; }

        public override ParameterDirection Direction { get; set; } = ParameterDirection.Input;

        public override bool IsNullable { get; set; }

        [AllowNull]
        public override string ParameterName { get; set; } = string.Empty;

        public override int Size { get; set; }

        [AllowNull]
        public override string SourceColumn { get; set; } = string.Empty;

        public override bool SourceColumnNullMapping { get; set; }

        public override object? Value { get; set; }

        public override void ResetDbType()
        {
        }
    }

    private sealed class TestDbParameterCollection : DbParameterCollection
    {
        private readonly List<DbParameter> _parameters = [];

        public override int Count => this._parameters.Count;

        public override object SyncRoot => ((ICollection)this._parameters).SyncRoot;

        public override int Add(object value)
        {
            this._parameters.Add((DbParameter)value);
            return this._parameters.Count - 1;
        }

        public override void AddRange(Array values)
        {
            foreach (var value in values)
            {
                this.Add(value!);
            }
        }

        public override void Clear() => this._parameters.Clear();

        public override bool Contains(object value) => this._parameters.Contains((DbParameter)value);

        public override bool Contains(string value)
            => this._parameters.Any(parameter => parameter.ParameterName == value);

        public override void CopyTo(Array array, int index)
            => ((ICollection)this._parameters).CopyTo(array, index);

        public override IEnumerator GetEnumerator() => this._parameters.GetEnumerator();

        public override int IndexOf(object value) => this._parameters.IndexOf((DbParameter)value);

        public override int IndexOf(string parameterName)
            => this._parameters.FindIndex(parameter => parameter.ParameterName == parameterName);

        public override void Insert(int index, object value)
            => this._parameters.Insert(index, (DbParameter)value);

        public override void Remove(object value) => this._parameters.Remove((DbParameter)value);

        public override void RemoveAt(int index) => this._parameters.RemoveAt(index);

        public override void RemoveAt(string parameterName) => this._parameters.RemoveAt(this.IndexOf(parameterName));

        protected override DbParameter GetParameter(int index) => this._parameters[index];

        protected override DbParameter GetParameter(string parameterName)
            => this._parameters[this.IndexOf(parameterName)];

        protected override void SetParameter(int index, DbParameter value) => this._parameters[index] = value;

        protected override void SetParameter(string parameterName, DbParameter value)
        {
            var index = this.IndexOf(parameterName);
            if (index < 0)
            {
                this._parameters.Add(value);
                return;
            }

            this._parameters[index] = value;
        }
    }
}
