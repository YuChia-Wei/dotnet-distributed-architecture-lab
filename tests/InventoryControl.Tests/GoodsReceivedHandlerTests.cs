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
        // Given: delivery metadata comes from the Procurement-owned v1 fact.
        var message = new GoodsReceived(
            Guid.CreateVersion7(), Guid.CreateVersion7(), Guid.CreateVersion7(), 4, DateTimeOffset.UtcNow);
        var useCase = Substitute.For<IApplyGoodsReceiptUseCase>();
        ApplyGoodsReceiptInput? mapped = null;
        useCase.ExecuteAsync(Arg.Any<ApplyGoodsReceiptInput>(), Arg.Any<CancellationToken>())
            .Returns(call =>
            {
                mapped = call.Arg<ApplyGoodsReceiptInput>();
                return Task.FromResult(new ApplyGoodsReceiptOutput(message.ReceiptId, Guid.CreateVersion7(), 4, false));
            });

        // When
        await new GoodsReceivedHandler().HandleAsync(message, useCase, CancellationToken.None);

        // Then: the handler delegates business work and preserves the receipt identity.
        mapped.ShouldBe(new ApplyGoodsReceiptInput(
            message.ReceiptId, message.PurchaseOrderId, message.ProductId, message.Quantity));
        await useCase.Received(1).ExecuteAsync(Arg.Any<ApplyGoodsReceiptInput>(), Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task R04_given_a_receipt_identity_conflict_when_consumed_then_exception_reaches_the_failure_policy()
    {
        // Given
        var message = new GoodsReceived(
            Guid.CreateVersion7(), Guid.CreateVersion7(), Guid.CreateVersion7(), 1, DateTimeOffset.UtcNow);
        var useCase = Substitute.For<IApplyGoodsReceiptUseCase>();
        var conflict = new InventoryGoodsReceiptException("ReceiptIdentityConflict");
        useCase.ExecuteAsync(Arg.Any<ApplyGoodsReceiptInput>(), Arg.Any<CancellationToken>())
            .Returns(Task.FromException<ApplyGoodsReceiptOutput>(conflict));

        // When
        var actual = await Should.ThrowAsync<InventoryGoodsReceiptException>(
            () => new GoodsReceivedHandler().HandleAsync(message, useCase, CancellationToken.None));

        // Then
        actual.ShouldBeSameAs(conflict);
    }
}
