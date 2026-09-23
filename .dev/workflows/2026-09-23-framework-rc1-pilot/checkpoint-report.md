# Current repaired candidate checkpoint

Source PR #388 merged the original #335 repair. A new immutable rc.1 candidate
was actually built/read from 1ce41a4f03f61e83bf9b99de3ce196887547e922, then
installed through an exact-lock delta plan: two PR files changed, 129 unchanged.
All 131 installed member hashes matched. Seventy-two protected inputs, 292 retained
authority files and the five existing local pilot records remained unchanged.
The actual installed PR prepare/inspect/render retry passed and created one local
prepared record bound only to the first three preparation commits. No target
provider action occurred. The new installer lock is a04e2df01f5f6df6889b7c09daa1b9ae1c78e6b503aac852d5aa2b325c56a0e8.

Binding is now pilot-review: final byte/mode parity passed; the frozen selected
gate and independent admission remain pending. See evidence/repaired-candidate-update.json.
Earlier checkpoints below describe their historical observations and remain
preserved with their raw failure evidence; they are not the current blocker state.

# Local complete rc.1 pilot checkpoint

The managed install and target integration are prepared, but **activation is
blocked by the actual PR package failure and independent review remains pending**.
Do not treat the earlier selected gate pass as whole-project readiness.

Actual evidence:
- 18 packages / 131 managed members installed with exact engine 3afb4ff4207acb3e12e3953018736305a439ed21.
- 132 candidate/index/fresh-checkout byte and mode comparisons passed.
- 13 installed explain/query calls passed before draft records were introduced.
- Five local record creates and ten read/validate/render/resume calls passed:
  Lesson candidate, ADR draft, local backlog draft, supporting planned workflow,
  and proposed CBF structural snapshot. None asserts owner acceptance.
- PR prepare failed without record mutation. Exact sanitized Git isolation found
  --worktree configuration unsupported with multiple worktrees and disabled
  worktreeConfig. Original source Issue 335/task resumed; no target setting changed.
- Promotion proposal is not executed: the target selected no concrete policy
  target/source roots. Existing explain/query is read capability only.
- Fourteen focused gate regressions passed. Working-content selected gate passed
  in 25.073 seconds before the PR failure was discovered; its Git range covered
  three existing preparation commits only. Final frozen-subject check is pending.

All original failures remain: first installation scan-limit and durable objects,
unowned-control plan/guard reconciliation, first target gate Windows metadata
failure, and current PR prepare. Source repair or a later successful retry cannot
erase them. Record summaries bind raw ignored receipts and results.

Current target roots select the new Codex packages with 14 retained .NET rules,
four customizations and 20 exact selectors. Runtime discovery has 18 generated
Codex entries plus two legacy duties; Claude has only two legacy duties and no
new-framework support. 26 replaced directories/29 original files plus four
original lifecycle entries are preserved in exact history.

Next: review/integrate original Issue 335 repair; build a new immutable unpublished
rc.1 candidate; perform an explicit managed delta update using the verified engine
and existing actual lock; repeat only affected PR/managed-byte checks. Preserve
five pilot records and all target customizations. Then freeze the complete target
subject for independent review and terminal admission. Target provider integration,
Issue closure, stable upgrade and publication remain separate.

Navigation correction: both retained upgrader wrappers now explicitly mark
the optional source Git-tree comparison helper as unavailable in this target.
The same missing path was already referenced at the baseline commit. The
retained playbook permits package inventories and recorded base identity;
no replacement tool or successful legacy upgrade execution is asserted.
Archived original wrapper bytes remain exact and active wrapper hashes were
refreshed. This does not change the current PR blocker or admission state.

Review preparation clarification: P15-10 now distinguishes the independent
reviewer's evidence from subsequent parent admission and lease release. The
content-subject descriptor keys and byte encoding are explicit before freeze.
This removes an impossible future-action claim; all independent review and
parent release requirements remain mandatory and unexecuted at this checkpoint.

Repaired candidate Git parity: all 131 managed members plus the actual new lock
match candidate/current bytes, staged Git blobs, declared modes and a fresh
selected index checkout. Six raw-byte attributes are unset for all 132 paths.
See evidence/repaired-git-byte-parity.json. No full repository checkout or
independent admission was performed by this parity check.
