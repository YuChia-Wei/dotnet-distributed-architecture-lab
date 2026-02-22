# WolverineFx + EF Core Outbox (Minimal)

```csharp
services.AddWolverine(opts =>
{
    opts.PersistMessagesWithEntityFrameworkCore();
    opts.UseEntityFrameworkCoreTransactions();
});
```
