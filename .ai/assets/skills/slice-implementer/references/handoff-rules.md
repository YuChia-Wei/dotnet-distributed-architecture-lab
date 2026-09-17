# Slice Implementer Handoff Rules

Use `../../../shared/IMPLEMENTATION-SCOPE-ROUTING-CONTRACT.md` to distinguish
a necessary owner handoff from an optional local subtask. A selected slice
retains ownership for its authorized internal edits and validation.

## Hand Off To Architecture

Use `ddd-ca-hex-architect` when:

- bounded context or aggregate boundary is unclear;
- the responsibility, compatibility or dependency decision for an abstraction,
  interface, port or adapter is missing or changes;
- command/query/reactor ownership is disputed;
- domain language changes affect business meaning.

## Hand Off To Local Change

If the entire request is one local target/operation, select
`local-change-implementer` directly. Within an already selected slice, a bounded
local subtask is optional when isolation or clarity makes it useful and the role
execution contract permits it. Do not hand off every internal method or file,
repeat accepted decisions, or transfer the overall slice acceptance owner.

The local subtask must remain within direct call sites and its allowed radius,
with no new type, public contract or architecture boundary.

## Hand Off To Test Design

Use `bdd-gwt-test-designer` when:

- behavior examples, Given-When-Then scenarios, or assertion points are missing.

Its scenario and assertion output does not authorize implementation. To
implement concrete tests, retain or obtain the bounded slice authorization,
select `generic` for a test-only slice, load the applicable use-case,
aggregate, controller, or reactor test binding, and keep test execution as a
separate capability.

## Hand Off To Review Or Compliance

Use `code-reviewer` for implementation review through the common core and
target-selected technology extensions; missing specialist coverage stays explicit.
Use `spec-compliance-validator` when problem-frame compliance must be gated.

For remediation, the implementer records finding dispositions and evidence but
does not rewrite the originating assessment or review. Return the result to the
workflow owner, and use a new review or verification assessment when independent
closure evidence is required.
