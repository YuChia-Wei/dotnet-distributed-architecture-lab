# Target-owned AI context validation overlay

This directory contains repository-owned validation behavior that must remain
separate from byte-exact framework-managed paths.

The v0.16 package receipt binds every selected framework path to the published
package SHA-256. Therefore target policy is composed here instead of editing
`.ai/scripts/` or `.dev/standards/` after package installation.

The overlay preserves one prospective, no-history-rewrite boundary bundle:

- Commit subjects switch at `2026-08-13T11:05:12+08:00` from the historical
  pipe meta-notation to exactly one discriminator: issue-only or scope-only.
- AI execution provenance becomes mandatory at
  `2026-08-12T22:08:09+08:00` for this repository.
- Commit `ad194beb3fb61a18b6870093b704264746c1516b` has one exact waiver for
  the missing `Assessment-Id: ASM-20260812-002` trailer. No other validation
  error is waived.

Run the target gate with:

```powershell
python -B .dev/ai-context/tooling/validate-target-ai-context.py `
  --allow-unfinalized `
  --commit-range main..HEAD `
  --workflow-id 2026-09-06-ai-context-v0-16-0-upgrade
```

After provenance and effective rules are finalized, omit
`--allow-unfinalized` and add `--require-effective-rules`.

The published v0.16 `check-all.sh` and generic `validate-ai-context.py` are not
the target gate because the downstream package intentionally omits source-only
release assets still named by the combined validator. The repaired
`validate-shell-assets.py` now passes and is promoted into the target gate. The
version-pinned applicability manifest records the remaining package-native
failure without claiming omitted source-only checks passed. A target-owned
projection runs the package-applicable validators, 34 downstream tests, and the
preserved prospective commit-policy overlay. During `--allow-unfinalized`, the
gate also skips the provenance sub-check because the package transaction
cannot bind its target-validation receipt until this command succeeds; the
transaction recorder and final gate restore that exact validation after the
receipt exists. Profile execution, evidence reuse, and CI selection remain
inactive target choices. This overlay does not alter package bytes or
synthesize omitted source assets to conceal them.

The carried product-source projection contract and changed-path
selection/evidence schema align with this target's authority boundary.
`AICU-V011-SELECTION-001` remains resolved through v0.16.0. The new dependency
observation surface is lower-bound evidence only: an observed undeclared input
may fail, while a declared but unobserved input does not authorize shrinking a
profile. Changed-path profiles and evidence reuse remain inactive target choices
until separately selected and validated.

v0.13 removes the bundled analyzer/runtime-validation payload and replaces it
with reference-only on-demand recipes. Those recipes remain `not-selected`:
their presence does not create a project, package reference, solution entry,
CI check, runtime invocation, or activation claim. The earlier dead persistence
validation command is therefore recorded as `resolved-by-v0.13.0` rather than
kept as a live target exception.
