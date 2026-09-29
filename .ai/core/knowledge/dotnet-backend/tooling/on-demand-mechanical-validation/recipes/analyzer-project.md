# Target-Owned Analyzer Starting-Point Recipe

Evidence tier: `reference-only`.

This recipe supplies no analyzer project, selected provider delivery, SDK,
Roslyn version, test framework, package source, compatibility result, or
execution result. Use it only after a target owner records a bounded diagnostic
subset from [`../diagnostic-mapping.yaml`](../diagnostic-mapping.yaml) in the
[`../templates/provider-selection.template.yaml`](../templates/provider-selection.template.yaml)
shape.

## Copy Bounded Starting Templates

Copy these files into a target-owned path only after the target records its
selection decision:

- [`../templates/minimal-diagnostic-analyzer.cs.template`](../templates/minimal-diagnostic-analyzer.cs.template)
- [`../templates/minimal-diagnostic-analyzer-test.cs.template`](../templates/minimal-diagnostic-analyzer-test.cs.template)
- [`../templates/code-fix-decision.md`](../templates/code-fix-decision.md)

They are deliberately incomplete reference material. Replacing placeholders,
choosing compiler and test dependencies, creating project structure, wiring
selected projects, and deciding severity remain target-owned work. The
framework neither writes target source nor selects a provider on copy.

The analyzer test template preserves explicit Given / When / Then steps. The
target must add positive, negative, exception, and false-positive coverage for
each selected rule. DBA labels are compatibility names only; canonical standards
remain the semantic owners.

## Provider Availability Gate

Read [`../provider-contract.yaml`](../provider-contract.yaml) before treating a
selection as executable.

- `not-selected` is the default capability gap; fallback templates remain
  available and no installation is inferred.
- `declined` records an explicit target decision without changing the official
  recommendation.
- `selected-unavailable` prohibits execution until exact provider identity,
  fresh readiness, and compatibility evidence exist.
- `synthetic-readiness-proven` proves only a schema transition. It does not
  prove real-provider execution.

## Evidence Required For an Active Claim

- a target decision naming selected diagnostics and exceptions;
- exact provider identity and delivery evidence selected by that target;
- separately typed and digested readiness, compatibility, and execution
  receipts;
- implementation and test commit;
- applied target-owned wiring and severity configuration;
- exact validation outcomes against the claimed target commit; and
- a compatibility and rollback statement.

Without all of that evidence, report the target state as `not-selected`,
`selected-unavailable`, or `unresolved`; do not infer activation from this
directory.
