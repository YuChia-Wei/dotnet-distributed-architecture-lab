
using SaleOrders.Applications.IntegrationServices;
using Wolverine;

namespace SaleOrders.Infrastructure.IntegrationServices;

/// <summary>
/// Message queue publisher for sale orders.
/// </summary>
/// <param name="messageBus"></param>
public class MessageQueuePublisher(IMessageBus messageBus) : IMessageQueuePublisher
{
    /// <summary>
    /// Publishes a message to the message queue asynchronously.
    /// </summary>
    /// <typeparam name="T">The type of the message to be published. Must be a reference type.</typeparam>
    /// <param name="message">The message to publish.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    public async Task PublishAsync<T>(T message) where T : class
    {
        await messageBus.PublishAsync(message);
    }
}
