using MediatR;
using SaleProducts.Applications.Dtos;

namespace SaleProducts.Applications.Commands;

public record CreateProductSaleCommand(Guid OrderId, string ProductName, int Quantity) : IRequest<ProductSaleDto>;
