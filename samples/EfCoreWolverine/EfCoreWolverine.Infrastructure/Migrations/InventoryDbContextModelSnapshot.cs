using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Metadata;

namespace EfCoreWolverine.Infrastructure.Migrations;

[DbContext(typeof(InventoryDbContext))]
public sealed class InventoryDbContextModelSnapshot : ModelSnapshot
{
    protected override void BuildModel(ModelBuilder modelBuilder)
    {
        modelBuilder.HasAnnotation("ProductVersion", "10.0.12")
            .HasAnnotation("Relational:MaxIdentifierLength", 63);
        NpgsqlModelBuilderExtensions.UseIdentityByDefaultColumns(modelBuilder);
        modelBuilder.Entity("InventoryControl.Domains.InventoryItem", item =>
        {
            item.Property<Guid>("Id").HasColumnType("uuid").HasColumnName("id");
            item.Property<Guid>("ProductId").HasColumnType("uuid").HasColumnName("product_id");
            item.Property<int>("Stock").HasColumnType("integer").HasColumnName("stock");
            item.Property<uint>("xmin").IsConcurrencyToken().ValueGeneratedOnAddOrUpdate().HasColumnType("xid");
            item.HasKey("Id").HasName("pk_inventory_items");
            item.HasIndex("ProductId").IsUnique().HasDatabaseName("ix_inventory_items_product_id");
            item.ToTable("inventory_items", InventoryDbContext.Schema,
                table => table.HasCheckConstraint("ck_stock_nonnegative", "stock >= 0"));
        });
    }
}
