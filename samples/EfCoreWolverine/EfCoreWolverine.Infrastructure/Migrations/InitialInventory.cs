using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Migrations;

namespace EfCoreWolverine.Infrastructure.Migrations;

/// <summary>Business schema only; Wolverine owns and provisions its own message-store schema.</summary>
[DbContext(typeof(InventoryDbContext))]
[Migration("202609170001_InitialInventory")]
public sealed class InitialInventory : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.EnsureSchema(InventoryDbContext.Schema);
        migrationBuilder.CreateTable("inventory_items", schema: InventoryDbContext.Schema,
            columns: table => new
            {
                id = table.Column<Guid>("uuid", nullable: false),
                product_id = table.Column<Guid>("uuid", nullable: false),
                stock = table.Column<int>("integer", nullable: false)
            }, constraints: table =>
            {
                table.PrimaryKey("pk_inventory_items", x => x.id);
                table.CheckConstraint("ck_stock_nonnegative", "stock >= 0");
            });
        migrationBuilder.CreateIndex("ix_inventory_items_product_id", "inventory_items", "product_id",
            schema: InventoryDbContext.Schema, unique: true);
    }

    protected override void Down(MigrationBuilder migrationBuilder)
        => migrationBuilder.DropTable("inventory_items", schema: InventoryDbContext.Schema);
}
