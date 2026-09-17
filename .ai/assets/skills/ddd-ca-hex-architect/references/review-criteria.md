# Architecture Review Criteria

Use with the shared artifact design/review contract. This skill owns DDD,
Clean Architecture and Hexagonal design reasoning. Apply those lenses to the
requested scope; an unadopted CQRS, event-sourcing or messaging choice is not
automatically a defect. Review executable code through `code-reviewer`.

| Criterion | Evidence to inspect |
| --- | --- |
| Requirements and quality | Link decisions to requirement IDs and measurable quality constraints. Separate evidence, assumptions and unknown workload/availability needs. |
| Responsibility and dependencies | Context/module ownership, ubiquitous language, inbound/outbound ports, dependency direction and adapter isolation. |
| Data and consistency | Data owner, invariant, aggregate/transaction boundary and consistency requirement. Check intermediate states and cross-boundary effects against that requirement. |
| Tradeoffs | Credible alternatives, reasons, cost and rejected options. Simpler valid designs are acceptable; extra abstractions need a purpose. |
| Failure and recovery | Relevant failure windows, retries, idempotency, durable state, compensation, observability and operational ownership. Do not assume delivery guarantees. |
| Evolution | Contract compatibility, migration/rollout order, versioning and recoverability when the proposed change requires them. |
| Testability | Observable acceptance and controllable dependency seams; identify required real integration evidence and feasibility limits. |

Every finding needs an artifact location and requirement or applicable rule.
Distinguish a demonstrable violation from an unanswered design question. Do not
choose a vendor or redefine a quality constraint to make a proposal pass.
Hand requirement decisions to `requirement-author`, specification changes to
`spec-author`, GWT test design to `bdd-gwt-test-designer`, and accepted bounded
implementation to `slice-implementer` or `local-change-implementer` as applicable.
An implementation handoff preserves the decision record and authorization; it
does not silently turn suggested architecture into accepted target truth.
