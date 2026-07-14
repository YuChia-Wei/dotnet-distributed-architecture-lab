using System.Data;
using System.Text.Json;
using Dapper;
using Lab.BuildingBlocks.Application;
using Lab.BuildingBlocks.Domains;
using Lab.BuildingBlocks.Integrations;
using SaleOrders.Applications.Repositories;
using SaleOrders.Domains;
using SaleOrders.Domains.DomainEvents;

namespace SaleOrders.Infrastructure.Applications.Repositories;

// dapper connection control: ./docs/problem-note/dapper-dbconnection.md

public class OrderEventSourcingRepository : IOrderDomainRepository, IOrderEventCommitter
{
    private static readonly JsonSerializerOptions _jsonSerializerOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private static readonly Dictionary<string, Type> _eventTypeMap = new()
    {
        {
            nameof(OrderPlacedDomainEvent), typeof(OrderPlacedDomainEvent)
        },
        {
            nameof(OrderCancelledDomainEvent), typeof(OrderCancelledDomainEvent)
        },
        {
            nameof(OrderShippedDomainEvent), typeof(OrderShippedDomainEvent)
        },
        {
            nameof(OrderDeliveredDomainEvent), typeof(OrderDeliveredDomainEvent)
        }
    };

    private readonly IDbConnection _dbConnection;
    private readonly IDomainEventDispatcher _dispatcher;

    public OrderEventSourcingRepository(IDbConnection dbConnection, IDomainEventDispatcher dispatcher)
    {
        this._dbConnection = dbConnection;
        this._dispatcher = dispatcher;
    }

    public async Task<Order?> FindByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        const string sql = "SELECT EventType, Data FROM OrderEvents WHERE StreamId = @StreamId ORDER BY Version";
        var eventsData = await this._dbConnection.QueryAsync<(string EventType, string Data)>(sql, new
        {
            StreamId = id
        });

        var eventTuples = eventsData.ToList();
        if (!eventTuples.Any())
        {
            return null;
        }

        var domainEvents = eventTuples.Select(e =>
        {
            var eventType = _eventTypeMap[e.EventType];
            var domainEvent = (IDomainEvent)JsonSerializer.Deserialize(e.Data, eventType, _jsonSerializerOptions)!;
            return domainEvent;
        }).ToList();

        var order = new Order(domainEvents);

        return order;
    }

    public Task SaveAsync(Order order, CancellationToken cancellationToken = default)
    {
        return this.CommitCoreAsync(order, Array.Empty<IIntegrationEvent>(), cancellationToken);
    }

    /// <inheritdoc />
    public Task CommitAsync(
        Order order,
        IReadOnlyCollection<IIntegrationEvent> integrationEvents,
        CancellationToken cancellationToken)
        => this.CommitCoreAsync(order, integrationEvents, cancellationToken);

    private async Task CommitCoreAsync(
        Order order,
        IReadOnlyCollection<IIntegrationEvent> integrationEvents,
        CancellationToken cancellationToken)
    {
        var events = order.DomainEvents.ToList();
        if (!events.Any())
        {
            return;
        }

        // Ensure the connection is open before starting a transaction.
        // Dapper will auto-open/close around its own commands when the connection is closed,
        // but ADO.NET requires an explicitly open connection for BeginTransaction().
        if (this._dbConnection.State != ConnectionState.Open)
        {
            this._dbConnection.Open();
        }

        const string versionSql = "SELECT MAX(Version) FROM OrderEvents WHERE StreamId = @StreamId";
        var dbVersion = await this._dbConnection.ExecuteScalarAsync<int?>(versionSql, new
        {
            StreamId = order.Id
        });
        var currentDbVersion = dbVersion ?? 0;

        if (order.Version != currentDbVersion)
        {
            throw new DBConcurrencyException(
                $"Concurrency conflict for Order {order.Id}. Expected version {order.Version}, but database version is {currentDbVersion}.");
        }

        using var transaction = this._dbConnection.BeginTransaction();

        var nextVersion = order.Version;
        try
        {
            foreach (var @event in events)
            {
                nextVersion++;
                var eventType = @event.GetType().Name;
                var data = JsonSerializer.Serialize(@event, @event.GetType(), _jsonSerializerOptions);

                const string insertSql = @"
                INSERT INTO OrderEvents (StreamId, Version, EventType, Data, Timestamp)
                VALUES (@StreamId, @Version, @EventType, @Data::jsonb, @Timestamp)";

                await this._dbConnection.ExecuteAsync(insertSql, new
                {
                    StreamId = order.Id,
                    Version = nextVersion,
                    EventType = eventType,
                    Data = data,
                    Timestamp = DateTime.UtcNow
                }, transaction);
            }

            foreach (var integrationEvent in integrationEvents)
            {
                const string outboxSql = @"
                INSERT INTO OrderIntegrationOutbox (Id, AggregateId, MessageType, Data, OccurredOn)
                VALUES (@Id, @AggregateId, @MessageType, @Data::jsonb, @OccurredOn)";

                await this._dbConnection.ExecuteAsync(outboxSql, new
                {
                    Id = Guid.CreateVersion7(),
                    AggregateId = order.Id,
                    MessageType = integrationEvent.GetType().Name,
                    Data = JsonSerializer.Serialize(integrationEvent, integrationEvent.GetType(), _jsonSerializerOptions),
                    integrationEvent.OccurredOn
                }, transaction);
            }

            const string readModelSql = @"
            INSERT INTO Orders (Id, OrderDate, TotalAmount, ProductId, ProductName, Quantity)
            VALUES (@Id, @OrderDate, @TotalAmount, @ProductId, @ProductName, @Quantity)
            ON CONFLICT (Id) DO UPDATE
            SET OrderDate = EXCLUDED.OrderDate,
                TotalAmount = EXCLUDED.TotalAmount,
                ProductId = EXCLUDED.ProductId,
                ProductName = EXCLUDED.ProductName,
                Quantity = EXCLUDED.Quantity";

            await this._dbConnection.ExecuteAsync(
                readModelSql,
                new
                {
                    order.Id,
                    order.OrderDate,
                    order.TotalAmount,
                    order.ProductId,
                    order.ProductName,
                    order.Quantity
                },
                transaction);

            transaction.Commit();
        }
        catch
        {
            transaction.Rollback();
            throw;
        }

        order.MarkChangesAsCommitted(nextVersion);
        await this._dispatcher.DispatchAsync(events, cancellationToken);
    }
}
