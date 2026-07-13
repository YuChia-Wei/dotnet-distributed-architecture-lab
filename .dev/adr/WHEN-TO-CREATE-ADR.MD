# When To Create ADR

Create an ADR only when a change represents a structural decision.

## Create An ADR When

- You are defining a new architecture boundary.
- You are changing dependency direction or layer responsibility.
- You are introducing a new cross-cutting pattern.
  - Examples include outbox, event sourcing, profile isolation, and multi-agent governance.
- You are deciding repo-wide canonical source ownership.
  - For example, the division of responsibilities among `.ai/`, `.dev/standards/`, and `.dev/guides/`.
- You need to preserve an explicit tradeoff record.
  - Someone may later ask why a different approach was not chosen.

## Do Not Create An ADR When

- You are only expanding a usage guide.
- You are only adding a checklist, template, or example.
- You are only moving an existing rule to a better canonical document.
- You are only making a local implementation adjustment.
- You are only changing code style, naming, or one small file.

## Decision Test

A decision usually merits an ADR when both of the following are true:

1. It affects multiple files, modules, or future workflow runs.
2. Without a recorded tradeoff, the team is likely to revisit the same discussion.

## Default Preference

When only adding or correcting a rule:

- Update `.dev/standards/` first.
- Alternatively, update `.dev/guides/`.
- Alternatively, update `.ai/`.

Do not place a rule that belongs in canonical documentation into an ADR and then leave it unresolved there.
