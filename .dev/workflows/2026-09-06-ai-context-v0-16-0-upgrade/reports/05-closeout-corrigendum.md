# v0.16.0 Closeout Corrigendum

- Created: `2026-09-07T07:12:53+08:00`.
- Updated: `2026-09-07T07:28:13+08:00`.
- Owner: `ai-context-governance`.
- Workflow: `2026-09-06-ai-context-v0-16-0-upgrade`.
- Corrected snapshot: `0a3fac7ce225802983249fcdb576cdf8ef40738e`.
- Baseline assessment: `ASM-20260907-001`.
- Status: corrective content complete; actual independent verification retained
  as `ASM-20260907-002`. Final integration admission remains a separate gate.

## Explicit correction

The original reports and `ASM-20260906-001/report.md` remain immutable historical
observations. Their independent-audit and safe-to-close claims are not sufficient
terminal evidence: the old delegation record remains required/pending, has no
subject or evidence, and contains four unsupported/incomplete schema selections.
The stock target gate did not check that run instance. Passing its 34 tests and
package/authority checks did not satisfy the missing terminal audit.

The finalized checkpoint already contained a `verified` reference to
`ASM-20260906-001`, but did not contain that assessment. The retained assessment
was created later and reviewed the finalized checkpoint. A new audit can verify
current installation integrity; it cannot prove a pre-finalization review
occurred. This historical sequence remains an explicitly disclosed limitation.

Do not change sealed ledger/provenance bytes to make a later assessment look like
the original prerequisite. Preserve the finalized transaction and add current
governance evidence separately. The prior workflow completion was premature;
the locator was explicitly reopened for `AICU-004-closeout-evidence-correction`
and completed only after the separate current verification was retained.

## Other clarified claims

- Target pins changed within a sealed transaction and raw-versus-canonical
  digest mistakes were execution errors. Earlier preflight/helper improvements
  can prevent recurrence, but these are not proven v0.16 engine regressions.
- Subject-before-paths ordering predates v0.16. Do not infer a new restriction
  merely because this attempt encountered it.
- Twenty-four missing source-only registry paths do not by themselves prove a
  packaging defect. The target overlay remains the applicable gate; precise
  upstream consumer applicability is a separate investigation.
- The `8.6/10` score has no reproducible rubric. It is not a release KPI.
- The original finalization time and two-minute clean-path statements are
  estimates, not a complete phase-timing benchmark. The observed workflow
  creation-to-closeout-commit interval was 81 minutes 04 seconds.
- The old plan's `23:13:50` finalized-subject row is not the Git committer time;
  `c0abe9c` was committed at `23:16:50+08:00`.
- Pending-receipt removal retained sufficient terminal validation identity;
  byte-exact recreation of the deleted original was not demonstrated. No
  additional evidence is deleted by this correction.
- Finalization provides in-process rollback, not cross-file crash atomicity.

## Correction and validation boundary

Add a target-owned declared-terminal gate, keep historical incomplete evidence
hash-pinned, and obtain actual independent verification on a clean repair
checkpoint. Persist its report separately. Then audit the final clean
integration head and retain current-head validation outside the tracked subject,
so evidence recording does not create an endless self-referential commit cycle.

Current runtime admission requires the complete reviewed Git tree; it does not
reuse an old audit after an evidence-only content change. A no-ff merge may be
accepted only after exact tree comparison and post-merge target validation.

Unchanged package apply and product surfaces do not need another upgrade or
product test run. Run focused new gate tests and affected target validation.
Upstream serializer/orchestration/performance/resume improvements remain outside
this local correction, owned by the framework maintainer for separate scoping.

## Current corrective outcome

The fresh independent reviewer `/root/repair_audit` passed repair commit
`c53dc84050685761b801bb992fae6101828b01e2` on `2026-09-07`, preserving all 29
selected historical/authority files byte-for-byte. The target gate passed all
52 tests and seven commits; the exact command, timestamps, exit code, output
digest and genuine invocation are retained under `ASM-20260907-002/evidence/`.
No new blocking finding was identified. The old assessment locator is now
reciprocally superseded; its frozen report and the pending old run are unchanged.

This repairs the present-day evidence and acceptance path, not the missing
historical prerequisite. The final containing commit still needs a fresh
independent audit and exact full-tree admission before local integration.
