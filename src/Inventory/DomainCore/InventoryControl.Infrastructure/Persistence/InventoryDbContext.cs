using InventoryControl.Domains;
using Microsoft.EntityFrameworkCore;

namespace InventoryControl.Infrastructure.Persistence;

/// <summary>Maps Inventory persistence to the existing PostgreSQL schema owned by the SQL migrations.</summary>
public sealed class InventoryDbContext(DbContextOptions<InventoryDbContext> options) : DbContext(options)
{
    public DbSet<InventoryItem> InventoryItems => this.Set<InventoryItem>();

    internal DbSet<InventoryReservationOperation> ReservationOperations => this.Set<InventoryReservationOperation>();

    internal DbSet<InventoryOutboxRecord> OutboxMessages => this.Set<InventoryOutboxRecord>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var inventory = modelBuilder.Entity<InventoryItem>();
        inventory.ToTable("inventoryitems");
        inventory.HasKey(item => item.Id);
        inventory.Property(item => item.Id).ValueGeneratedNever();
        inventory.HasIndex(item => item.ProductId).IsUnique().HasDatabaseName("ux_inventoryitems_productid");
        inventory.Ignore(item => item.DomainEvents);
        inventory.Ignore(item => item.Version);

        var operations = modelBuilder.Entity<InventoryReservationOperation>();
        operations.ToTable("inventoryreservationoperations");
        operations.HasKey(operation => operation.OperationId);
        operations.Property(operation => operation.OperationId).ValueGeneratedNever();
        operations.HasIndex(operation => operation.ProductId).HasDatabaseName("ix_inventoryreservationoperations_productid");

        var outbox = modelBuilder.Entity<InventoryOutboxRecord>();
        outbox.ToTable("inventoryintegrationoutbox");
        outbox.HasKey(message => message.Id);
        outbox.Property(message => message.Id).ValueGeneratedNever();
        outbox.Property(message => message.PartitionKey).HasMaxLength(64);
        outbox.Property(message => message.MessageType).HasMaxLength(255);
        outbox.Property(message => message.Data).HasColumnType("jsonb");
        outbox.Property(message => message.CreatedOn).HasDefaultValueSql("CURRENT_TIMESTAMP");
        outbox.Property(message => message.NextAttemptAt).HasDefaultValueSql("CURRENT_TIMESTAMP");
        outbox.HasIndex(message => new { message.NextAttemptAt, message.CreatedOn, message.Id })
            .HasDatabaseName("ix_inventoryintegrationoutbox_claim")
            .HasFilter("publishedat IS NULL AND parkedat IS NULL");

        foreach (var entity in modelBuilder.Model.GetEntityTypes())
        {
            foreach (var property in entity.GetProperties())
            {
                property.SetColumnName(property.Name.ToLowerInvariant());
            }
        }
    }

    /// <summary>Removes snapshots invalidated by a set-based stock update from this processing scope.</summary>
    internal void DetachInventoryItem(Guid id)
    {
        foreach (var entry in this.ChangeTracker.Entries<InventoryItem>().Where(entry => entry.Entity.Id == id).ToArray())
        {
            entry.State = EntityState.Detached;
        }
    }
}
