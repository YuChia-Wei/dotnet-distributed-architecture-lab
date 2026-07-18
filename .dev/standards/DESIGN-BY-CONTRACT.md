# Design By Contract Semantics

Rule ID: `CONTRACT-SEMANTICS-001`.

This standard preserves Design by Contract semantics without requiring the
unavailable historical uContract API or a shared base class.

## Contract Categories

- A precondition rejects invalid input or an invalid state before behavior runs.
- A postcondition verifies the observable state/result promised by a successful
  operation.
- An invariant must hold for every externally observable valid Aggregate or
  Entity state.

## Implementation Boundary

A target may implement these semantics with:

- standard guard clauses and exceptions;
- a target-owned assertion/contract helper;
- an explicitly selected third-party package;
- focused tests where runtime postcondition checks are intentionally omitted.

The selected mechanism is target-owned technology/architecture evidence. This
framework does not prescribe a `Contract` package, `Old(...)` API, exception
type, or production enable/disable switch.

## Required Behavior

1. Preconditions execute before state mutation.
2. A failed precondition leaves the modeled state unchanged.
3. Postconditions execute only after the operation has produced its candidate
   result/state.
4. Event-sourced postconditions may inspect the last pending event but must not
   mutate state outside `When`.
5. Invariants contain Domain truth and no persistence, broker, clock, or other
   Infrastructure I/O.
6. Tests assert both rejection and preservation of state/events.

## Illustrative Shape

```csharp
public void Rename(ProductName newName)
{
    ArgumentNullException.ThrowIfNull(newName); // precondition

    Apply(new ProductRenamed(Id, newName, DateTimeOffset.UtcNow));

    // Optional runtime postcondition helper; the semantic check is required,
    // but this helper name is not canonical framework API.
    Ensure(Name == newName, "The applied event must update the name.");
}
```

Targets that do not perform runtime postcondition checks must prove the same
promise with focused Domain tests. Historical uContract examples remain
provenance only.
