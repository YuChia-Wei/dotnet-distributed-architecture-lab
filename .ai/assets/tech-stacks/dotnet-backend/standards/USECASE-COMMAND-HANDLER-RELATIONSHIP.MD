# Use Case, Command, Query, and Handler Relationships

This document defines the standard responsibility boundaries among `Use Case`,
`Input`, `Command`, `Query`, `Handler`, `Controller`, and related ports in this
repository under DDD, Clean Architecture, CQRS, and Hexagonal Architecture.

## Core Conclusions

- A `Use Case interface` is an Application inbound port.
- A concrete `*UseCase` class implements application-flow orchestration.
- A `Controller` is an HTTP inbound adapter and calls only a Use Case interface by default.
- A `Command` / message contract is dispatch or transport input, not Use Case input.
- A `Handler` exists only when there is an actual dispatch, message, consumer, or scheduled entry. It maps input and invokes one Use Case.
- Use Cases and Handlers are distinct objects. A Handler must not be the default Use Case implementation.
- A Use Case depends on outbound ports. Wolverine, MediatR, HTTP, MQ, and persistence packages must not leak into portable Use Case contracts.
- This workflow neither defines nor expands `Application Service`. If an existing product uses that term, a separate explicit decision must define its purpose.

## Standard Call Chains

### Synchronous Command API

```text
HTTP Request
  -> Controller
  -> I<CreateOperation>UseCase
  -> <CreateOperation>UseCase
  -> Aggregate / Domain Service / outbound ports
  -> Use Case Output
  -> HTTP Response
```

A Controller does not execute an ordinary synchronous API Use Case through
`IMessageBus`, a mediator, or a Command Handler.

### Synchronous Query API

Default flow:

```text
HTTP Request
  -> Controller
  -> I<GetOperation>UseCase
  -> <GetOperation>UseCase
  -> I<Feature>QueryRepository / Query Service
  -> Use Case Output
  -> HTTP Response
```

Only an explicitly designated pure-query endpoint may directly inject a read-only
`IQueryRepository`-derived port or query service. This exception is permitted but
not recommended. A query Use Case remains mandatory unless the exception is
explicitly designated. Direct query-handler dispatch is not part of this exception.

### Dispatch or Message Entry

```text
Command / Message / Scheduled Trigger
  -> Handler (inbound adapter)
  -> I<CreateOperation>UseCase
  -> <CreateOperation>UseCase
```

A Handler is responsible only for delivery-contract validation, input mapping,
invoking one Use Case, and mapping failures to the retry/dead-letter semantics of
that delivery mechanism. It must not load an Aggregate, operate a Repository,
commit a transaction, or publish business events itself.

### Cross-BC Flow

```text
BC A Use Case
  -> outbound event publisher port
  -> Infrastructure messaging/outbox adapter
  -> MQ
  -> BC B Consumer / Handler
  -> BC B Use Case
```

Cross-BC communication must use MQ. A Use Case does not depend directly on
Wolverine `IMessageBus`; Infrastructure adapts the project-owned event publisher
port to the selected broker/framework.

## Use Case Contract

### Naming

- interface: `ICreateProductUseCase`
- implementation: `CreateProductUseCase`
- operation: `ExecuteAsync`
- input: `CreateProductInput`
- output: `CreateProductOutput`

### Signature

Every asynchronous Use Case must declare a non-optional `CancellationToken`.

```csharp
public interface ICreateProductUseCase
{
    Task<CreateProductOutput> ExecuteAsync(
        CreateProductInput input,
        CancellationToken cancellationToken);
}
```

A dedicated, transport-neutral `*Input` is the default. Two exceptions are allowed:

1. Input may be omitted when there is no input other than cancellation.
2. A single scalar built-in/BCL value may be accepted directly.

Standard scalars include `string`, numeric types, `bool`, `Guid`, and date/time
types. A collection, tuple, custom record/class, or multiple values require a
dedicated input.

```csharp
Task ExecuteAsync(CancellationToken cancellationToken);

Task<FindProductOutput> ExecuteAsync(
    Guid productId,
    CancellationToken cancellationToken);
```

An HTTP Request, broker message, Wolverine Command, or another delivery contract
must not be used directly as Use Case input.

### Output

A Use Case returns only transport-neutral output produced by the completed
operation. Return `Task` when there is no output object; do not create an empty
output merely for formatting consistency. A Use Case does not return:

- `IActionResult` / `IResult`
- broker acknowledgement
- Wolverine/MediatR envelope
- retry/dead-letter instruction

## Responsibilities and Dependencies

### Use Case Responsibilities

- application-level validation and authorization orchestration;
- loading an Aggregate or read-side data;
- invoking Aggregate behavior / a Domain Service;
- using outbound ports such as an Aggregate Repository, Query Repository, or gateway;
- using `IUnitOfWork` in an explicit strong-consistency scenario;
- coordinating outbox and pending Domain Event acknowledgement;
- publishing application/integration events through a project-owned event publisher port;
- assembling transport-neutral output.

A Domain Event should be produced by a Domain object. The Use Case coordinates
the persistence, outbox, and dispatch lifecycle.

### Controller Responsibilities

- HTTP model binding and transport validation;
- mapping an HTTP Request to Use Case input;
- invoking a Use Case interface;
- mapping the Use Case outcome to an HTTP response.

A Controller must not inject a concrete Handler, `IMessageBus`, mediator/dispatcher,
write repository, Aggregate, or Domain Service. The pure-query exception permits
only an explicitly approved read-only Query Repository / Query Service.

### Handler Responsibilities

- receiving actual dispatch/message input;
- delivery-level validation and mapping;
- invoking one Use Case interface;
- delivery-specific failure mapping.

A Handler must not:

- become a Use Case implementation;
- operate a Repository, Aggregate, or Domain Service directly;
- create a transaction itself or commit after the Use Case;
- use a bus to publish another Command;
- inject or chain multiple Use Cases.

When multiple steps are needed to complete one business goal, create a higher-level
Use Case. Do not have a Controller or Handler orchestrate multiple Use Cases.

## Handler Placement

- A package-neutral convention Handler may reside in Application.
- A Wolverine/MediatR-specific Handler resides at an inbound adapter or composition boundary.
- An MQ Consumer / Integration Event Handler resides in a Consumer/Presentation adapter.
- A Domain Event Handler / Reactor resides at an explicit Application reaction boundary according to event and consistency rules, but must not be combined with a synchronous API Use Case role.

Handler placement is determined by delivery/framework coupling, not by the
`Handler` suffix alone.

## DI Rules

Synchronous API:

```csharp
services.AddScoped<ICreateProductUseCase, CreateProductUseCase>();
```

Register a Handler only for an actual dispatch entry. Do not recombine the roles
through `ICreateProductUseCase -> CreateProductHandler`.

Use Cases, Handlers, and adapters use constructor injection and are registered
explicitly through `IServiceCollection` at the composition root. Do not use a
Service Locator, DI attributes, or assembly-scanning magic.

## Transaction and Event Rules

- Eventual consistency is the default across Aggregates / BCs.
- A Use Case injects `IUnitOfWork` only for an explicit all-or-nothing business requirement.
- A Handler must not introduce hidden strong consistency.
- A Repository participating in a Unit of Work must not commit independently.
- Pending Domain Events must not be acknowledged/cleared before a successful commit.
- A Use Case uses a project-owned event publisher port; Infrastructure may implement that port with the Wolverine outbox.
- A Use Case must not publish a Command through any bus or publisher.

## Testing and Analyzer Boundaries

- A Use Case unit test tests the concrete `*UseCase` directly and mocks outbound ports.
- A Handler test verifies only mapping, one Use Case invocation, and delivery-failure mapping.
- A Controller test mocks the Use Case interface, not a Handler or Repository.
- An analyzer should report a deterministic boundary violation as an error.
- A naming-only migration advisory or one without reliable target evidence remains a warning.
- An explicit pure-query exception must have target-repository evidence that can be evaluated; otherwise, the analyzer still applies the default Use Case boundary.

## Migration Boundary

This standard does not publish a general migration recipe. Before scheduling a
migration for an existing `ICreateProductUseCase -> CreateProductHandler`,
Controller-to-Handler, or combined `Execute`/`Handle` implementation during an
actual product refactor, first inventory callers, DI registrations, actual dispatch
entries, transactions, and event ownership.

## Relationship to Specs

In `.dev/specs/`, Use Case is the primary name for production behavior. Command,
Query, HTTP Request, and message contracts are delivery/input models. A Handler is
an adapter implementation detail and should not become the primary business-behavior
name in a spec.
