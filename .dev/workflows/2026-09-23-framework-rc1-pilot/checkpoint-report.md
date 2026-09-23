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
