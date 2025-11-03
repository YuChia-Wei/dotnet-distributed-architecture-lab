namespace Lab.BoundedContextContracts.Orders.DataTransferObjects;

public record OrderDetailsResponse
{
    public Guid OrderId { get; init; }
    public List<LineItemDto> LineItems { get; init; } = new();
}

public record LineItemDto
{
    public Guid ProductId { get; init; }
    public int Quantity { get; init; }
}
