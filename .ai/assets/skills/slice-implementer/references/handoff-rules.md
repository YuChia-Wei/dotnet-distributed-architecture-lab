# Slice Implementer Handoff Rules

Use explicit handoff instead of continuing when a slice uncovers work outside its boundary.

## Hand Off To Architecture

Use `ddd-ca-hex-architect` when:

- bounded context or aggregate boundary is unclear;
- new abstraction, interface, port, adapter, or dependency direction is needed;
- command/query/reactor ownership is disputed;
- domain language changes affect business meaning.

## Hand Off To Local Change

Use `local-change-implementer` when:

- the slice contains one local class/object/symbol technical edit;
- the change is limited to direct call sites;
- no new class/interface or architecture boundary is needed.

## Hand Off To Test Design

Use `bdd-gwt-test-designer` when:

- behavior examples, Given-When-Then scenarios, or assertion points are missing.

Its scenario and assertion output does not authorize implementation. To
implement concrete tests, retain or obtain the bounded slice authorization,
select `generic` for a test-only slice, load the applicable use-case,
aggregate, controller, or reactor test binding, and keep test execution as a
separate capability.

## Hand Off To Review Or Compliance

Use `code-reviewer` for .NET backend review findings.
Use `spec-compliance-validator` when problem-frame compliance must be gated.

For remediation, the implementer records finding dispositions and evidence but
does not rewrite the originating assessment or review. Return the result to the
workflow owner, and use a new review or verification assessment when independent
closure evidence is required.
