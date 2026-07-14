# Reactor Coding Standards (.NET)

This document defines coding standards for Reactors and event-driven handlers, including interface types, event conversion, boundary responsibilities, and common errors.

---

## 📌 Overview

Use a Reactor to:

- handle event-driven flows across Aggregates;
- update a read model, archive, or projection;
- trigger follow-up collaboration across Bounded Contexts.

A Reactor must not be treated as a general command handler or directly carry Controller concerns.

---

## 🔴 Mandatory Rules (MUST FOLLOW)

### 1. Reactor Interfaces Must Use `DomainEventData`

Every Reactor interface must inherit from:

```csharp
IReactor<DomainEventData>
```

```csharp
// ✅ Correct
public interface INotifyOrderProjectionReactor : IReactor<DomainEventData>
{
}

// ❌ Incorrect: uses DomainEvent directly
public interface INotifyOrderProjectionReactor : IReactor<DomainEvent>
{
}

// ❌ Incorrect: generic type is omitted
public interface INotifyOrderProjectionReactor : IReactor
{
}
```

Rationale:

- The Message bus/event pipeline carries `DomainEventData`.
- The interface layer first aligns with the transport shape; the implementation converts it back to a domain event.
- This prevents the Reactor interface from diverging from the event bus type.

### 2. A Handler Receives `DomainEventData` and Then Converts It to a Domain Event

```csharp
public sealed class NotifyOrderProjectionReactor : INotifyOrderProjectionReactor
{
    public Task Handle(DomainEventData eventData)
    {
        var domainEvent = DomainEventMapper.ToDomainEvent(eventData);

        if (domainEvent is OrderPlaced placed)
        {
            // handle
        }

        return Task.CompletedTask;
    }
}
```

Do not bind a Reactor interface directly to a single domain event class.

### 3. A Reactor Focuses on Event-Driven Collaboration, Not HTTP/Controller Concerns

A Reactor should handle only:

- event-to-action flow
- projection / archive update
- cross-aggregate coordination
- outbound integration follow-up

A Reactor should not:

- directly handle an HTTP request/response;
- directly become Controller action logic;
- mix a Use Case command flow with an event flow.

### 4. A Reactor Must Account for Redelivery and Idempotency

At minimum, account for:

- at-least-once delivery
- duplicate delivery
- replay/rebuild scenarios.

External I/O, read-model updates, and notifications should be protected against duplicate processing.

---

## 🎯 Recommended Responsibility Boundary

```text
Domain Event / Integration Event
  -> Reactor
  -> Archive / Projection / Query Model / Follow-up Application Action
```

A Reactor is an event-driven application collaborator, not part of the Aggregate itself.

---

## ⚠️ Common Errors

### Error 1: A Reactor Declares `IReactor<DomainEvent>` Directly

This makes the interface diverge from the actual bus payload.

### Error 2: A Reactor Contains Controller/API Concerns

A Reactor is an event handler, not a transport adapter.

### Error 3: A Reactor Does Not Account for Idempotency

If a Reactor updates a read model, calls an external system, or sends a notification, it cannot assume that an event arrives only once.

---

## 🔍 Checklist

- [ ] The Reactor interface uses `IReactor<DomainEventData>`.
- [ ] `Handle(...)` receives `DomainEventData`.
- [ ] It converts to a domain event before performing type checks.
- [ ] It does not mix in Controller/HTTP concerns.
- [ ] It accounts for duplicate-delivery/replay risks.

---

## Related Documents

- [usecase-standards.md](usecase-standards.md)
- [archive-standards.md](archive-standards.md)
- [../../operations/runbooks/README.MD](../../operations/runbooks/README.MD)
- [../../ARCHITECTURE.md](../../ARCHITECTURE.md)
