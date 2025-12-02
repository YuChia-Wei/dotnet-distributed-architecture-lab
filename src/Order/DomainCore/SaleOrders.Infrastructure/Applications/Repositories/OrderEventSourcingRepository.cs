using System.Data;
using System.Text.Json;
using Dapper;
using Lab.BuildingBlocks.Domains;
using SaleOrders.Applications.Repositories;
using SaleOrders.Domains;
using SaleOrders.Domains.DomainEvents;

namespace SaleOrders.Infrastructure.Applications.Repositories;

public class OrderEventSourcingRepository : IOrderDomainRepository
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

    public async Task<Order?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
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

        var order = new Order();
        order.LoadFromHistory(domainEvents);

        return order;
    }

    public async Task AddAsync(Order order, CancellationToken cancellationToken = default)
    {
        await this.SaveAsync(order, cancellationToken);
    }

    public async Task UpdateAsync(Order order, CancellationToken cancellationToken = default)
    {
        await this.SaveAsync(order, cancellationToken);
    }

    public async Task<IEnumerable<Order>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        // WARNING: This is inefficient for a large number of aggregates.
        // A read model (projection) is a better approach for list views.
        const string sql = "SELECT DISTINCT StreamId FROM OrderEvents";
        var streamIds = await this._dbConnection.QueryAsync<Guid>(sql);

        var orders = new List<Order>();
        foreach (var streamId in streamIds)
        {
            var order = await this.GetByIdAsync(streamId, cancellationToken);
            if (order != null)
            {
                orders.Add(order);
            }
        }

        return orders;
    }

    public async Task DeleteAsync(Guid id, CancellationToken cancellationToken = default)
    {
        // This is a hard delete of the event stream, which is not standard practice in Event Sourcing.
        // A better approach is to use a 'deleted' event (soft delete).
        const string sql = "DELETE FROM OrderEvents WHERE StreamId = @StreamId";
        await this._dbConnection.ExecuteAsync(sql, new
        {
            StreamId = id
        });
    }

    private async Task SaveAsync(Order order, CancellationToken cancellationToken)
    {
        var events = order.DomainEvents.ToList();
        if (!events.Any())
        {
            return;
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

        transaction.Commit();

        await this._dispatcher.DispatchAsync(events, cancellationToken);
    }
}