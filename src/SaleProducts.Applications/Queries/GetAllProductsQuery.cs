using MediatR;
using SaleProducts.Applications.Dtos;

namespace SaleProducts.Applications.Queries;

public record GetAllProductsQuery()
    : IRequest<IEnumerable<ProductDto>>;