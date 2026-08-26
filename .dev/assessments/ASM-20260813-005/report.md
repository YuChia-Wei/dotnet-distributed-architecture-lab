# AI Context Audit Report

## Metadata

- `assessment_id`: `ASM-20260813-005`
- `assessment_type`: `ai-context-verification`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `created_at`: `2026-08-13T11:33:19+08:00`
- `subject_commit`: `8437e178db96237edd7457bb48c531afb3bdae79`
- `previous_assessment`: `.dev/assessments/ASM-20260813-004/report.md`
- `workflow_refs`: `2026-08-12-ai-context-v0-13-upgrade`

## Executive Summary

- Decision: `healthy-with-followups`
- Finalization verdict: `SAFE-TO-FINALIZE`
- Overall score: `N/A` (the requested developer-experience score is reserved for the final v0.13 assessment).
- Owner decision: none remains for the v0.12 checkpoint.

The exact v0.12 package, 80-operation structural candidate, 640-path receipt,
prospective title-policy transition, target-owned validation overlay, inactive
settings, six active defect records, and durable workflow state are internally
consistent. The first audit correctly blocked false durable evidence; the
metadata-only correction preserved that failure and the second audit accepted
the fixed clean subject. Both audits were independent, read-only, fail-closed,
and executed by `gpt-5.6-sol` at `max` reasoning effort.

## Verified Evidence

| Surface | Result | Evidence |
| --- | --- | --- |
| Package | passed | ZIP/sidecar `29af751de3ab1fe7e0ac3ce838eee327bb35f53542dae8a74e09feb8a4390cf5`; 660/660 checksums; 661 archive/extracted files; source `a4fd14f…` |
| Plans | passed | byte-identical SHA-256 `623d79040aacfa0dabaa63498b6e03058367ec052fe4a4863a7c1700c50e5f14` |
| Receipt | passed | SHA-256 `bd4d6dea53520c7c91b84a770c105a1d53c889faeb07ba8306c3925d7b3bfda9`; 640/640 paths; 80 applied; zero skipped/ignored |
| Commit transition | passed | 39 legacy commits plus three issue-only commits; target boundary `2026-08-13T11:05:12+08:00`; no history rewrite |
| Historical waiver | passed | exact `ad194beb…` / `ASM-20260812-002` / `missing-matching-trailer` only |
| Target overlay | passed | 25/25 pins; 31/31 target tests; exact stale-catalog-only candidate allowance |
| Settings | passed | profiles, changed-path execution, evidence reuse, and provider inactive; local manual; CI unconfigured |
| Existing authority | passed | v0.11 provenance, four CUST records, 13 dispositions, 20 routes/packets/state unchanged |
| Git state | passed | exact clean subject `8437e178db96237edd7457bb48c531afb3bdae79`; `git diff --check` passed |

The independent outside-sandbox target gate passed in 34.1 seconds and covered
all 42 `main..HEAD` commits. Candidate mode accepts only
`effective state catalogs[0] is stale`; any additional diagnostic or stderr
fails closed until packet and state regeneration.

## Findings

| ID | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| AIC-001 | moderate | `AICU-V010-PROJECTION-001` remains: stock source-only checks require assets absent from the downstream package. | Preserve the target-owned gate; do not claim stock profiles passed. |
| AIC-002 | low | `AICU-V090-DOC-001` remains: the persistence guide names the owner-retired analyzer test project. | Preserve exact receipt bytes and carry to upstream feedback. |
| AIC-003 | moderate | `AICU-V011-SELECTION-001` remains: changed-path dependency recursion can omit dependencies. | Keep changed-path profile execution and evidence reuse inactive. |
| AIC-004 | moderate | `AICU-V012-PROFILE-REGISTRY-PROJECTION-001`: the packaged profile-registry test unconditionally reads an absent source-only profile. | Exclude it explicitly from the downstream gate and preserve exact defect evidence. |
| AIC-005 | moderate | `AICU-V012-COMMIT-CUTOVER-001`: the package cutoff would invalidate previously valid downstream commit titles. | Preserve the prospective target cutoff and do not rewrite history. |
| AIC-006 | low | `AICU-V012-COMMIT-DOC-001`: release/migration guidance omits the breaking title grammar boundary. | Carry exact documentation feedback upstream. |

The 13 rule semantics and 20 exact routes remain unchanged. The selected
profile-catalog identity advances to `8f42b3c6…`, so all 20 packets and the
effective state must be regenerated even though the dispositions do not change.

## Preserved Failed Audit

The first audit of `41a3a1dc984d84f6ebd8e0cae7f53b5a820fd984`
passed its technical gate but blocked finalization because active evidence named
nonexistent structural SHA `8fb457d972fdb3af10d2b7e5bcd000696ad35b00`
and still instructed the next agent to commit synchronization already present
in that subject. Commit `8437e178db96237edd7457bb48c531afb3bdae79`
corrected only metadata and retained both findings in the validation summary.

## Finalization Handoff

1. Advance all four CUST entries to v0.12 and verified `ASM-20260813-005`, preserving dispositions and owner reconciliation.
2. Advance provenance from exact v0.11 authority to `REL-v0.12.0` at source commit `a4fd14f0f08ad53859df1c860db0eb9643cdb2de`.
3. Preserve 13 dispositions and 20 routes; regenerate packets first and state last with recomputed authority and catalog digests.
4. Run the finalized target gate with `--require-effective-rules`; remove the working receipt only after success and rerun.
5. Do not activate profiles/reuse/provider, merge, push, close Issue/Project work, or submit upstream feedback.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260813-005/report.md`
- Stable findings: `ASM-20260813-005#AIC-001` through `#AIC-006`
- Related workflow: `2026-08-12-ai-context-v0-13-upgrade`
- Remediation performed by auditor: `no`
