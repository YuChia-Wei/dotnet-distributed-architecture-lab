# Local Change Implementer Boundaries

## Owns

- one local class/object/method/symbol technical edit, including a private
  implementation helper type only when it preserves the accepted target, radius,
  behavior, responsibility, dependency direction, lifetime, and transaction boundary;
- direct call-site updates;
- behavior-preserving local cleanup;
- small localized bug fix;
- local SQL/ORM implementation adjustment.

## Does Not Own

- planning a bounded implementation slice;
- command/query/reactor mode selection;
- architecture direction changes;
- public or responsibility-changing class/interface extraction;
- dependency direction changes;
- domain language changes;
- cross-module changes.

## Handoff

- Use `slice-implementer` when the work is a coordinated bounded behavior/refactoring
  goal or introduces a public, responsibility-changing, dependency/lifetime/transaction-
  affecting type within an accepted design. Multiple direct call-site files alone do
  not require a slice. Apply the shared implementation scope contract.
- Use `ddd-ca-hex-architect` when the work needs architecture or domain-language decisions.
- Use `code-reviewer` when the local change came from review findings and needs independent verification.

For an unexplained observed symptom, use `diagnostic-analyst` to establish a bounded diagnosis before selecting a repair. A diagnostic handoff does not grant repair authorization.
