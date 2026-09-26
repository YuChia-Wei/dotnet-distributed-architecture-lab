using InventoryControl.Applications.Outbox;
using InventoryControl.Applications.Receipts;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using NSubstitute;
using Shouldly;

namespace InventoryControl.Tests;

public sealed class ApplyGoodsReceiptUseCaseTests
{
    [Theory]
    [InlineData(0, 1)]
    [InlineData(1, 0)]
    [InlineData(2, 0)]
    [InlineData(3, 0)]
    public async Task given_invalid_receipt_identity_or_quantity_when_applied_then_store_is_not_called(int invalidField, int quantity)
    {
        // Given R07: invalid requests must not create a receipt claim.
        var store = Substitute.For<IInventoryGoodsReceiptStore>();
        var ids = new[] { Guid.CreateVersion7(), Guid.CreateVersion7(), Guid.CreateVersion7() };
        if (invalidField < 3) ids[invalidField] = Guid.Empty;
        var input = new ApplyGoodsReceiptInput(ids[0], ids[1], ids[2], quantity);

        // When
        var error = await Should.ThrowAsync<InventoryGoodsReceiptException>(
            () => new ApplyGoodsReceiptUseCase(store).ExecuteAsync(input, CancellationToken.None));

        // Then
        error.Code.ShouldBe(invalidField < 3 ? "ReceiptIdentityRequired" : "ReceiptQuantityMustBePositive");
        await store.DidNotReceiveWithAnyArgs().ApplyAndStageAsync(default!, default!, TestContext.Current.CancellationToken);
    }

    [Fact]
    public async Task given_a_valid_physical_receipt_when_applied_then_inventory_event_uses_the_receipt_identity()
    {
        // Given R03: the receipt ID is the stable source event and Inventory outbox ID.
        var input = new ApplyGoodsReceiptInput(Guid.CreateVersion7(), Guid.CreateVersion7(), Guid.CreateVersion7(), 4);
        var output = new ApplyGoodsReceiptOutput(input.ReceiptId, Guid.CreateVersion7(), 9, false);
        var store = Substitute.For<IInventoryGoodsReceiptStore>();
        InventoryOutboxMessage? staged = null;
        store.ApplyAndStageAsync(input, Arg.Any<Func<ApplyGoodsReceiptOutput, InventoryOutboxMessage>>(), Arg.Any<CancellationToken>())
            .Returns(call =>
            {
                staged = call.Arg<Func<ApplyGoodsReceiptOutput, InventoryOutboxMessage>>()(output);
                return Task.FromResult(output);
            });

        // When
        var actual = await new ApplyGoodsReceiptUseCase(store).ExecuteAsync(input, CancellationToken.None);

        // Then
        actual.ShouldBe(output);
        staged.ShouldNotBeNull();
        staged.Delivery.MessageId.ShouldBe(input.ReceiptId);
        staged.Delivery.PartitionKey.ShouldBe(input.ProductId.ToString("N"));
        var integrationEvent = staged.IntegrationEvent.ShouldBeOfType<ProductStockIncreasedIntegrationEvent>();
        integrationEvent.InventoryItemId.ShouldBe(output.InventoryItemId);
        integrationEvent.IncreasedQuantity.ShouldBe(input.Quantity);
        integrationEvent.CurrentStock.ShouldBe(output.ResultingStock);
    }
}
