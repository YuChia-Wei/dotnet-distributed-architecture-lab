using InventoryControl.Domains;
using Microsoft.EntityFrameworkCore;

namespace EfCoreWolverine.Infrastructure;

/// <summary>The one scoped business context enrolled by Wolverine's Eager middleware.</summary>
public sealed class InventoryDbContext(DbContextOptions<InventoryDbContext> options) : DbContext(options)
{
    public const string Schema = "ef_inventory_sample";

    public DbSet<InventoryItem> InventoryItems => Set<InventoryItem>();

    /// <summary>Maps state with PostgreSQL xmin concurrency; the unused inherited Version and pending DomainEvents are excluded.</summary>
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var item = modelBuilder.Entity<InventoryItem>();
        item.ToTable("inventory_items", Schema,
            table => table.HasCheckConstraint("ck_stock_nonnegative", "stock >= 0"));
        item.HasKey(x => x.Id).HasName("pk_inventory_items");
        item.Property(x => x.Id).HasColumnName("id").ValueGeneratedNever();
        item.Property(x => x.ProductId).HasColumnName("product_id");
        item.HasIndex(x => x.ProductId).IsUnique().HasDatabaseName("ix_inventory_items_product_id");
        item.Property(x => x.Stock).HasColumnName("stock");

        item.Ignore(x => x.Version);
        item.Property<uint>("xmin").IsRowVersion();
        item.Ignore(x => x.DomainEvents);
    }
}
