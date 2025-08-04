using SaleOrders.Domains;

namespace SaleOrders.Applications.Repositories;

/// <summary>
/// Represents a repository for managing Order domain entities.
/// </summary>
public interface IOrderDomainRepository
{
    /// <summary>
    /// Adds a new order to the repository.
    /// </summary>
    /// <param name="order">The order entity to add.</param>
    /// <param name="cancellationToken">A token to cancel the operation if needed.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task AddAsync(Order order, CancellationToken cancellationToken = default);

    /// <summary>
    /// Deletes an order from the repository by its identifier.
    /// </summary>
    /// <param name="id">The unique identifier of the order to delete.</param>
    /// <param name="cancellationToken">A token to cancel the operation if needed.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task DeleteAsync(Guid id, CancellationToken cancellationToken = default);

    /// <summary>
    /// Retrieves all orders from the repository.
    /// </summary>
    /// <param name="cancellationToken">A token to cancel the operation if needed.</param>
    /// <returns>A task containing a collection of all orders.</returns>
    Task<IEnumerable<Order>> GetAllAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Retrieves an order by its unique identifier.
    /// </summary>
    /// <param name="id">The unique identifier of the order to retrieve.</param>
    /// <param name="cancellationToken">A token to cancel the operation if needed.</param>
    /// <returns>A task containing the order if found, or null if not found.</returns>
    Task<Order?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);

    /// <summary>
    /// Updates an existing order in the repository.
    /// </summary>
    /// <param name="order">The order entity with updated information.</param>
    /// <param name="cancellationToken">A token to cancel the operation if needed.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task UpdateAsync(Order order, CancellationToken cancellationToken = default);
}