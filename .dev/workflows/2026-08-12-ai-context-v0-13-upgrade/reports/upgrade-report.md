# AI Context v0.6.0 To v0.13.0 Progressive Upgrade Report

## Executive Summary

The repository's initialized AI context was upgraded through every supported
immediate predecessor:

`v0.6.0 → v0.7.0 → v0.8.0 → v0.9.0 → v0.10.0 → v0.11.0 → v0.12.0 → v0.13.0`

The final authority is `REL-v0.13.0` at upstream source commit
`8584337b47295da1af914180baf2b3f815b9dcc7`. The target has four verified
semantic customization records, thirteen explicit baseline-effective rules,
twenty exact routes and packets, and effective-rule readiness `ready`.

Every release archive and sidecar was verified; their identities, hashes, and
verification outcomes are retained under this workflow, while the downloaded
archive/sidecar bytes remain outside the repository evidence root. Payload
identity, migration contract, dry-run, apply plan, receipt, reconciliation,
failure, correction, independent audit, and provenance-transition evidence is
retained in the repository. No worktree was created before or during the
progressive route. No merge, push, Issue closure, Project mutation, provider
activation, or upstream feedback submission was performed.

Final post-upgrade developer score: **7.8/10**. Discussion-branch expectation
coverage: **47%** across the issue draft's sixteen acceptance criteria.

## Source And Target Identity

| Version | Release/source commit | Automatic source | Published ZIP SHA-256 |
| --- | --- | --- | --- |
| v0.6.0 | `8b98b5f917513f2d143f42a322050a1162bb63f9` | installed baseline | retained in prior initialization evidence |
| v0.7.0 | `49723a943f744820f4bdb2c22de7930693a7106d` | v0.6.0 | `ce817b6635f515eec9fb824d6fea89a01a6273a4a0401682dd65b38202c5adb6` |
| v0.8.0 | `97ccc9e9f218ec681bb726d2e1b4edbb3e14fb25` | v0.7.0 | `94fe4ff17222423f2fa521343e02b8a7e4709c566ea22e264f5b1b1ac3a4701c` |
| v0.9.0 | `c14a3260cba7d0a9e2b67b73df9e221280d2d2ef` | v0.8.0 | `2c98ac02eabd24ca881798caf83657adc2062ababe42fdb09fe26ce499cc98f2` |
| v0.10.0 | `5878f213b50bdbb4b3123a60525cdc206fd5be04` | v0.9.0 | `e45f88917d6a8d0db798600db414436634ba140a89590acd70a1f26bd5c1e489` |
| v0.11.0 | `05199ed0a9ed509ef1696df014fce244f8e7cffa` | v0.10.0 | `cd7010f65941cccfa2151ded2e0d7b3ef27f7a9d0bb3c5772a5b5c9855a0a10c` |
| v0.12.0 | `a4fd14f0f08ad53859df1c860db0eb9643cdb2de` | v0.11.0 | `29af751de3ab1fe7e0ac3ce838eee327bb35f53542dae8a74e09feb8a4390cf5` |
| v0.13.0 | `8584337b47295da1af914180baf2b3f815b9dcc7` | v0.12.0 | `092cd9e49de366458cafb304ca63b4c8f028b03e8cf7f718b06d8710a98efcfd` |

The upstream repository identity changed from
`ai-collaboration-prompts-dotnet-backend` to
`https://github.com/YuChia-Wei/ai-collaboration-framework.git`. Final
provenance records both the current source and exact previous source identity.

## Checkpoint Summary

| Version | Planned/applied operations | Important reconciliation | Independent audit | Final authority |
| --- | --- | --- | --- | --- |
| v0.7 | 6 safe applies + 20 reconciliations | 12 CRLF false conflicts; incoming provenance enforcement adopted with target cutoff | `ASM-20260812-001` | `REL-v0.7.0` |
| v0.8 | 24 safe applies + 43 reconciliations | directory-scoped `.codex/agents/**`; work-item binding; exact historical assessment attestation | `ASM-20260812-002` | `REL-v0.8.0` |
| v0.9 | 218 applied + 143 skipped reconciliations | 159 unchanged required paths reconciled; target gate rehomed; analyzers removed | `ASM-20260813-002` | `REL-v0.9.0`, 20 packets ready |
| v0.10 | 16 replace + 5 add | stock profiles/evidence installed but inactive; target gate repinned | `ASM-20260813-003` | `REL-v0.10.0`, 20 packets ready |
| v0.11 | 3 replace + 1 add | projection contract adopted; selector defect recorded | `ASM-20260813-004` | `REL-v0.11.0`, 20 packets ready |
| v0.12 | 73 replace + 5 remove + 2 add | prospective commit grammar cutover; profile test excluded as source-only | `ASM-20260813-005` | `REL-v0.12.0`, 20 packets ready |
| v0.13 | 80 replace + 36 remove + 15 add + 2 reconcile | PR template merged; `global.json` retained; provider removed; aggregate debt fixed | `ASM-20260813-006` plus post-finalization audit | `REL-v0.13.0`, 20 packets ready |

## v0.7.0 — Incoming Enforcement And Windows EOL

The first hop proved that package reconciliation and package validation are
different gates. The initial plan treated twenty paths as conflicts; twelve
were only CRLF/LF differences against the v0.6 base. Installed v0.6 validators
passed, but incoming v0.7 workflow validation correctly found ten missing
`model`/`reasoning_effort` fields. The target adopted incoming enforcement,
preserved a prospective execution-provenance cutoff, and corrected durable
evidence before `ASM-20260812-001` allowed finalization.

Evidence: [`01-v0.7.0-reconciliation.md`](01-v0.7.0-reconciliation.md) and
[`../evidence/v0.7.0/`](../evidence/v0.7.0/).

## v0.8.0 — Transaction Failure And Work Authorization

The first apply attempt failed at ignored `.codex/agents/context-translator.toml`
after earlier writes had occurred. No receipt was created and rollback was not
complete. Exact starting blobs were restored, the directory-level ignore
exception was authorized, and the same plan was rerun outside the sandbox.

v0.8 added required GitHub work-item binding, merge-gate metadata, Python
prerequisite/entrypoint contracts, and skill-local scripts. Two independent
audits caught a false ZIP checksum and stale resume state. A later full-range
gate found one assessment commit without its required trailer; history was not
rewritten. The owner approved one exact SHA/assessment/error attestation while
prospective validation remained strict.

Evidence: [`02-v0.8.0-reconciliation.md`](02-v0.8.0-reconciliation.md) and
[`../evidence/v0.8.0/`](../evidence/v0.8.0/).

## v0.9.0 — Effective Rules And Downstream Projection

v0.9 was the largest reconciliation. The stock planner covered 361 migration
operations, but the pending receipt additionally required exact bytes for 159
paths unchanged between v0.8 and v0.9: 127 EOL-only, two whitespace-only, and
thirty semantic target deltas. Every path was explicitly inventoried. Retained
semantics moved to target-owned authorities/tooling, while all receipt-bound
framework paths were restored to exact package bytes.

The target retired its analyzer and runtime-validation projects and kept the
incoming bundled provider source-available but inactive. Because stock package
validation referenced omitted source-only content, a version-pinned,
fail-closed target gate was created under `.dev/ai-context/tooling/**`. It
preserved the exact historical commit attestation without altering canonical
package policy bytes.

v0.9 introduced thirteen target-effective rule decisions and twenty exact
routes/packets. Independent audits caught stale target truth, ignored retired
artifacts, a premature assessment, a dead tool command, and a nonexistent
provider path before finalization.

Evidence: [`03-v0.9.0-reconciliation.md`](03-v0.9.0-reconciliation.md) and
[`../evidence/v0.9.0/`](../evidence/v0.9.0/).

## v0.10.0 — Validation Profiles And Evidence

The conflict-free 21-operation migration added `fast`, `pr`, `release`,
`closeout`, and `nightly-full` profiles; privacy-minimized JSONL evidence;
input/environment-keyed reuse; timeout/resource metadata; and new registry
tests. The stock downstream projection remained incomplete, so these features
were installed but not activated. Local validation stayed manual, CI remained
unconfigured, and reuse remained inactive.

Evidence: [`04-v0.10.0-reconciliation.md`](04-v0.10.0-reconciliation.md) and
[`../evidence/v0.10.0/`](../evidence/v0.10.0/).

## v0.11.0 — Product/Projection Boundary And Selector Defect

Four exact operations added the canonical product-source projection contract
and changed-path/evidence behavior. Static and dynamic review found that direct
matches are marked selected before recursive dependency expansion, allowing
declared dependencies to be omitted. Relevant projected tests did not cover the
new selection behavior. Changed-path execution and reuse therefore remained
inactive, while the target gate was repinned and all authority regenerated.

Evidence: [`05-v0.11.0-reconciliation.md`](05-v0.11.0-reconciliation.md) and
[`../evidence/v0.11.0/`](../evidence/v0.11.0/).

## v0.12.0 — Prospective Commit Grammar

The 80-operation migration changed commit policy schema to exactly one title
discriminator: issue references or scope. The package cutoff predated 32 valid
target commits, so literal adoption would have required unauthorized history
rewrite. The target recorded the last legacy commit and a prospective adoption
instant; new issue-only and scope-only titles pass while literal pipe titles
fail.

v0.12 also increased source-only registry declarations and shipped a profile-
registry test that reads an omitted distribution profile. The exact test is
pinned as defect evidence and excluded from the downstream target gate. A first
audit caught a nonexistent structural SHA and stale already-completed action;
the fixed metadata checkpoint passed `ASM-20260813-005`.

Evidence: [`06-v0.12.0-reconciliation.md`](06-v0.12.0-reconciliation.md) and
[`../evidence/v0.12.0/`](../evidence/v0.12.0/).

## v0.13.0 — Provider Removal, Routing, And Product Rule Gate

The package applied 131 framework operations and skipped only two acknowledged
reconciliations. `migration-0132` merged v0.13 PR delivery prompts with the
target's Issue/authorization fields. `migration-0133` retained target .NET 10
`global.json`; the framework is SDK-neutral.

Thirty-six bundled provider files were removed and six reference-only,
not-selected on-demand recipes were added. No analyzer package, project,
solution, severity, CI, or runtime wiring exists. Post-upgrade cross-analysis
found four stale target-owned statements that still described the old provider.
They were corrected at `d985e0ef24d8716481ca7dc323472cf19545103f`, guarded
by GWT012, and independently accepted at clean checkpoint
`46928f4379f57a7bec155056aacdf6dbcf070f81`.

The incoming `AGGREGATE-ES-001` construction invariant exposed pre-existing
virtual dispatch from the aggregate base constructor. The owner authorized a
bounded product correction but not rule weakening. Because live v0.13 packets
could not be authoritative before finalization, the workflow consumed the same
fresh rule through finalized v0.12 packets, implemented and tested the narrow
fix, cherry-picked it to v0.13, and then resolved both fresh v0.13 packets after
finalization. Domain tests passed 13/13 on both branches and the recorded full
solution build had zero errors.

The finalizer retained the working receipt, advanced all four CUST records and
provenance, wrote twenty packets before ready state, ran the complete gate,
resolved both exact local-change packets, removed only the working receipt, and
ran the gate again. The durable receipt remains at SHA-256
`094840edc10744c12397a905e1783f8200a498081a492d5fae0f13f41b979ec0`.

Evidence: [`07-v0.13.0-reconciliation.md`](07-v0.13.0-reconciliation.md) and
[`../evidence/v0.13.0/`](../evidence/v0.13.0/).

## Final Target Configuration

- Components: `software-development-core`, `ai-context-lifecycle-core`.
- Technology profile: `dotnet-backend`.
- Provenance provider: `repo-backlog`, enabled.
- Work management: GitHub; binding and merge gate required.
- Local routine validation: `manual`.
- CI routine validation: `unconfigured`.
- Stock validation profiles: inactive.
- Changed-path selection: inactive.
- Validation evidence reuse: inactive.
- Target analyzers/runtime validators: retired and absent.
- Bundled provider: removed.
- On-demand mechanical-validation recipes: reference-only, not selected.
- Test style: plain xUnit with Given/When/Then organization.
- SDK: target-owned .NET `10.0.302` retained.

## Final Validation

- Finalized AI-context target validation: passed; readiness `ready`.
- Customizations: four finalized and verified.
- Effective rules: thirteen dispositions.
- Routing: twenty unique wildcard-free routes and twenty packets.
- Target overlay: 41/41 passed.
- Provider truth regression: 12/12 focused projection tests passed.
- Commit policy: 56 commits passed at the last pre-analysis checkpoint.
- Product validation: 13/13 domain tests on both applicable checkpoints; full
  solution build evidence reports zero errors.
- Independent audit: `46928f4` returned `SAFE-TO-PROCEED`; two Windows symlink
  cases were privilege-skipped and no audit residue remained.
- Stock validator: intentionally not claimed passed; exact v0.13 execution
  reports 36 downstream projection errors.
- Stock routing test: intentionally not claimed passed; it imports omitted
  source-only `ai_context_package.py`.

## Failures And Corrections Preserved

The evidence intentionally retains failed attempts rather than rewriting them:

- CRLF raw-hash false conflicts and predecessor-validator false positives.
- v0.8 non-transactional partial apply and sandbox permission failure.
- Wrong v0.8 ZIP checksum and stale resume metadata.
- Missing assessment trailer with exact history-preserving attestation.
- v0.9 unchanged-required-path planner gap, source-projection defects, stale
  target truth, ignored retired artifacts, premature assessment, dead command,
  and nonexistent provider root.
- Windows executable-mode, Temp ACL, symlink, Git Bash signal-pipe, and Python
  bytecode/fixture hygiene friction.
- v0.12 nonexistent structural SHA and stale completed-action instruction.
- v0.13 pre-finalization packet bootstrap gap, aggregate compliance debt, stale
  provider truth, and one blocked remediation audit caused by stale resume text.

## Post-Upgrade Deliverables

- Developer impact and score:
  [`08-developer-impact-and-score.md`](08-developer-impact-and-score.md)
- Discussion-branch comparison:
  [`09-discussion-branch-comparison.md`](09-discussion-branch-comparison.md)
- Upstream feedback brief:
  [`upstream-feedback-brief.md`](upstream-feedback-brief.md)
- Initial post-upgrade assessment `ASM-20260813-007` was content-audit blocked
  and remains byte-preserved as superseded evidence. Complete successor
  `ASM-20260813-008` passed independent closeout audit at `d770885...`.

## Authorization Boundary

The upgrade and local evidence are complete. This report does not authorize
merge, push, Issue closure, Project mutation, CI/profile/reuse/provider
activation, Architecture Kit adoption, or upstream feedback submission.
