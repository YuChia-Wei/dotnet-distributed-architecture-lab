# Target Technology Selection Policy

Rule IDs: `TECH-SELECT-001`, `TEST-MOCK-001`.

## Purpose

This policy defines one target-owned mechanism for selecting or overriding
technology choices such as mocking libraries, ORMs, database providers, message
brokers, dispatch frameworks, and runtime observability adapters.

Architecture invariants and technology selections are different:

- an invariant such as Given-When-Then test semantics cannot be replaced by a
  technology selection;
- a profile default such as NSubstitute may be replaced through an explicit
  target selection;
- conditional technology guidance applies only when its slot selects that
  technology.

## Selection Record

Target selections belong in generated `.dev/project-config.yaml` under
`technologySelections`. Every record uses the schema in
`.ai/assets/skills/repo-structure-sync/templates/technology-selection.schema.yaml`.

```yaml
technologySelections:
  - slot: testing.mocking
    value: Moq
    status: selected
    source: explicit-target-decision
    evidence:
      - .dev/requirement/TECH-STACK-REQUIREMENTS.MD
    reason: Existing product test stack
```

Required semantics:

- `slot` is a stable dotted capability name, not a package-specific field;
- `value` is the target selection;
- `status` is `selected`, `not-applicable`, or `unresolved`;
- `source` is `repository-evidence` or `explicit-target-decision`;
- `evidence` contains repository-relative paths supporting the selection;
- `reason` explains an explicit override or unresolved decision.

An absent slot does not invent target truth. If the framework registers a
profile default for that slot, the default applies until target evidence records
another selection. A target override changes the selected technology, not the
architecture invariants surrounding it.

Recommended stable slots include:

- `testing.mocking`
- `testing.bdd-runner`
- `persistence.orm`
- `persistence.database`
- `messaging.broker`
- `messaging.framework`
- `observability.runtime`

New slots must reuse this record shape.

## Default And Override Resolution

Resolve one slot in this order:

1. explicit target decision recorded in `technologySelections`;
2. repository evidence recorded by `repo-structure-sync`;
3. the applicable framework profile default;
4. unresolved, when no default exists.

Do not infer a selection from an illustrative example or from a package-specific
document that the target has not adopted.

## Mocking Default

Rule `TEST-MOCK-001` defines NSubstitute as the dotnet-backend profile default for
`testing.mocking`. A target may select Moq, FakeItEasy, or another library by
recording one selection record with evidence.

The following remain invariant regardless of mocking library:

- tests preserve Given-When-Then structure and naming;
- tests do not inherit shared test base classes;
- test doubles are used only at appropriate external boundaries;
- interaction verification remains async-safe and readable;
- one test suite does not mix mocking libraries without an explicit migration
  decision.

Agent guidance, code review, test generation, and validation must consume the
selected slot. They must not require edits to every downstream standard when a
target changes the mocking library.

## Ownership And Upgrade

- `repo-structure-sync` creates or refreshes target selection records from
  file-backed evidence and explicit user decisions.
- `ai-context-upgrader` treats `.dev/project-config.yaml` as target-owned truth
  and reconciles incoming defaults without overwriting selections.
- Framework upgrades may change a profile default, but they do not silently
  replace a recorded target selection.
