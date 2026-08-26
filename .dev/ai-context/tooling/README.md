# Target-owned AI context validation overlay

This directory contains repository-owned validation behavior that must remain
separate from byte-exact framework-managed paths.

The v0.13 package receipt binds every selected framework path to the published
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
  --workflow-id 2026-08-12-ai-context-v0-13-upgrade
```

After provenance and effective rules are finalized, omit
`--allow-unfinalized` and add `--require-effective-rules`.

The published v0.13 `check-all.sh` and `validate-ai-context.py` are not the
target gate. Their downstream projection still retains source-only paths that
are absent from the published payload, and the new package-smoke/closeout
routes add further missing source-only dependencies. The version-pinned
applicability manifest records those package-native failures for upstream
feedback. The profile-registry test itself still requires a source-only
distribution profile, so its exact bytes are pinned as defect evidence and it
is excluded from the downstream gate. Applicable lessons and canonical commit
policy tests are selected instead. The new stock code-review routing test is
also recorded as a projection defect because it imports an omitted source-only
package module before its tests can run. A target-owned projection executes
the downstream-applicable GWT1-GWT7 contract; source-release payload GWT8 is
explicitly not applicable. Profile execution, evidence reuse, and CI selection
remain inactive target choices. This overlay does not alter package bytes or
synthesize omitted source assets to conceal them.

The carried product-source projection contract and changed-path
selection/evidence schema. The projection contract aligns with this target's
authority boundary, but `AICU-V011-SELECTION-001` records that direct matches
are marked selected before dependency expansion, causing the recursive helper
to return before traversing declared dependencies. The new selector behavior
also shipped without matching projected regression coverage. Changed-path
profiles and reuse therefore remain inactive until a later exact package proves
the defect resolved.

v0.13 removes the bundled analyzer/runtime-validation payload and replaces it
with reference-only on-demand recipes. Those recipes remain `not-selected`:
their presence does not create a project, package reference, solution entry,
CI check, runtime invocation, or activation claim. The earlier dead persistence
validation command is therefore recorded as `resolved-by-v0.13.0` rather than
kept as a live target exception.
