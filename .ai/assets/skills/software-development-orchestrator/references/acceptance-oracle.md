# Software Development Orchestrator Deterministic Acceptance Oracle

This reference defines the reproducible acceptance boundary for
`DEVWF-002`. The oracle proves deterministic orchestration after an input has
already been classified and normalized. It does not claim to understand
arbitrary natural-language requests.

## Classification Boundary

The activation fixture uses this boundary:

```text
natural-language request
  -> model-in-loop classification and evaluation
  -> preclassified deterministic input envelope
  -> software-development-orchestrator acceptance oracle
```

Natural-language interpretation, ambiguous intent resolution, and classifier
quality remain owned by model-in-loop `EVAL` work. The deterministic oracle
requires:

- `classification.intent_class` equal to
  `high-level-multi-stage-software-development`;
- `classification.producer` equal to `model-in-loop-eval`;
- `classification.deterministic_boundary` equal to
  `preclassified-envelope`;
- normalized `stage_intents` from the oracle's documented vocabulary.

The free-text summary is evidence for human review only. The oracle does not
parse it, infer synonyms from it, or treat it as deterministic routing input.

## Activation Fixture

The canonical fixture and expected oracle are:

- `../fixtures/acceptance/activation-high-level-pending-approval.yaml`
- `../fixtures/acceptance/activation-high-level-pending-approval.expected.yaml`

They prove this chain with `request.named_skills: []`:

1. accept a preclassified high-level multi-stage software-development
   envelope;
2. activate `software-development-orchestrator` without a named skill dependency;
3. route normalized stage intents to capability slots and profile providers;
4. stop the implementation transition when approval is pending;
5. keep later test and review stages pending behind the same approval.

## Fresh-Session Fixture

`../fixtures/acceptance/fresh-session-checkpoint-blueprint.yaml` is the
deterministic blueprint for a temporary Git repository. The production
acceptance test creates:

- a validated parent commit and a distinct containing checkpoint commit;
- repository, branch, validated-commit, clean-state, and status-digest pins;
- a complete critical-gate observation;
- execution provenance and attribution evidence;
- a development locator, registered handoff checkpoint, target test policy,
  and current task with recorded unit/integration test state.

The acceptance oracle invokes:

```text
python .ai/scripts/validate-workflow-handoff.py \
  --root <fixture-repository> \
  --checkpoint <checkpoint-path> \
  --verify-repository
```

It then applies the development continuation and task contracts to prove that
the checkpoint, current task, target policy, and recorded test state agree.
The fixture does not re-run a real target repository's critical gate; it
verifies the durable observation and repository pins. Execution of real
environment-dependent gates remains target-owned acceptance evidence.

## Commands

Run both acceptance paths:

```text
python .ai/scripts/tests/test_software_development_orchestrator_acceptance.py -v
```

Run the activation oracle directly:

```text
python .ai/scripts/validate-software-development-orchestrator-acceptance.py activation \
  --fixture .ai/assets/skills/software-development-orchestrator/fixtures/acceptance/activation-high-level-pending-approval.yaml \
  --expected .ai/assets/skills/software-development-orchestrator/fixtures/acceptance/activation-high-level-pending-approval.expected.yaml
```
