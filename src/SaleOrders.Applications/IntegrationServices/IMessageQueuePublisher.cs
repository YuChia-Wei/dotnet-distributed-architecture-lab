namespace SaleOrders.Applications.IntegrationServices;

/// <summary>
/// Defines a contract for publishing messages to a message queue system.
/// </summary>
/// <remarks>
/// 先不考慮共用介面，因此 sale order / sale product 兩個 BC 中都有對應的介面
/// </remarks>
public interface IMessageQueuePublisher
{
    /// <summary>
    /// Publishes a message to the message queue asynchronously.
    /// </summary>
    /// <typeparam name="T">The type of the message to be published. Must be a reference type.</typeparam>
    /// <param name="message">The message to publish.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task PublishAsync<T>(T message) where T : class;
}