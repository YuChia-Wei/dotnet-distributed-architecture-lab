using InventoryControl.Applications.Receipts;
using InventoryControl.Consumer.Messaging;
using Lab.BoundedContextContracts.Procurement.IntegrationEvents;
using NSubstitute;
using Shouldly;

namespace InventoryControl.Tests;

public sealed class GoodsReceivedHandlerTests
{
    [Fact]
    public async Task R03_given_a_procurement_receipt_when_consumed_then_exact_identity_is_applied_once()
    {
        var message = GivenGoodsReceived(4);
        var useCase = Substitute.For<IApplyGoodsReceiptUseCase>();
        ApplyGoodsReceiptInput? mapped = null;
        useCase.ExecuteAsync(Arg.Any<ApplyGoodsReceiptInput>(), Arg.Any<CancellationToken>())
            .Returns(call =>
            {
                mapped = call.Arg<ApplyGoodsReceiptInput>();
                return Task.FromResult(new ApplyGoodsReceiptOutput(message.ReceiptId, Guid.CreateVersion7(), 4, false));
            });

        await WhenHandling(message, useCase);

        await ThenMappedOnce(useCase, message, mapped);
    }

    [Fact]
    public async Task R04_given_a_receipt_identity_conflict_when_consumed_then_exception_reaches_the_failure_policy()
    {
        var message = GivenGoodsReceived(1);
        var useCase = Substitute.For<IApplyGoodsReceiptUseCase>();
        var conflict = new InventoryGoodsReceiptException("ReceiptIdentityConflict");
        useCase.ExecuteAsync(Arg.Any<ApplyGoodsReceiptInput>(), Arg.Any<CancellationToken>())
            .Returns(Task.FromException<ApplyGoodsReceiptOutput>(conflict));

        var actual = await Should.ThrowAsync<InventoryGoodsReceiptException>(
            () => WhenHandling(message, useCase));

        actual.ShouldBeSameAs(conflict);
    }

    private static GoodsReceived GivenGoodsReceived(int quantity)
        => new(Guid.CreateVersion7(), Guid.CreateVersion7(), Guid.CreateVersion7(), quantity, DateTimeOffset.UtcNow);

    private static Task WhenHandling(GoodsReceived message, IApplyGoodsReceiptUseCase useCase)
        => new GoodsReceivedHandler().HandleAsync(message, useCase, CancellationToken.None);

    private static async Task ThenMappedOnce(
        IApplyGoodsReceiptUseCase useCase, GoodsReceived message, ApplyGoodsReceiptInput? mapped)
    {
        mapped.ShouldBe(new ApplyGoodsReceiptInput(
            message.ReceiptId, message.PurchaseOrderId, message.ProductId, message.Quantity));
        await useCase.Received(1).ExecuteAsync(Arg.Any<ApplyGoodsReceiptInput>(), Arg.Any<CancellationToken>());
    }
}
