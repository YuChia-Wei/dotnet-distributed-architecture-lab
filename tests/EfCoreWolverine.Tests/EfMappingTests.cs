using EfCoreWolverine.Infrastructure;
using InventoryControl.Domains;
using Microsoft.EntityFrameworkCore;
using Shouldly;

namespace EfCoreWolverine.Tests;

public sealed class EfMappingTests
{
    [Fact]
    public void Given_the_current_mapping_when_compared_to_the_migration_then_no_pending_model_changes_exist()
    {
        using var db = GivenAContextWithoutConnecting();
        var hasChanges = db.Database.HasPendingModelChanges();
        hasChanges.ShouldBeFalse();
        db.Database.GenerateCreateScript().ShouldContain("ck_stock_nonnegative");
    }

    [Fact]
    public async Task Given_a_tracked_aggregate_when_repository_saves_then_changes_remain_pending_without_database_io()
    {
        await using var db = GivenAContextWithoutConnecting();
        var item = new InventoryItem(Guid.NewGuid(), 10);
        db.Attach(item);
        item.DecreaseStock(2);

        await new EfInventoryRepository(db).SaveAsync(item, TestContext.Current.CancellationToken);

        db.Entry(item).State.ShouldBe(EntityState.Modified);
        db.ChangeTracker.HasChanges().ShouldBeTrue();
        item.DomainEvents.Count.ShouldBe(1);
        db.Model.FindEntityType(typeof(InventoryItem))!.FindProperty("xmin")!.IsConcurrencyToken.ShouldBeTrue();
    }

    [Fact]
    public async Task Given_a_detached_aggregate_when_repository_saves_then_an_unenrolled_instance_is_rejected()
    {
        await using var db = GivenAContextWithoutConnecting();
        await Should.ThrowAsync<InvalidOperationException>(() => new EfInventoryRepository(db)
            .SaveAsync(new InventoryItem(Guid.NewGuid(), 10), TestContext.Current.CancellationToken));
    }

    private static InventoryDbContext GivenAContextWithoutConnecting()
        => new(new DbContextOptionsBuilder<InventoryDbContext>()
            .UseNpgsql("Host=localhost;Port=1;Database=unused;Username=unused;Timeout=1").Options);
}
