using Procurement.Applications;
using Procurement.Domains;

namespace Procurement.Tests;

public sealed class ReceiptScenarios
{
    // R01 / AC02: accepted quantity ten can be received as six and four; acceptance alone has no receipt.
    [Fact, Trait("Scenario", "R01")]
    public void Two_partial_receipts_complete_the_order()
    {
        var order = GivenAcceptedOrder(10);
        var firstId = Guid.NewGuid();
        var secondId = Guid.NewGuid();
        var first = WhenReceiving(order, firstId, 6);
        ThenOrderIsPartiallyReceived(order, first, 6);
        var second = WhenReceiving(order, secondId, 4);
        ThenOrderIsCompletelyReceived(order, second, 10);
    }

    // R02 / AC02: overreceipt and nonpositive quantities preserve aggregate state.
    [Theory, Trait("Scenario", "R02")]
    [InlineData(5)]
    [InlineData(0)]
    [InlineData(-1)]
    public void Invalid_second_receipt_preserves_prior_six(int quantity)
    {
        var order = GivenAcceptedOrderWithSixReceived();
        var error = WhenReceivingInvalid(order, Guid.NewGuid(), quantity);
        ThenOnlyPriorReceiptRemains(order, error, quantity);
    }

    // R03 / AC02: a terminal replay returns the original receipt and changes no quantity/version.
    [Fact, Trait("Scenario", "R03")]
    public void Matching_terminal_replay_has_one_receipt()
    {
        var order = GivenAcceptedOrder(10);
        var receiptId = Guid.NewGuid();
        var original = WhenReceiving(order, receiptId, 10);
        var version = order.Version;
        var replay = WhenReceiving(order, receiptId, 10);
        ThenReplayHasNoSecondEffect(order, original, replay, version);
    }

    // R04 / AC02: a changed quantity under the same ReceiptId conflicts even after completion.
    [Fact, Trait("Scenario", "R04")]
    public void Changed_receipt_replay_conflicts()
    {
        var order = GivenAcceptedOrder(10);
        var receiptId = Guid.NewGuid();
        WhenReceiving(order, receiptId, 10);
        var error = WhenReceivingInvalid(order, receiptId, 9);
        ThenChangedReceiptConflictsWithoutMutation(order, error);
    }

    private static PurchaseOrder GivenAcceptedOrder(int quantity)
    {
        var identity = new PurchaseIdentity(Guid.NewGuid(), Guid.NewGuid(), "REAL-001", quantity,
            100m, "TWD", "direct");
        var order = PurchaseOrder.Create(Guid.NewGuid(), identity, DateTimeOffset.UtcNow);
        order.ApplySupplierOutcome(true, "vendor-42", DateTimeOffset.UtcNow);
        Assert.Empty(order.Receipts);
        return order;
    }
    private static PurchaseOrder GivenAcceptedOrderWithSixReceived()
    {
        var order = GivenAcceptedOrder(10);
        order.Receive(Guid.NewGuid(), 6, DateTimeOffset.UtcNow);
        return order;
    }
    private static GoodsReceipt WhenReceiving(PurchaseOrder order, Guid receiptId, int quantity) =>
        order.Receive(receiptId, quantity, DateTimeOffset.UtcNow);
    private static Exception? WhenReceivingInvalid(PurchaseOrder order, Guid receiptId, int quantity) =>
        Record.Exception(() => order.Receive(receiptId, quantity, DateTimeOffset.UtcNow));
    private static void ThenOrderIsPartiallyReceived(PurchaseOrder order, GoodsReceipt receipt, int expectedQuantity)
    {
        Assert.Equal(PurchaseOrderState.PartiallyReceived, order.State);
        Assert.Equal(expectedQuantity, order.ReceivedQuantity);
        Assert.Equal(expectedQuantity, receipt.Quantity);
        Assert.Single(order.Receipts);
    }
    private static void ThenOrderIsCompletelyReceived(PurchaseOrder order, GoodsReceipt receipt, int expectedQuantity)
    {
        Assert.Equal(PurchaseOrderState.Received, order.State);
        Assert.Equal(expectedQuantity, order.ReceivedQuantity);
        Assert.Equal(4, receipt.Quantity);
        Assert.Equal(2, order.Receipts.Count);
    }
    private static void ThenOnlyPriorReceiptRemains(PurchaseOrder order, Exception? error, int requested)
    {
        Assert.Equal(requested > 0 ? "over_receipt" : "invalid_receipt",
            Assert.IsType<ProcurementRuleException>(error).Code);
        Assert.Equal(6, order.ReceivedQuantity);
        Assert.Single(order.Receipts);
    }
    private static void ThenReplayHasNoSecondEffect(PurchaseOrder order, GoodsReceipt original, GoodsReceipt replay, int version)
    {
        Assert.Same(original, replay);
        Assert.Equal(version, order.Version);
        Assert.Equal(10, order.ReceivedQuantity);
        Assert.Single(order.Receipts);
    }
    private static void ThenChangedReceiptConflictsWithoutMutation(PurchaseOrder order, Exception? error)
    {
        Assert.Equal("receipt_identity_conflict", Assert.IsType<ProcurementRuleException>(error).Code);
        Assert.Equal(10, order.ReceivedQuantity);
        Assert.Single(order.Receipts);
    }
}
