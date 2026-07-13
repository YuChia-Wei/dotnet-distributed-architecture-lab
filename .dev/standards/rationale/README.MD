# Standards Rationale

This directory stores portable rationales for pattern choices.

It answers:

- why this knowledge base prefers a given pattern;
- why other common alternatives are not preferred;
- what tradeoffs underlie these rules.

## When Content Belongs Here

- The rule already exists in a standards document.
- Its rationale was previously scattered across ADRs.
- The rationale is worth carrying with `.dev/` / `.ai/` into other projects.

## Division of Responsibility with ADRs

- `ADR`
  - records which decision this repository made at a specific time;
- `standards/rationale`
  - records why this kind of rule generally holds.

Therefore, when an ADR's primary remaining value is methodological rationale, extract that rationale here before deciding whether to retire the ADR.
