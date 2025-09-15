using System;
using System.Linq;
using SaleOrders.Domains;
using Xunit;

namespace SaleOrders.Domains.Tests;

public class OrderTests
{
    [Fact]
    public void Cancel_SetsStatus_To_Cancelled_And_Raises_DomainEvent()
    {
        var order = new Order(DateTime.UtcNow, 100m, Guid.NewGuid(), "Test Product", 1);

        order.Cancel();

        Assert.Equal(OrderStatus.Cancelled, order.Status);
        Assert.Contains(order.DomainEvents, e => e.GetType().Name == "OrderCancelledDomainEvent");
    }
}

