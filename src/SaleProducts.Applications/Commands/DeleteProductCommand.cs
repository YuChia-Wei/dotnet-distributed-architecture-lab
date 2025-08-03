using MediatR;

namespace SaleProducts.Applications.Commands;

public record DeleteProductCommand(Guid Id)
    : IRequest;