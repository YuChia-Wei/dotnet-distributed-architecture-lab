# .NET backend learning path

## Applicability

This optional .NET reference applies only to the target-selected architecture,
providers and adopted test rules. Examples do not install packages, select an ORM,
broker or Event Sourcing, create fixed project paths, or prove execution. Preserve
per-domain persistence decisions and the target-selected GWT contract; BDDfy and
mocking packages remain separately selected.

This optional guide organizes the packaged references. Start from the target's
requirements, root instructions and adopted decisions. Select only relevant
topics; no initialization skill, generated context or fixed layout is required.
Examples of EF Core, Wolverine, Event Sourcing and BDDfy do not select those
technologies for the target or supply current runtime/version compatibility.

## Architecture and language

Read the [architecture overview](../design/architecture-overview.md),
[architecture rules](../shared/architecture-config.md) and
[use-case/handler boundaries](../standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD).
Identify the bounded context, aggregate/invariant owner and dependency direction
before choosing a directory or implementation type. Aggregate ownership is a
business/transaction decision, not a file-count rule. Domain events express
accepted domain meaning; Event Sourcing is a separate persistence choice.

A command changes state and a query observes it. Output types and routes come
from the target contract. A dispatch handler maps a real inbound entry; it does
not replace use-case behavior. Cross-context reactors coordinate only accepted
integration effects and preserve the target's consistency/replay constraints.

## Implement the selected behavior

Use [use-case examples](../examples/usecase/README.md) and
[code templates](../references/CODE-TEMPLATES.MD) as starting points.
Choose persistence per bounded context; do not standardize an ORM just because
one example uses it. If selected, read [outbox examples](../examples/outbox/README.md)
and [profile isolation](DUAL-PROFILE-CONFIGURATION-GUIDE.md).
Package-neutral application ports keep concrete messaging/ORM registration at
the adapter/composition boundary. Time, randomness and external effects need
controlled seams when the target's behavior and tests depend on them.

## Design observable verification

Read the [testing strategy](../shared/testing-strategy.md),
[test standards](../standards/coding-standards/test-standards.md) and
[GWT example](../examples/reference/bdd-gwt-test-template.md) only under their
adopted applicability. Preserve the target-selected Given-When-Then structure;
BDDfy can be replaced by explicit Given/When/Then steps in the selected runner.
Mocking packages and `.feature` support are separately selected. Unit/domain
checks can call domain behavior directly; application tests exercise application
ports instead of bypassing the boundary their scenario promises to verify.

Use [test-data guidance](TEST-DATA-PREPARATION-GUIDE.md) for complete, isolated
business setup. Read-only observation of relevant repositories is valid when
explicitly permitted by the scenario design. Real integration acceptance needs
actual infrastructure evidence rather than example text or synthetic results.

## Diagnose and retain useful knowledge

Use [common pitfalls](../references/COMMON-PITFALLS.MD),
[failure patterns](../references/FAILURE-CASES.MD) and
[common mistakes](COMMON-MISTAKES-GUIDE.md) to form hypotheses, then inspect the
actual target. Examples do not establish its root cause. Preserve relevant
accepted decisions and reusable observations through the target-selected owners;
a completed tutorial does not require a workflow, ADR or Lesson.
