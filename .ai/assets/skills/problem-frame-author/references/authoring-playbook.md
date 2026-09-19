# Problem Frame Authoring Playbook

## Goal

Turn existing requirement/spec truth into a first validator-ready problem-frame draft for one use case.

## Required Inputs

- target use case name
- available requirement/spec sources and their authority status, or an explicitly
  requested observed/inferred recovery from bounded code and tests
- optional code/tests for gap filling

Use `../../../shared/AUTHORING-BOUNDARY-CONTRACT.md` to confirm the requested
CBF/SWF artifact. Code-only recovery does not require fabricating requirement
or spec documents; missing normative intent remains an open question and
cannot support a compliance claim.

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
4. Draft `machine/use-case.yaml`, the selected domain file, `frame.yaml`, `machine/machine.yaml`, then the selected acceptance or requirement files. Use only the branch selected in step 2:

   | Frame type | Domain file | Acceptance or requirement files |
   | --- | --- | --- |
   | `CBF` | `controlled-domain/aggregate.yaml` | `acceptance.yaml` |
   | `SWF` | `workpiece/aggregate.yaml` | `requirements/*.yaml` |

   Do not create the other frame type's files unless a separate frame has been explicitly selected.

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
