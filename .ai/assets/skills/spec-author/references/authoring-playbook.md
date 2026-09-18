# Spec Authoring Playbook

## Goal

Turn requirement truth into repository-aligned specs under `.dev/specs/`.

## Workflow

1. Read `.dev/specs/SPEC-GUIDE.MD`.
2. Read `.dev/specs/SPEC-ORGANIZATION-GUIDE.MD`.
3. Decide the target spec type:
   - use case spec
   - entity/value-object spec
   - adapter/controller spec
   - test spec
4. Draft the minimum required fields and recommended extras.
5. Recommend the output path that matches aggregate boundaries.
6. Escalate to `ddd-ca-hex-architect` if aggregate ownership is unclear.

## Boundary Rule

`spec-author` turns requirement truth into structured specs.
It does not redesign architecture and it does not claim implementation/test completion.
