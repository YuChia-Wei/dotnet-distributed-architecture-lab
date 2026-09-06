# v0.16.0 corrective terminal audit criteria

Owning skill: `ai-context-auditor`, coordinated by `ai-context-governance`.
Canonical role: `.ai/assets/sub-agent-role-prompts/fixed-head-independent-auditor/sub-agent.yaml`.
Selection: explicit terminal post-remediation and local integration gate.
Owner authorization: `closeout-correction-authorization.yaml` in this directory.

## Subject and independence

The parent supplies one full fixed clean execution commit and its entire Git
tree ID. No tracked path is excluded from the content subject. The auditor
must not have implemented this repair and must not mutate the reviewed tree.
Return failed or blocked on checkout drift, missing evidence, timeout or
authority mismatch. Do not repair as part of this audit.

## Acceptance criteria

1. Original upgrade reports, old delegation-run.yaml, provenance,
   customizations, effective-rules and packets retain the bytes from
   `0a3fac7ce225802983249fcdb576cdf8ef40738e`. The finalized transaction is not
   reapplied, reopened, rewritten or rolled back.
2. Current workflow state and correction reports disclose the historical
   pre-finalization evidence gap. They do not claim the old pending run passed
   or that a present-day audit retroactively happened before finalization.
3. The target-owned gate enforces explicit terminal_audit declarations. An
   active pending correction is not completion. A completed workflow needs
   genuine retained passed evidence with matching subject and file hashes.
4. Focused tests cover pending completion, missing evidence, failed outcome,
   subject mismatch, unsafe paths, authority drift and full-tree drift.
   The target gate includes the new check; excluded source-only checks and
   product tests are not mislabeled as passed.
5. Historical retained audit validation is distinct from current integration
   admission. Admission requires a clean current checkout and the exact
   reviewed commit or identical complete tree for a SHA-only merge/history
   change; no broad evidence-only exclusion permits new unaudited content.
6. The baseline, corrective report and later verification remain separate.
   Final reports are not silently rewritten. Deferred upstream proposals have
   an owner, reason and next action rather than an implementation claim.
7. Local integration is authorized, Issue #9 remains separate, and no push,
   PR, Issue closure, package publication or product change is included.

## Required returned evidence

Return actual start/end times, runtime child identity, exact subject commit and
tree, criteria hash, canonical role hash, result, findings and commands/results.
Record skipped checks honestly. An audit outcome is evidence, not integration
authorization. A post-remediation assessment may be captured after the reviewed
commit; a subsequent content-bearing commit requires a fresh terminal audit.
