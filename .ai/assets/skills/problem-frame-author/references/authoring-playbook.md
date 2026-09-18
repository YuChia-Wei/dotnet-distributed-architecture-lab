# Problem Frame Authoring Playbook

## Goal

Turn existing requirement/spec truth into a first validator-ready problem-frame draft for one use case.

## Required Inputs

- target use case name
- requirement files
- spec files
- optional code/tests for gap filling

## Workflow

1. Pick one use case.
2. Prefer `CBF` unless the use case is clearly a workpiece-oriented `SWF`.
3. Build a compact extraction sheet:
   - actor
   - command or trigger
   - input fields
   - preconditions
   - success and failure outcomes
   - domain events
   - external systems
   - authority boundaries
   - timeout / retry / duplicate rules
   - acceptance scenarios
4. Draft files in this order:
   - `machine/use-case.yaml`
   - `controlled-domain/aggregate.yaml`
   - `frame.yaml`
   - `machine/machine.yaml`
   - `acceptance.yaml`
5. Mark every inferred item as inferred.
6. End with open questions and the next handoff.

## External-System Heuristics

When the use case depends on external systems, always ask:

- Which system is the authority?
- Can success be known synchronously, asynchronously, or both?
- What does timeout mean?
- Which retries or callbacks can duplicate side effects?
- Which identifiers are mandatory for audit and reconciliation?

## Drafting Rules

- Keep one directory per use case.
- Keep one aggregate focus unless the use case truly spans multiple aggregates.
- Keep scenarios traceable to requirement/spec identifiers.
- Do not invent final test implementation; only provide `tests_anchor`.
- Do not claim validator completion; drafting is only the input stage.
