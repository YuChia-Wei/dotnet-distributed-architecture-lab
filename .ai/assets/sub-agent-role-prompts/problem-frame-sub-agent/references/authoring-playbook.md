# Problem Frame Sub-Agent Playbook

Use this role prompt when a delegated worker should produce a first problem-frame draft.

## Task Shape

The sub-agent should:

- work from requirement/spec truth first
- use code/tests only to fill gaps or expose mismatches
- produce a validator-ready file set for one use case

## Expected Draft Set

- `frame.yaml`
- `machine/machine.yaml`
- `machine/use-case.yaml`
- `controlled-domain/aggregate.yaml` or `workpiece/aggregate.yaml`
- `acceptance.yaml` or `requirements/*.yaml`

## Mandatory Notes

- list every inferred item
- list missing truth that blocks validator-grade confidence
- recommend the next handoff:
  - `bdd-gwt-test-designer` when scenario design should continue
  - `spec-compliance-validator` only after code/tests exist
