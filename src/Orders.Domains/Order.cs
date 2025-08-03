using Shared.Kernel.Abstractions;

namespace Orders.Domains;

public class Order : IAggregateRoot
{
    public Guid Id { get; private set; }
    public DateTime OrderDate { get; private set; }
    public decimal TotalAmount { get; private set; }

    public object[] GetKeys() => new object[] { Id };
}
