using System.Collections;
using System.Data;
using System.Data.Common;
using System.Diagnostics.CodeAnalysis;
using System.Reflection;
using InventoryControl.Infrastructure.BuildingBlocks;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;
using Microsoft.Extensions.DependencyInjection;
using NSubstitute;
using Shouldly;
using Wolverine;

namespace InventoryControl.Tests;

public sealed class InventoryIntegrationOutboxRelayTests
{
    [Fact]
    public async Task given_a_stable_delivery_when_published_then_wolverine_metadata_matches_the_outbox_identity()
    {
        // Given
        var messageId = Guid.CreateVersion7();
        var partitionKey = Guid.CreateVersion7().ToString("N");
        var capturedOptions = new List<DeliveryOptions>();
        var messageBus = Substitute.For<IMessageBus>();
        messageBus.PublishAsync(
                Arg.Any<IIntegrationEvent>(),
                Arg.Do<DeliveryOptions>(options => capturedOptions.Add(options)))
            .Returns(ValueTask.CompletedTask);
        var publisher = new IntegrationEventPublisher(
            messageBus,
            Substitute.For<Microsoft.Extensions.Logging.ILogger<IntegrationEventPublisher>>());
        var message = new ProductStockDecreasedIntegrationEvent(
            Guid.CreateVersion7(),
            Guid.CreateVersion7(),
            2,
            3);

        // When
        await publisher.PublishAsync(message, new IntegrationMessageDelivery(messageId, partitionKey));

        // Then
        var options = capturedOptions.ShouldHaveSingleItem();
        options.DeduplicationId.ShouldBe(messageId.ToString("N"));
        options.PartitionKey.ShouldBe(partitionKey);
        options.Headers["lab-message-id"].ShouldBe(messageId.ToString("D"));
    }

    [Fact]
    public async Task given_the_same_claimed_row_when_publish_is_retried_then_delivery_identity_and_event_time_are_stable()
    {
        // Given
        var rowId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        var inventoryItemId = Guid.CreateVersion7();
        var occurredOn = new DateTime(2026, 8, 27, 0, 0, 0, DateTimeKind.Utc);
        var partitionKey = productId.ToString("N");
        var connection = new OutboxDbConnection(
            rowId,
            partitionKey,
            nameof(ProductStockDecreasedIntegrationEvent),
            $$"""{"InventoryItemId":"{{inventoryItemId}}","ProductId":"{{productId}}","DecreasedQuantity":2,"CurrentStock":3,"OccurredOn":"{{occurredOn:O}}"}""");
        var publisher = new RetryRecordingPublisher();
        var relay = CreateRelay(connection, publisher);

        // When
        await RelayBatchAsync(relay);
        await RelayBatchAsync(relay);

        // Then
        publisher.Deliveries.Count.ShouldBe(2);
        publisher.Deliveries.ShouldAllBe(delivery => delivery.MessageId == rowId);
        publisher.Deliveries.ShouldAllBe(delivery => delivery.PartitionKey == partitionKey);
        publisher.Messages.ShouldAllBe(message => message.OccurredOn == occurredOn);
        connection.PublishedCount.ShouldBe(1);
        connection.FailureCount.ShouldBe(1);
    }

    [Fact]
    public async Task given_five_transport_failures_when_relay_runs_again_then_the_row_is_parked_and_not_republished()
    {
        // Given
        var rowId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        var connection = new OutboxDbConnection(
            rowId,
            productId.ToString("N"),
            nameof(ProductStockDecreasedIntegrationEvent),
            $$"""{"InventoryItemId":"{{Guid.CreateVersion7()}}","ProductId":"{{productId}}","DecreasedQuantity":1,"CurrentStock":2,"OccurredOn":"2026-08-27T00:00:00.0000000Z"}""");
        var publisher = new AlwaysFailPublisher();
        var relay = CreateRelay(connection, publisher);

        // When
        for (var attempt = 0; attempt < 6; attempt++)
        {
            await RelayBatchAsync(relay);
        }

        // Then
        publisher.Attempts.ShouldBe(5);
        connection.FailureCount.ShouldBe(5);
        connection.ParkedCount.ShouldBe(1);
    }

    [Fact]
    public async Task given_finite_published_retention_when_relay_runs_then_expired_published_rows_are_pruned()
    {
        // Given
        var productId = Guid.CreateVersion7();
        var connection = new OutboxDbConnection(
            Guid.CreateVersion7(),
            productId.ToString("N"),
            nameof(ProductStockIncreasedIntegrationEvent),
            $$"""{"InventoryItemId":"{{Guid.CreateVersion7()}}","ProductId":"{{productId}}","IncreasedQuantity":1,"CurrentStock":3,"OccurredOn":"2026-08-27T00:00:00.0000000Z"}""");
        var relay = CreateRelay(
            connection,
            new RetryRecordingPublisher(),
            new InventoryOutboxRelayOptions(
                true,
                InventoryOutboxRetentionMode.PublishedForDays,
                30));

        // When
        await RelayBatchAsync(relay);

        // Then
        connection.RetentionDeleteCount.ShouldBe(1);
    }

    private static object CreateRelay(
        IDbConnection connection,
        IIntegrationEventPublisher publisher,
        InventoryOutboxRelayOptions? options = null)
    {
        var relayType = typeof(IntegrationEventPublisher).Assembly.GetType(
            "InventoryControl.Infrastructure.BuildingBlocks.InventoryIntegrationOutboxRelay",
            throwOnError: true)!;
        var services = new ServiceCollection()
            .AddSingleton(connection)
            .AddSingleton(publisher)
            .BuildServiceProvider();
        var scopeFactory = services.GetRequiredService<IServiceScopeFactory>();
        var loggerType = typeof(Microsoft.Extensions.Logging.Abstractions.NullLogger<>).MakeGenericType(relayType);
        var logger = loggerType.GetField("Instance", BindingFlags.Public | BindingFlags.Static)!.GetValue(null);

        return Activator.CreateInstance(
            relayType,
            scopeFactory,
            options ?? new InventoryOutboxRelayOptions(
                false,
                InventoryOutboxRetentionMode.RetainAll,
                null),
            logger)!;
    }

    private static async Task RelayBatchAsync(object relay)
    {
        var method = relay.GetType().GetMethod("RelayBatchAsync", BindingFlags.Instance | BindingFlags.NonPublic)!;
        await (Task)method.Invoke(relay, [CancellationToken.None])!;
    }

    private sealed class RetryRecordingPublisher : IIntegrationEventPublisher
    {
        public List<IIntegrationEvent> Messages { get; } = [];
        public List<IntegrationMessageDelivery> Deliveries { get; } = [];

        public Task PublishAsync(IIntegrationEvent integrationEvent)
            => throw new NotSupportedException();

        public Task PublishAsync(IIntegrationEvent integrationEvent, IntegrationMessageDelivery delivery)
        {
            this.Messages.Add(integrationEvent);
            this.Deliveries.Add(delivery);
            return this.Deliveries.Count == 1
                ? Task.FromException(new InvalidOperationException("Simulated transport failure."))
                : Task.CompletedTask;
        }
    }

    private sealed class AlwaysFailPublisher : IIntegrationEventPublisher
    {
        public int Attempts { get; private set; }

        public Task PublishAsync(IIntegrationEvent integrationEvent)
            => throw new NotSupportedException();

        public Task PublishAsync(IIntegrationEvent integrationEvent, IntegrationMessageDelivery delivery)
        {
            this.Attempts++;
            return Task.FromException(new InvalidOperationException("Simulated persistent transport failure."));
        }
    }

    private sealed class OutboxDbConnection(
        Guid rowId,
        string partitionKey,
        string messageType,
        string data) : DbConnection
    {
        private ConnectionState state = ConnectionState.Closed;
        private bool parked;

        public int PublishedCount { get; private set; }
        public int FailureCount { get; private set; }
        public int ParkedCount { get; private set; }
        public int RetentionDeleteCount { get; private set; }

        [AllowNull]
        public override string ConnectionString { get; set; } = string.Empty;

        public override string Database => "inventory-tests";
        public override string DataSource => "in-memory";
        public override string ServerVersion => "1.0";
        public override ConnectionState State => this.state;

        public override void ChangeDatabase(string databaseName)
        {
        }

        public override void Close() => this.state = ConnectionState.Closed;
        public override void Open() => this.state = ConnectionState.Open;

        protected override DbTransaction BeginDbTransaction(IsolationLevel isolationLevel)
            => throw new NotSupportedException();

        protected override DbCommand CreateDbCommand()
            => new OutboxDbCommand(this, this.CreateReader, this.RecordExecution);

        private DbDataReader CreateReader()
        {
            var table = new DataTable();
            table.Columns.Add("Id", typeof(Guid));
            table.Columns.Add("PartitionKey", typeof(string));
            table.Columns.Add("MessageType", typeof(string));
            table.Columns.Add("Data", typeof(string));
            table.Columns.Add("Attempts", typeof(int));
            if (this.PublishedCount == 0 && !this.parked)
            {
                table.Rows.Add(rowId, partitionKey, messageType, data, this.FailureCount + 1);
            }

            return table.CreateDataReader();
        }

        private int RecordExecution(string commandText, DbParameterCollection parameters)
        {
            if (commandText.Contains("SET PublishedAt = NOW()", StringComparison.OrdinalIgnoreCase))
            {
                this.PublishedCount++;
            }
            else if (commandText.Contains("SET LockId = NULL", StringComparison.OrdinalIgnoreCase))
            {
                this.FailureCount++;
                this.parked = parameters
                    .Cast<DbParameter>()
                    .Single(parameter => parameter.ParameterName == "IsParked")
                    .Value is true;
                if (this.parked)
                {
                    this.ParkedCount++;
                }
            }
            else if (commandText.Contains("DELETE FROM InventoryIntegrationOutbox", StringComparison.OrdinalIgnoreCase))
            {
                this.RetentionDeleteCount++;
            }

            return 1;
        }
    }

    private sealed class OutboxDbCommand(
        DbConnection connection,
        Func<DbDataReader> createReader,
        Func<string, DbParameterCollection, int> recordExecution) : DbCommand
    {
        private readonly DbParameterCollection parameters = new TestDbParameterCollection();

        [AllowNull]
        public override string CommandText { get; set; } = string.Empty;
        public override int CommandTimeout { get; set; }
        public override CommandType CommandType { get; set; }
        public override bool DesignTimeVisible { get; set; }
        public override UpdateRowSource UpdatedRowSource { get; set; }

        [AllowNull]
        protected override DbConnection DbConnection { get; set; } = connection;
        protected override DbParameterCollection DbParameterCollection => this.parameters;
        protected override DbTransaction? DbTransaction { get; set; }

        public override void Cancel()
        {
        }

        public override int ExecuteNonQuery() => recordExecution(this.CommandText, this.parameters);
        public override object? ExecuteScalar() => throw new NotSupportedException();
        public override void Prepare()
        {
        }

        protected override DbParameter CreateDbParameter() => new TestDbParameter();
        protected override DbDataReader ExecuteDbDataReader(CommandBehavior behavior) => createReader();
        public override Task<int> ExecuteNonQueryAsync(CancellationToken cancellationToken)
            => Task.FromResult(recordExecution(this.CommandText, this.parameters));
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
        private readonly List<DbParameter> parameters = [];

        public override int Count => this.parameters.Count;
        public override object SyncRoot => ((ICollection)this.parameters).SyncRoot;

        public override int Add(object value)
        {
            this.parameters.Add((DbParameter)value);
            return this.parameters.Count - 1;
        }

        public override void AddRange(Array values)
        {
            foreach (var value in values)
            {
                this.Add(value!);
            }
        }

        public override void Clear() => this.parameters.Clear();
        public override bool Contains(object value) => this.parameters.Contains((DbParameter)value);
        public override bool Contains(string value)
            => this.parameters.Any(parameter => parameter.ParameterName == value);
        public override void CopyTo(Array array, int index)
            => ((ICollection)this.parameters).CopyTo(array, index);
        public override IEnumerator GetEnumerator() => this.parameters.GetEnumerator();
        public override int IndexOf(object value) => this.parameters.IndexOf((DbParameter)value);
        public override int IndexOf(string parameterName)
            => this.parameters.FindIndex(parameter => parameter.ParameterName == parameterName);
        public override void Insert(int index, object value)
            => this.parameters.Insert(index, (DbParameter)value);
        public override void Remove(object value) => this.parameters.Remove((DbParameter)value);
        public override void RemoveAt(int index) => this.parameters.RemoveAt(index);
        public override void RemoveAt(string parameterName) => this.parameters.RemoveAt(this.IndexOf(parameterName));
        protected override DbParameter GetParameter(int index) => this.parameters[index];
        protected override DbParameter GetParameter(string parameterName)
            => this.parameters[this.IndexOf(parameterName)];
        protected override void SetParameter(int index, DbParameter value) => this.parameters[index] = value;

        protected override void SetParameter(string parameterName, DbParameter value)
        {
            var index = this.IndexOf(parameterName);
            if (index < 0)
            {
                this.parameters.Add(value);
                return;
            }

            this.parameters[index] = value;
        }
    }
}
