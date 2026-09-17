# Target-owned AI context validation overlay

This directory contains repository-owned validation behavior that must remain
separate from byte-exact framework-managed paths.

The v0.17 package receipt binds every selected framework path to the published
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
  --workflow-id 2026-09-18-ai-context-v0-17-0-disposable-upgrade
```

After provenance and effective rules are finalized, omit
`--allow-unfinalized` and add `--require-effective-rules`.

The published v0.17 `check-all.sh` and generic `validate-ai-context.py` are not
the target gate because the downstream package intentionally omits source-only
release assets still named by the combined validator. The repaired
`validate-shell-assets.py` now passes and is promoted into the target gate. The
version-pinned applicability manifest records the remaining package-native
failure without claiming omitted source-only checks passed. A target-owned
projection runs the package-applicable validators, target-owned downstream tests, and the
preserved prospective commit-policy overlay. During `--allow-unfinalized`, the
gate also skips the provenance sub-check because the package transaction
cannot bind its target-validation receipt until this command succeeds; the
transaction recorder and final gate restore that exact validation after the
receipt exists. Profile execution, evidence reuse, and CI selection remain
inactive target choices. This overlay does not alter package bytes or
synthesize omitted source assets to conceal them.

The carried product-source projection contract and changed-path
selection/evidence schema align with this target's authority boundary.
`AICU-V011-SELECTION-001` remains resolved through v0.17.0. The new dependency
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

## Explicit target-owned terminal audit gate

`validate-target-terminal-audit.py` implements a prospective repository-owned
closeout check. It is not the framework upgrader's UPG-004 contract and does not
retroactively certify an earlier upgrade, rewrite its transaction, or authorize
integration. No `.ai/` package bytes are changed.

Only a tracked workflow locator with this explicit extension opts in:

```yaml
terminal_audit:
  schema_version: "1.0"
  required: true
  historical_record:
    path: "<repository-relative unchanged incomplete record>"
    sha256: "<raw SHA-256>"
    disposition: "superseded-incomplete"
  current_record: "<repository-relative receipt JSON>"
```

The default scan checks tracked locators only; it does not infer obligations
from a workflow's title, age, version, or location. An explicit `--workflow-id`
requires that exact locator to opt in. The historical record must remain
unchanged. `current_record` must be a separate tracked file (staged files count
while assembling a checkpoint).

An `in_progress` workflow may retain precisely
`{"schema_version":"1.0","status":"pending"}`. The command discloses pending;
it does not report terminal acceptance. A `completed` workflow requires a
passed receipt with exactly these fields:

| Field | Contract |
| --- | --- |
| `schema_version`, `status` | `"1.0"`, `"passed"` |
| `subject_commit`, `subject_tree` | Full 40-character Git IDs; the commit must exist and resolve to that tree. |
| `reviewer_id`, `invocation_id` | Non-empty genuine runtime identity and invocation reference; not invented from a planned role. |
| `role_path` | `.ai/assets/sub-agent-role-prompts/fixed-head-independent-auditor/sub-agent.yaml` |
| `started_at`, `completed_at` | ISO 8601 seconds with UTC offset; completion cannot precede start. |
| `criteria`, `report`, `invocation_evidence` | Each is exactly `{path, sha256}`, with a safe repository-relative file and its raw SHA-256. |
| `authority_hashes` | Mapping of repository-relative authority paths to raw SHA-256; must include `role_path`. |

The pinned invocation JSON contains exactly `status`, `subject_commit`,
`subject_tree`, `reviewer_id`, `invocation_id`, `role_path`, `started_at`,
`completed_at`, and `evidence_refs`. Shared values must equal the receipt;
`evidence_refs` is a non-empty unique list of safe existing files including
the pinned report. Preserve the actual child response with its real invocation
metadata. These checks establish evidence integrity and consistent binding,
not cryptographic reviewer authentication, independence, or prose truth; the
parent must verify those against the genuine child invocation.

Criteria and authority hashes must match both the reviewed commit's Git blobs
and the current checkout. Outcome reports need not exist in the reviewed tree:
they are produced after review. Ordinary retained evidence must be tracked or
staged; traversal, absolute paths, symlinks, reparse points, missing/empty files,
failed results, unknown fields, and raw hash drift are rejected. A retained
historical audit is not a claim that the current HEAD has been reviewed.

```powershell
python -B .dev/ai-context/tooling/validate-target-terminal-audit.py `
  --workflow-id 2026-09-06-ai-context-v0-16-0-upgrade
python -B .dev/ai-context/tooling/validate-target-terminal-audit.py `
  --admit <fresh-final-audit-receipt.json>
```

Explicit `--admit` accepts an external or ignored receipt and repository-relative
ignored outcome evidence to avoid changing the audited tree merely to record
its result. It requires a clean tracked checkout with no non-ignored untracked
files and the exact reviewed full Git tree at current HEAD. A SHA-only history change or a no-ff merge with the
same tree is admissible; changing even only evidence files requires a fresh
audit of that new tree. There are no evidence-only exclusions, ancestor
shortcuts, or implicit waivers. Run the same read-only admission before and
after local integration; it does not itself merge, push, or mutate any state.

Focused tests run with `python -B -m unittest discover -s
.dev/ai-context/tooling/tests -p test_target_terminal_audit.py -v`. They use
isolated temporary Git repositories and are included in the target gate's
normal test discovery. On Windows, an execution sandbox that denies temporary
Git repository creation requires an appropriately authorized test execution;
setup failures must not be described as assertion passes.
