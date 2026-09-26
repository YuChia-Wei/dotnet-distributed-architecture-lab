using System.Text.Json;
using Dapper;
using Lab.BoundedContextContracts.Procurement.IntegrationEvents;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Npgsql;
using Wolverine;

namespace Procurement.Infrastructure;

/// <summary>租用已提交收貨並交付 Wolverine 持久化寄件匣；失敗保留診斷資訊。</summary>
public sealed class ProcurementOutboxRelay(NpgsqlDataSource dataSource, IMessageBus bus,
    ILogger<ProcurementOutboxRelay> logger) : BackgroundService
{
    private const int MaxAttempts = 8;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try { await RelayBatchAsync(stoppingToken); }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested) { break; }
            catch (Exception exception) { logger.LogError(exception, "Procurement outbox batch failed."); }
            try { await Task.Delay(TimeSpan.FromSeconds(2), stoppingToken); }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested) { break; }
        }
    }

    /// <summary>交付一批待處理來源事件；published_at 表示傳輸持久化交接，不代表 Kafka 消費完成。</summary>
    public async Task<int> RelayBatchAsync(CancellationToken cancellationToken)
    {
        var lease = Guid.NewGuid();
        await using var connection = await dataSource.OpenConnectionAsync(cancellationToken);
        const string claim = """
            WITH claimed AS (
                SELECT id FROM procurement_outbox
                WHERE published_at IS NULL AND parked_at IS NULL AND next_attempt_at <= now()
                  AND (locked_until IS NULL OR locked_until < now())
                ORDER BY next_attempt_at, created_at, id
                FOR UPDATE SKIP LOCKED LIMIT 20
            )
            UPDATE procurement_outbox AS target
            SET locked_by=@Lease, locked_until=now()+interval '30 seconds', attempts=attempts+1
            FROM claimed WHERE target.id=claimed.id
            RETURNING target.id,target.partition_key,target.payload::text AS payload,target.attempts
            """;
        var rows = (await connection.QueryAsync<OutboxRow>(new CommandDefinition(claim,
            new { Lease = lease }, cancellationToken: cancellationToken))).ToArray();
        foreach (var row in rows)
        {
            cancellationToken.ThrowIfCancellationRequested();
            try
            {
                var message = JsonSerializer.Deserialize<GoodsReceived>(row.Payload)
                    ?? throw new JsonException("Outbox payload was empty.");
                if (message.ReceiptId != row.Id)
                    throw new JsonException("Outbox receipt identity differs from payload.");
                var options = new DeliveryOptions
                {
                    DeduplicationId = row.Id.ToString("N"),
                    PartitionKey = row.PartitionKey
                };
                options.WithHeader("lab-message-id", row.Id.ToString("D"));
                await bus.PublishAsync(message, options);
                // 只有 awaited Wolverine durable-outbox handoff 成功後才標記來源列；Kafka 實際送達需另查傳輸寄件匣。
                await connection.ExecuteAsync(new CommandDefinition("""
                    UPDATE procurement_outbox SET published_at=now(),locked_by=NULL,locked_until=NULL,last_error=NULL
                    WHERE id=@Id AND locked_by=@Lease
                    """, new { row.Id, Lease = lease }, cancellationToken: cancellationToken));
            }
            catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested) { throw; }
            catch (Exception exception)
            {
                var parked = row.Attempts >= MaxAttempts;
                var delay = Math.Min(120, 1 << Math.Min(row.Attempts, 7));
                var error = exception.ToString();
                if (error.Length > 4000) error = error[..4000];
                await connection.ExecuteAsync(new CommandDefinition("""
                    UPDATE procurement_outbox
                    SET locked_by=NULL,locked_until=NULL,last_error=@Error,
                        parked_at=CASE WHEN @Parked THEN now() ELSE NULL END,
                        next_attempt_at=CASE WHEN @Parked THEN next_attempt_at ELSE now()+(@Delay * interval '1 second') END
                    WHERE id=@Id AND locked_by=@Lease
                    """, new { row.Id, Lease = lease, Error = error, Parked = parked, Delay = delay },
                    cancellationToken: cancellationToken));
                logger.LogWarning(exception, "Procurement receipt {ReceiptId} publish attempt {Attempt} failed; parked={Parked}.",
                    row.Id, row.Attempts, parked);
            }
        }
        return rows.Length;
    }

    private sealed class OutboxRow
    {
        public Guid Id { get; set; }
        public string PartitionKey { get; set; } = "";
        public string Payload { get; set; } = "";
        public int Attempts { get; set; }
    }
}
