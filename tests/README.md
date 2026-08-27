# Test execution profiles

Ordinary `dotnet test` runs are the deterministic default. Tests that only parse RabbitMQ or Kafka configuration, use Wolverine in-memory transports, use mocks, or use in-memory repositories remain part of that default profile.

Tests that open a connection to PostgreSQL, RabbitMQ, Kafka, or another service outside the test process must:

1. use the `ExternalIntegration` category;
2. use an opt-in test attribute that reports the test as skipped when its prerequisites are absent;
3. document every required environment variable without committing credentials;
4. clean up only data uniquely created by that test.

The Inventory PostgreSQL profile is enabled explicitly in PowerShell:

```powershell
$env:RUN_EXTERNAL_INTEGRATION_TESTS = "true"
$env:INVENTORY_TEST_POSTGRES_CONNECTION_STRING = "Host=localhost;Port=5435;Database=inventory_db;Username=user;Password=<local-secret>"
dotnet test tests/InventoryControl.Tests/InventoryControl.Tests.csproj --filter "Category=ExternalIntegration"
```

The target database must already contain `InventoryItems`, `InventoryReservationOperations`, and `InventoryIntegrationOutbox`; apply both Inventory migrations documented in `.dev/operations/mq-topology.md` for an existing volume. The opted-in profile covers reservation concurrency plus ordinary stock/outbox atomic commit and expected-stock concurrency. Without the opt-in, all such tests are reported as skipped and remain non-passing external evidence.

Without both environment variables, the external test is skipped. A skipped external test is not passing evidence for PostgreSQL locking, reservation/outbox atomicity, or rollback behavior; release or reconstruction gates that require this evidence remain open until an opted-in run passes.
