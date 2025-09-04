namespace SaleProducts.Applications.Dtos;

public class ProductSaleDto
{
    public Guid OrderId { get; set; }
    public int Quantity { get; set; }
    public DateTime SaleDate { get; set; }
}
