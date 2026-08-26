# Routine Validation Activation Policy

Routine automatic validation is resolved before interpreter discovery and does
not itself execute a validator. Its authority is tracked
`.dev/project-config.yaml#validation.routine`.

`local.mode` defaults to `manual`; approved modes are `manual`,
`auto-if-ready`, and `required`. `manual` means zero routine interpreter probes,
validator executions, and retries. The only persistent developer setting is
ignored `/.dev/validation.local.conf`, exactly one data line
`validation.routine.local=<approved-mode>`. It is data only, never sourced,
may only strengthen the tracked setting, and is never written implicitly.
Environment variables and runtime-specific settings are not overrides.

CI defaults to `unconfigured`; `advisory` and `required` are target-owned.
`required` is fail-closed without a tracked workflow, exact command/profile,
provisioned prerequisites, durable check evidence, and any claimed provider
merge-gate verification. Local preference never weakens CI.

Keep the legacy outcome enum. An applicable routine check unselected by policy
records `outcome: not-applicable` and `selection_reason: not-run-by-policy`;
it is not passed. For a selected command and stable task/checkpoint state allow
one preflight and one execution, then one retry only after recorded material
state change. Record policy source, command fingerprint, prerequisite result,
execution outcome, attempt count, retry justification, and at most two CI
observations. Explicit CLI and lifecycle-owned install, apply, init, upgrade,
provenance, governance, release, and publication commands are unaffected.
