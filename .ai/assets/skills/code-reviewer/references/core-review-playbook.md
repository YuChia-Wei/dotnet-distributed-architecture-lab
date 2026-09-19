# Common Code Review

The common route is available with software-development-core. It supplies a
review method across languages; it does not claim specialist knowledge that an
unavailable extension or missing target contract would have supplied.

## Establish The Subject

Identify the requested files or diff, base and reviewed revision, intended
behavior, acceptance criteria and relevant target decisions. A patch review
traces affected callers and dependencies only as needed to assess impact.
Separate pre-existing problems from regressions introduced by the change.
If intent or the subject is ambiguous, state the ambiguity and ask only for
information necessary to judge the affected behavior. Do not invent requirements.

Record selected components, technology evidence and architecture methods per
reviewed partition. The core route always applies; installed extensions add
specialist checks only to their matching partitions. An unknown technology can
still receive bounded reasoning about visible behavior and supplied contracts.
Report unavailable coverage and any resulting acceptance blocker explicitly.

## Review Reasoning

- Trace inputs, state changes, side effects and outputs against the intended
  contract. Examine boundaries, invalid inputs, failure propagation and cleanup.
- Follow affected dependencies, API/data compatibility and ownership boundaries.
  Consider concurrency, retries and idempotency when the reviewed behavior uses them.
- Examine relevant security boundaries, resource lifetime and performance costs
  supported by the scope. Do not turn every review into an exhaustive security
  or performance audit, or invent an impact without a feasible trigger.
- Compare tests with observable behavior: useful assertions, meaningful failure
  cases, affected contracts and gaps. Existing test output is evidence with a
  subject and environment, not proof that every changed behavior is correct.
- When tests implement selected GWT scenarios, consume
  `.ai/assets/shared/GWT-TEST-HANDOFF-CONTRACT.md`. Follow step methods into
  actual setup, action and assertions; check every designed outcome and data-row
  mapping. Names, comments, compilation or green results alone do not prove
  that the scenario was faithfully implemented.
- Apply adopted architecture and target rules within their scope. A different
  valid design or unfamiliar library is not itself a defect. Do not impose DDD,
  CQRS, Event Sourcing, a broker, DI helper or testing library without authority.
- Prefer actionable defects and material maintainability risks over style
  preferences. Mark uncertainty and distinguish verified facts from hypotheses.

Consume applicable effective-rule packets before checking catalog rules. A
missing or stale packet cannot be replaced by a framework default or this
playbook. A concern directly supported by supplied behavior or contract may be
reported with its source; do not present it as verification of unresolved rules.

## Evidence And Findings

For each finding, identify the location, trigger, observed or reasoned failure,
impact, applicable contract, supporting evidence, severity and confidence.
Keep the shortest explanation that lets the author reproduce or assess it.
Tests, analyzers and searches may support reasoning; record what actually ran,
what was reused with proof, and what was not checked. Do not run code, install
dependencies, access credentials or broaden external actions merely because
review was requested; follow the task's execution permissions.

Return no findings when the examined evidence supports none. State the reviewed
coverage and residual limitations without manufacturing issues or claiming
universal correctness. Scores are optional only when requested or required by
the target, and need a stated rubric; they do not replace findings.

Review remains read-only. Recommend bounded corrections and the next owner,
without implementing a repair or redefining target architecture. Self-check is
distinct from independent acceptance; preserve the fixed subject, reviewer
identity and governing evidence contract when independence is required.
