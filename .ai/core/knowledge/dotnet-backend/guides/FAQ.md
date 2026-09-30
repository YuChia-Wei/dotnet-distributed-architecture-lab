# .NET backend FAQ

## Applicability

This optional .NET reference applies only to the target-selected architecture,
providers and adopted test rules. Examples do not install packages, select an ORM,
broker or Event Sourcing, create fixed project paths, or prove execution. Preserve
per-domain persistence decisions and the target-selected GWT contract; BDDfy and
mocking packages remain separately selected.

This optional guide explains profile examples. Apply only the target's adopted
rules and selected technologies; the package does not introduce universal choices.

## Does CQRS require Event Sourcing?

No. CQRS separates state-changing behavior from reads. Event Sourcing can provide
an event history and replay when the domain accepts the operational, versioning
and consistency costs. EF Core, direct SQL, event stores and mixed per-domain
persistence remain valid target choices.

## What differs between a use case and a handler?

A use case owns the application behavior; a handler maps a real dispatch/message
entry and invokes it. A reactor handles an accepted integration effect. Read the
[terminology contract](../standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD) under
its adopted applicability before choosing the target's names and responsibilities.

## Does every repository have exactly three methods?

No. Separate aggregate-root persistence from read-only queries and explicit
capability writers. The target's port contract determines its methods. Do not
copy an example's method count as a new requirement.

## Must every event or change create a specification?

Use the target's actual requested artifact and accepted traceability obligations.
Capture relevant event semantics and business sources when needed; do not create
an empty specification merely because an event type exists.

## Why use a controlled clock?

When behavior depends on time, an injected target-selected clock makes boundary
conditions reproducible. It does not mean every diagnostic timestamp requires a
new abstraction or that one DateProvider package is mandatory.
