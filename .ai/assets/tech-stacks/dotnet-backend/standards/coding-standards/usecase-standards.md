# Use Case Coding Standards (.NET)

This document defines coding standards for synchronous Command/Query Use Cases,
Input/Output, Handlers, transactions, and the event lifecycle. The authoritative
role relationship is defined in
[USECASE-COMMAND-HANDLER-RELATIONSHIP.MD](../USECASE-COMMAND-HANDLER-RELATIONSHIP.MD).

## Core Model

```text
Controller / Handler (inbound adapter)
  -> I<Operation>UseCase (inbound port)
  -> <Operation>UseCase (orchestration)
  -> Domain / outbound ports
```

- A Use Case and a Handler are distinct objects.
- By default, a synchronous API Controller directly injects the Use Case interface.
- A Handler exists only for a real dispatch or message entry point.
- Wolverine is a conditional adapter technology, not a portable Use Case dependency.

## MUST Rules

### 1. Interface, Implementation, and Operation Naming

```csharp
public interface ICreateProductUseCase
{
    Task<CreateProductOutput> ExecuteAsync(
        CreateProductInput input,
        CancellationToken cancellationToken);
}

public sealed class CreateProductUseCase : ICreateProductUseCase
{
    public Task<CreateProductOutput> ExecuteAsync(
        CreateProductInput input,
        CancellationToken cancellationToken)
    {
        // Orchestrate Domain behavior and outbound ports.
    }
}
```

- Interfaces use `I<Operation>UseCase`.
- Implementations use `<Operation>UseCase`.
- The operation name is always `ExecuteAsync`.
- An asynchronous operation MUST declare a non-optional `CancellationToken`.
- A Use Case MUST NOT also expose a `Handle` entry point.

### 2. Input MUST Be Separate from the Delivery Contract

By default, create a dedicated, transport-neutral `*Input` for a Use Case:

```csharp
public sealed record CreateProductInput(
    string ProductId,
    string Name,
    string UserId);
```

Two exceptions are allowed:

- Do not create an input when there is no input other than cancellation.
- A single scalar built-in/BCL value may be accepted directly.

The scalar exception is limited to `string`, numeric types, `bool`, `Guid`, and
date/time types. Collections, tuples, custom records/classes, or multiple values
MUST use a dedicated input.

A Use Case MUST NOT accept:

- ASP.NET Request DTO
- Wolverine/MediatR Command or Query
- broker contract
- package marker interface

### 3. Output MUST Be Separate from Transport

```csharp
public sealed record CreateProductOutput(ProductId ProductId);
```

A Use Case returns only the transport-neutral object produced by the completed
operation. Return `Task` when there is no object. It MUST NOT return
`IActionResult`, a broker acknowledgement, retry/dead-letter instructions, or a
framework envelope.

### 4. Separate Command and Query Responsibilities

- A Command Use Case changes state and preserves invariants through Aggregate behavior.
- A Query Use Case reads only a read model and does not change Domain state.
- Create a Command/message contract only when a dispatch entry point exists.
- A Command/message Handler maps the delivery contract to Use Case input.
- Queries use a query Use Case by default. Only an explicitly approved read-only
  endpoint may directly use an `IQueryRepository`-derived port or query service.

### 5. Dependency Injection

A Use Case uses constructor injection and depends only on Domain types and
Application outbound ports:

```csharp
public sealed class CreateProductUseCase : ICreateProductUseCase
{
    private readonly IAggregateRepository<Product, ProductId> repository;
    private readonly IApplicationEventPublisher eventPublisher;

    public CreateProductUseCase(
        IAggregateRepository<Product, ProductId> repository,
        IApplicationEventPublisher eventPublisher)
    {
        this.repository = repository;
        this.eventPublisher = eventPublisher;
    }
}
```

Forbidden:

- `IServiceProvider` / Service Locator
- DI registration attribute
- framework package dependency in portable Use Case
- direct Wolverine `IMessageBus`
- another Use Case dependency

Register explicitly with `IServiceCollection` in the composition root:

```csharp
services.AddScoped<ICreateProductUseCase, CreateProductUseCase>();
```

MUST NOT register `ICreateProductUseCase` to `CreateProductHandler`.

### 6. A Handler MUST Be a Thin Inbound Adapter

Create a Handler only for a real dispatch/message entry point:

```csharp
public sealed class CreateProductCommandHandler
{
    private readonly ICreateProductUseCase useCase;

    public CreateProductCommandHandler(ICreateProductUseCase useCase)
    {
        this.useCase = useCase;
    }

    public Task<CreateProductOutput> HandleAsync(
        CreateProductCommand command,
        CancellationToken cancellationToken)
    {
        var input = new CreateProductInput(
            command.ProductId,
            command.Name,
            command.UserId);

        return this.useCase.ExecuteAsync(input, cancellationToken);
    }
}
```

A Handler MUST NOT:

- load or save an Aggregate;
- depend on a Repository or Domain Service;
- commit a transaction;
- publish a business event or Command;
- inject or orchestrate multiple Use Cases.

A package-neutral convention Handler may reside in Application. A
framework/transport-specific Handler belongs at the inbound adapter or composition
boundary.

### 7. Strong Consistency MUST Be Explicit

One command changes one Aggregate by default. Events and eventual consistency are
the default for coordination between Aggregates. A Use Case may inject
`IUnitOfWork` for multiple Aggregates only as an exceptional same-bounded-context
decision when all of these conditions hold:

1. The business names an all-or-nothing invariant involving the Aggregates.
2. Any eventually consistent intermediate state would be unacceptable and cannot
   be safely compensated.
3. The design rechecks that the Aggregate boundaries are correct instead of using
   a transaction to hide a misplaced invariant.
4. The decision documents the invariant, the involved Aggregates, and why eventual
   consistency or compensation is insufficient.

The following Reservation + Capacity example represents such an exceptional
business rule; it is not a general Use Case template:

```csharp
public sealed class CompleteReservationUseCase
{
    private readonly IUnitOfWork unitOfWork;

    public async Task ExecuteAsync(CancellationToken cancellationToken)
    {
        // Exceptional case: Reservation and Capacity are in the same bounded
        // context and the named invariant requires both changes to succeed or
        // neither to succeed. An intermediate overbooked state is unacceptable
        // and cannot be safely compensated. Do not copy this as a general template.
        // Load Reservation and Capacity, invoke Domain behavior, and save through ports.
        await this.unitOfWork.CommitAsync(cancellationToken);
    }
}
```

- MUST NOT select a multi-Aggregate transaction because of shared storage, ORM or
  framework capabilities, fewer I/O round trips, implementation convenience, or a
  general future need.
- MUST NOT make `IUnitOfWork` a default Use Case dependency.
- MUST NOT span bounded contexts with one transaction; cross-bounded-context
  coordination uses integration events and eventual consistency.
- A Repository participating in a Unit of Work MUST NOT commit independently.
- A Handler MUST NOT introduce a transaction or commit after the Use Case.
- Pending Domain Events may be acknowledged or cleared only after a successful commit.

### 8. Event Publication Uses an Outbound Port

A Domain object produces Domain Events; the Use Case coordinates persistence,
outbox, and the publication lifecycle.

```csharp
public interface IApplicationEventPublisher
{
    Task PublishAsync(
        object applicationEvent,
        CancellationToken cancellationToken);
}
```

The concrete port SHOULD use the target domain language instead of a generic bus
abstraction. Infrastructure may implement the port with Wolverine/outbox. A Use
Case MUST NOT inject `IMessageBus` directly or publish Commands through the publisher.

## Test Rules

- A Use Case unit test directly creates the concrete `*UseCase`.
- Mock outbound ports such as Aggregate Repository, Query Repository, gateway,
  clock, and publisher.
- Verify `ExecuteAsync` output, Domain behavior, persistence, and event lifecycle.
- A Handler test verifies only mapping, one Use Case invocation, and delivery
  failure mapping.
- A Handler test MUST NOT replace a Use Case business-flow test.

## Checklist

### Use Case

- [ ] Interface and concrete class names use `*UseCase`.
- [ ] The operation is `ExecuteAsync`.
- [ ] `CancellationToken` is not optional.
- [ ] Input/Output are separate from HTTP, MQ, and Wolverine/MediatR.
- [ ] Dependencies are limited to Domain types and outbound ports.
- [ ] There is no dependency on `IServiceProvider`, `IMessageBus`, or another Use Case.
- [ ] The transaction and event lifecycle reside in the Use Case.
- [ ] One command changes one Aggregate by default; other Aggregate effects use events.
- [ ] `IUnitOfWork` is absent unless a documented, named all-or-nothing invariant
      satisfies every exceptional strong-consistency criterion above.
- [ ] An exceptional transaction records the involved Aggregates, boundary recheck,
      and why eventual consistency or compensation is unacceptable.
- [ ] No transaction spans bounded contexts.

### Handler

- [ ] Exists only for a real dispatch/message entry point.
- [ ] Maps delivery input to Use Case input.
- [ ] Invokes exactly one Use Case.
- [ ] Does not directly operate a Repository, Aggregate, transaction, or event publication.
- [ ] Framework/transport coupling stays at the adapter/composition boundary.

## Related Documents

- [Aggregate Standards](aggregate-standards.md)
- [Controller Standards](controller-standards.md)
- [Repository Standards](repository-standards.md)
- [Test Standards](test-standards.md)
- [Conditional target project structure profile](../project-structure.md) (apply physical layout only with target evidence or explicit adoption)
