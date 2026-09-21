using InventoryControl.Applications.Outbox;
using InventoryControl.Applications.Queries;
using InventoryControl.Applications.Repositories;
using InventoryControl.Applications.Reservations;
using InventoryControl.Domains;
using InventoryControl.Infrastructure;
using InventoryControl.Infrastructure.Applications.Repositories;
using InventoryControl.Infrastructure.Persistence;
using Lab.BuildingBlocks.Application;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using NSubstitute;
using Shouldly;

namespace InventoryControl.Tests;

/// <summary>AC1/AC2: EF model, scoped registration, SQL-created rows, repository initialization and projections.</summary>
public sealed class InventoryEfPersistenceTests
{
    [Fact]
    public void given_existing_inventory_schema_when_model_is_built_then_only_persisted_domain_fields_are_mapped()
    {
        using var context = GivenContextWithoutConnecting();
        var entity = WhenReadingInventoryMapping(context);
        ThenMappingShouldMatchExistingSchema(entity);
    }

    [Fact]
    public void given_inventory_registration_when_scopes_are_resolved_then_repository_ports_share_the_scoped_context_boundary()
    {
        using var services = GivenInfrastructureServices();
        using var first = services.CreateScope();
        using var second = services.CreateScope();
        var (domain, queries, stock, reservation) = WhenResolvingPersistencePorts(first.ServiceProvider);
        ThenPortsShouldResolveWithinTheirScope(first.ServiceProvider, second.ServiceProvider, domain, queries, stock, reservation);
    }

    [ExternalIntegrationFact]
    public async Task given_a_row_created_with_existing_sql_when_queried_then_the_no_tracking_projection_preserves_its_values()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var itemId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        await GivenExistingSqlRow(database, itemId, productId, 7);
        await using var context = database.CreateContext();
        var result = await WhenQueryingProduct(context, productId);
        ThenProjectionShouldBeUntracked(context, result, itemId, productId, 7);
    }

    [ExternalIntegrationFact]
    public async Task given_a_new_inventory_item_when_repository_saves_then_a_fresh_context_can_query_it()
    {
        await using var database = await InventoryPostgresDatabase.CreateAsync();
        var item = GivenNewItem(9);
        await WhenSavingItem(database, item);
        await ThenFreshContextShouldReadItem(database, item, 9);
    }

    private static InventoryDbContext GivenContextWithoutConnecting()
        => new(new DbContextOptionsBuilder<InventoryDbContext>().UseNpgsql("Host=localhost;Database=inventory_model_only").Options);

    private static IEntityType WhenReadingInventoryMapping(InventoryDbContext context)
        => context.Model.FindEntityType(typeof(InventoryItem))!;

    private static void ThenMappingShouldMatchExistingSchema(IEntityType entity)
    {
        entity.GetTableName().ShouldBe("inventoryitems");
        var table = StoreObjectIdentifier.Table("inventoryitems", null);
        entity.GetProperties().Select(property => property.GetColumnName(table)).Order().ShouldBe(["id", "productid", "stock"]);
        entity.FindProperty(nameof(InventoryItem.Version)).ShouldBeNull();
        entity.FindNavigation(nameof(InventoryItem.DomainEvents)).ShouldBeNull();
        entity.GetIndexes().ShouldHaveSingleItem().IsUnique.ShouldBeTrue();
    }

    private static ServiceProvider GivenInfrastructureServices()
    {
        var configuration = new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string, string?>
        {
            ["ConnectionStrings:DefaultConnection"] = "Host=localhost;Database=inventory_di_only"
        }).Build();
        var services = new ServiceCollection();
        services.AddInfrastructureServices(configuration);
        services.AddScoped(_ => Substitute.For<IDomainEventDispatcher>());
        return services.BuildServiceProvider(new ServiceProviderOptions { ValidateScopes = true });
    }

    private static (IInventoryItemDomainRepository, IInventoryItemQueryRepository, IInventoryStockOutbox, IInventoryReservationOutbox)
        WhenResolvingPersistencePorts(IServiceProvider services)
        => (services.GetRequiredService<IInventoryItemDomainRepository>(), services.GetRequiredService<IInventoryItemQueryRepository>(),
            services.GetRequiredService<IInventoryStockOutbox>(), services.GetRequiredService<IInventoryReservationOutbox>());

    private static void ThenPortsShouldResolveWithinTheirScope(IServiceProvider first, IServiceProvider second,
        IInventoryItemDomainRepository domain, IInventoryItemQueryRepository queries, IInventoryStockOutbox stock, IInventoryReservationOutbox reservation)
    {
        domain.ShouldBeSameAs(queries);
        domain.ShouldBeOfType<InventoryItemDomainRepository>();
        stock.ShouldBeOfType<PostgresInventoryStockOutbox>();
        reservation.ShouldBeOfType<PostgresInventoryReservationRepository>();
        first.GetRequiredService<InventoryDbContext>().ShouldBeSameAs(first.GetRequiredService<InventoryDbContext>());
        first.GetRequiredService<InventoryDbContext>().ShouldNotBeSameAs(second.GetRequiredService<InventoryDbContext>());
        domain.ShouldNotBeSameAs(second.GetRequiredService<IInventoryItemDomainRepository>());
    }

    private static async Task GivenExistingSqlRow(InventoryPostgresDatabase database, Guid id, Guid productId, int stock)
    {
        await using var context = database.CreateContext();
        await context.Database.ExecuteSqlAsync($"INSERT INTO InventoryItems (Id, ProductId, Stock) VALUES ({id}, {productId}, {stock})");
    }

    private static Task<InventoryItemReadModel?> WhenQueryingProduct(InventoryDbContext context, Guid productId)
        => new InventoryItemDomainRepository(context, Substitute.For<IDomainEventDispatcher>()).FindByProductIdAsync(productId);

    private static void ThenProjectionShouldBeUntracked(InventoryDbContext context, InventoryItemReadModel? result, Guid id, Guid productId, int stock)
    {
        result.ShouldNotBeNull();
        result.Id.ShouldBe(id);
        result.ProductId.ShouldBe(productId);
        result.Stock.ShouldBe(stock);
        context.ChangeTracker.Entries().ShouldBeEmpty();
    }

    private static InventoryItem GivenNewItem(int stock) => new(Guid.CreateVersion7(), stock);

    private static async Task WhenSavingItem(InventoryPostgresDatabase database, InventoryItem item)
    {
        await using var context = database.CreateContext();
        await new InventoryItemDomainRepository(context, Substitute.For<IDomainEventDispatcher>()).SaveAsync(item);
    }

    private static async Task ThenFreshContextShouldReadItem(InventoryPostgresDatabase database, InventoryItem expected, int stock)
    {
        await using var context = database.CreateContext();
        var actual = await WhenQueryingProduct(context, expected.ProductId);
        actual.ShouldNotBeNull();
        actual.Id.ShouldBe(expected.Id);
        actual.Stock.ShouldBe(stock);
    }
}
