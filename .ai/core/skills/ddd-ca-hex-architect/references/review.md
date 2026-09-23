# Review a fixed architecture artifact

Bind the path/version and digest, or quote bounded inline input, before review.
Record requirements, decisions, quality constraints and coverage separately:
artifact claims cannot validate themselves. Leave the subject unchanged. If
revision is also requested, finish this result before [design](design.md)
revises it; a later review must bind the revised subject.

Apply relevant common criteria and selected target rules. Missing authority
blocks the affected judgment. This package has no technology extension; report
missing selected specialist coverage and do not substitute common reasoning for
a required specialist gate. A different valid style, unadopted CQRS or absence
of a speculative abstraction is not a defect.

| Criterion | Evidence and questions |
| --- | --- |
| Requirements and quality | Bind decisions to requirements/ACs and measurable constraints. Which workload/availability claims remain assumptions? |
| Responsibility and language | Does each context/module have an owner, coherent vocabulary and purpose? Are disputed terms or shared responsibilities explicit? |
| Dependencies and ports | Does dependency direction protect business decisions? Are external adapters isolated where needed? Does each abstraction have a purpose? |
| Data and consistency | Who owns state/invariants? Do aggregate/transaction boundaries and intermediate states meet the consistency requirement? |
| Alternatives | Are credible options and simpler valid designs considered with costs/consequences? Is preference masquerading as a requirement? |
| Failure and recovery | Are relevant retry, duplicates, ordering, durability, compensation, observability and operational ownership explicit? Are guarantees supported? |
| Evolution | Where needed, are compatibility, rollout, migration, recovery and rollback limits coherent for existing consumers? |
| Testability | Are outcomes observable and dependency/time/data seams controllable? Is real integration evidence distinguished from mocks? |

Each supported finding needs location, criterion/source requirement, evidence,
triggering condition, impact, severity rationale, uncertainty and bounded
correction. Distinguish defects, questions and optional improvements; retain
valid alternatives and their tradeoffs. Review artifacts here; executable-code
review is a separate responsibility. Do not invent a requirement/vendor choice
to make a proposal pass.

Return subject, sources, findings, criterion coverage, unavailable/excluded
coverage, assumptions and exact unresolved decisions. State actual inspections,
commands and limits. No findings means none supported in the inspected scope,
not compliance or acceptance. A digest proves identity, not execution or
independent authorship.

Select one classification with supporting author relationship:

- `self-check` if the reviewer authored or repaired the subject.
- `review; independence not established` when author relationship or required
  independence evidence is unknown.
- `independent-review` only when a different author, fixed subject, read-only
  reviewer and applicable target independence requirements are evidenced.

A different prompt/model alone establishes no independence. This method creates
no mandatory audit packet; required target acceptance remains separate.
Optional handoff names affected artifact, source IDs, proposed correction,
decision owner and existing revision/implementation permission. Return that
semantic handoff when another skill is unavailable. It cannot enlarge scope
or turn proposed architecture into accepted truth.
