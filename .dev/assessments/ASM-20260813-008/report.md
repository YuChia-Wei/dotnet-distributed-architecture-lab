# AI Context Audit Report

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260813-008`
- `assessment_type`: `ai-context-verification`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-13`
- `created_at`: `2026-08-13T14:08:36+08:00`
- `updated_at`: `2026-08-13T14:08:36+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `dotnet-mq-arch-lab`
- `subject_branch`: `codex/2026-08-12-ai-context-v0-13-upgrade`
- `subject_commit`: `d97d8e8488bb8a87116f7d9f9b9089e1c2ed9010`
- `previous_assessment`: `.dev/assessments/ASM-20260813-007/report.md`
- `workflow_refs`: `2026-08-12-ai-context-v0-13-upgrade`
- Analysis model: `gpt-5.6-sol`, reasoning effort `max`

## Executive Summary

- Overall assessment: finalized v0.13 is action-ready and materially safer than
  the v0.6 baseline, with bounded target mitigations and significant upstream
  package and lifecycle follow-ups.
- Overall score: **7.8/10**.
- Decision: `healthy-with-followups`.
- Primary strengths: fail-closed authority and receipts; exact predecessor
  evidence; explicit authorization boundaries; digest-bound effective rules;
  provider-neutral routing; independent fixed-commit audits.
- Primary risks: stock downstream validation is not package-closed; changed-
  path dependency traversal is defective; pre-finalization remediation lacks
  an incoming-authority packet; current routing remains broader than task-
  minimal; only 47% of the discussion branch's sixteen expectations is met.

The assessment supersedes `ASM-20260813-007`, whose final report remains
unchanged as evidence of a content-audit-blocked checkpoint. Three independent
content re-audits accepted the corrected clean subject commit. No owner decision
is required for current v0.13 operation; activation, Architecture Kit adoption,
integration, publication, and upstream submission remain separate decisions.

## Scope

### Included AI Context Surfaces

- Finalized provenance, four CUST records, thirteen rule dispositions, twenty
  exact routes and packets, and ready effective-rule state.
- Root collaboration and target-truth entries, `.ai/**`, `.dev/**`, runtime
  wrappers, target validation overlay, upgrade workflow, reports, and evidence.
- Developer impact, changed operating rules and details, progressive migration
  behavior, active/resolved defects, and the prepared upstream feedback brief.
- Discussion branch `codex/2026-07-30-ai-context-architecture-kit-standards-discussion`
  at `b29ef357d7c6c7cb202d11896466a039e1e17483`.

### Default Exclusions

- `src/**`
- `tests/**`, `test/**`
- product implementation trees
- generated and dependency trees

### Additional Exclusions

- General product code review; only the separately authorized and already
  validated `AGGREGATE-ES-001` remediation evidence was read.
- Merge, push, Issue closure, Project mutation, provider or validation-profile
  activation, Architecture Kit adoption, and upstream submission.
- Online package currency and vulnerability claims.

### Code Review Handoff

- Requested: `no`
- Paths not scanned: general `src/**` and `tests/**` implementation surfaces.
- Recommended skill: `code-reviewer` for any later .NET implementation review.

## Methodology And Evidence

### Pass A: Independent Baseline

- Evidence used: exact package identities and receipts for v0.7 through v0.13,
  finalized target authorities, per-version validation summaries, Git history,
  discussion-branch records, and corrected reports at the fixed subject commit.
- Checks performed: package/target fact separation; arithmetic and denominator
  reproduction; decision-supersession reconstruction; defect-count and priority
  recount; evidence-path resolution; active versus inactive behavior review;
  fixed-HEAD cleanliness and full target-gate read-back.

### Pass B: Repository-Aware Skill Review

- Policies and skills used: `ai-context-auditor`, `ai-context-governance`,
  `ai-context-upgrader`, Assessment Artifact Policy, workflow/commit policies,
  effective-rule contracts, target project configuration, and root routing.
- Checks performed: canonical versus target-owned authority; four-CUST semantic
  preservation; wrapper/routing consistency; authorization/stop boundaries;
  stock-versus-target validation classification; provider-removal truth; and
  immutable-assessment successor lifecycle.

### Delegation

- Sub-agents used: `yes`; three independent `gpt-5.6-sol` agents at `max`.
- Assigned surfaces: developer impact and assessment contract; the discussion
  branch's sixteen acceptance criteria and DEC relationships; upstream feedback
  facts, priorities, evidence links, and publication boundary.

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| Git history, trees, and diffs | `d97d8e8488bb8a87116f7d9f9b9089e1c2ed9010`; discussion `b29ef357...` | fixed and clean | workflow, assessment, AI-context and discussion surfaces | semantic compliance is not inferred from ancestry | direct report, policy, catalog, and evidence reads |
| Target AI-context gate | finalized REL-v0.13.0 authority | passed outside sandbox over 59 commits | target-applicable checks; stock package projection separately blocked | does not prove stock source-only closure or online currency | exact command output and defect manifest |
| Structured artifact validators | assessment/workflow schemas at subject | passed | schema, indexes, timestamps, paths | prose truth and evidence quality require independent audit | manual cross-file content comparison |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Root entries | 11 files | humans and agents | identity, routing, SDK/product truth | synchronized | English canonical guide plus zh-TW translation; no provider activation claim |
| `.ai/**` | 510 files | reusable agent runtime | canonical framework payload | finalized v0.13 | receipt-governed bytes; stock source projection remains incomplete |
| `.dev/**` | 362 files | target governance and humans | target truth, authorities, workflows, reports | active | four CUST records, ready state, complete progressive evidence |
| Runtime wrappers | 37 files | Codex and Claude runtimes | thin skill loading/routing | synchronized | canonical skills plus two compatibility aliases |

## Strengths

1. Exact-predecessor planning, receipts, durable checkpoints, and independent
   audits make failures observable and recoverable without rewriting history.
2. Provenance, CUST records, catalogs, effective state, and packets are digest-
   bound and fail closed on stale or unknown authority.
3. Work-item authorization, execution, merge, push, release, Issue closure, and
   publication are treated as distinct permissions.
4. Provider and analyzer state is honest: the bundled provider is removed, six
   recipes are reference-only and not selected, and no wiring or activation is
   inferred from file presence.
5. Target validation does not relabel broken stock projection as success; its
   SHA-pinned overlay and negative tests retain exact upstream defect evidence.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIC-001 | HIGH | `AICU-V010-PROJECTION-001`: the published downstream payload is not closed over its declared stock validation surface. | `reports/upstream-feedback-brief.md`; v0.13 validation summary; target gate manifest | Stock validation exits nonzero with 36 projection errors, so target consumers need a version-pinned overlay. | Close all packaged runtime references and test isolated downstream payloads. | Upstream framework maintainer; `ai-context-governance` retains mitigation. |
| AIC-002 | HIGH | `AICU-V011-SELECTION-001`: changed-path direct matches can bypass dependency expansion. | `reports/05-v0.11.0-reconciliation.md`; target gate manifest | Authoritative partial validation could omit required checks. | Traverse dependencies before marking checks selected and add transitive/cycle tests. | Upstream framework maintainer. |
| AIC-003 | MEDIUM | `AICU-V012-PROFILE-REGISTRY-PROJECTION-001`: a packaged test reads an omitted source-only profile. | `reports/06-v0.12.0-reconciliation.md`; feedback brief | Downstream profile-registry validation is not hermetic. | Package a fixture or mark and exclude the source-only case explicitly. | Upstream framework maintainer. |
| AIC-004 | MEDIUM | `AICU-V012-COMMIT-CUTOVER-001` and `...DOC-001` use a source-time title boundary without a complete target migration contract. | v0.12 evidence and target commit-policy overlay | Literal adoption would reject 32 valid target commits or pressure history rewrite. | Make cutovers target-prospective and document legacy/new grammar and no-rewrite handling. | Upstream framework maintainer; target overlay retained. |
| AIC-005 | MEDIUM | `AICU-V013-ROUTING-PROJECTION-001`: the portable routing test imports omitted source-only code. | v0.13 reconciliation; feedback brief | The stock test aborts before its portable GWT cases. | Make GWT1-7 dependency-closed and classify the source-release-only case without importing omitted code. | Upstream framework maintainer. |
| AIC-006 | LOW | `AICU-V013-COMPONENT-OWNERSHIP-001`: portable and package metadata disagree on one shared policy owner. | v0.13 preflight and feedback brief | Optional component selection could become inconsistent even though both are mandatory here. | Generate ownership projections from one source and test optional selections. | Upstream framework maintainer. |
| AIC-007 | HIGH | `AICU-V013-PREACTION-PACKET-BOOTSTRAP-001`: no live incoming packet can govern required remediation before finalization. | v0.13 preaction analysis and remediation evidence | Upgrade finalization and governed product remediation can become circular. | Define a receipt/HEAD/owner-bound, narrow, non-activating candidate-packet contract. | Upstream framework maintainer; `ai-context-upgrader`. |
| AIC-008 | MEDIUM | All twenty current routes load the same thirteen rules. | `.dev/ai-context/effective-rules.yaml`; report 09 | Safe routing is broader and more expensive than task-minimal projection. | Add evidence-backed selectors and explicit not-applicable subsets without defaults. | `ai-context-governance`; owner decision if semantics narrow. |
| AIC-009 | MEDIUM | Only 47% of the discussion branch's exact sixteen expectations is achieved or partially achieved; its readiness-gated Architecture Kit transition is contradicted. | `reports/09-discussion-branch-comparison.md` | The installed system does not yet meet the proposed identity/constraint/compatibility/provider architecture. | Decide separately whether to implement or explicitly supersede the Architecture Kit direction. | Repository owner; future governance workflow. |
| AIC-010 | LOW | Repository-local Python fixtures can survive suppressed cleanup failures; two receipt-bound package EOF blanks remain. | feedback brief; full-range `git diff --check` evidence | Windows runs can leave unreadable ignored residue and package deltas retain hygiene noise. | Use an external temp root, fail cleanup visibly, and lint full package deltas before release. | Upstream framework maintainer. |

## Baseline And Skill Comparison

### Confirmed

- The 7.8/10 developer-impact score and six-dimension arithmetic are supported
  by explicit qualitative anchors and retained evidence.
- Finalized v0.13 authority is ready; four CUST records, thirteen dispositions,
  twenty exact routes, and twenty packets are mutually consistent.
- Seventeen upstream feedback findings remain reproducible (`P0=6`, `P1=6`,
  `P2=5`), and the brief remains prepared but unsubmitted.

### Added By Repository-Aware Review

- The discussion denominator is exactly sixteen Issue-draft checkboxes, and the
  reproduced result is 3 achieved, 9 partial, 3 not achieved, 1 contradicted:
  `7.5 / 16 = 46.875%`, rounded to **47%**.
- `DEC-003` remains active; the exact partial supersessions for `DEC-012`,
  `DEC-014`, `DEC-027`, and `DEC-037` are preserved.
- Package omission is 18/18 source-only entrypoints; target absence is 17/18
  because the exact compare helper remains available.

### Downgraded Or Deferred

- Architecture Kit adoption, provider/recipe activation, CI/profile/reuse
  activation, and narrower rule selection remain owner decisions outside this
  upgrade.
- Online package currency and vulnerability status remain advisory and were not
  asserted by the offline gate.

### Overturned

- `ASM-20260813-007` is not authoritative for closeout; it is superseded while
  its frozen report remains as failed content-audit evidence.
- Discussion item 5 is partial, not achieved, because constraints are empty and
  eleven baseline documents remain unpacketized.
- Stock validation is blocked by package projection, not generally inapplicable
  and not passed.
- Workflow evidence retains archive identities, hashes, and results, not the
  archive and sidecar bytes themselves.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state | passed | exact clean subject `d97d8e8488bb8a87116f7d9f9b9089e1c2ed9010` on the workflow branch |
| Registry and wrapper parity | passed | target gate and 41/41 target overlay tests; two Windows symlink privilege cases skipped |
| Path and reference checks | passed | all report links resolved; provider paths/absence and six recipe files cross-checked |
| Schema / structured file parse | passed | assessment, workflow, target-context, dependency, and shell validators passed |
| Repository context checks | passed | readiness `ready`; four CUST; 13 dispositions; 20 routes/packets; provider inactive |
| Commit policy | passed | target validator accepted all 59 first-parent commits at the subject checkpoint |
| Discussion comparison | passed | exact 16 rows; 3/9/3/1; 46.875% rounded to 47%; DEC relationships re-read |
| Upstream feedback | passed | 17 findings, priorities 6/6/5, exact package/target counts, no submission |

### Skipped Validation

- Stock full downstream validation was not skipped as success: its exact
  nonzero 36-error package-projection result is retained as a blocking finding.
- Two symlink-boundary cases were skipped because Windows lacked the privilege;
  all non-symlink resolver cases passed.
- General product source/test review and online dependency currency were outside
  scope. Product remediation relies on its separate tests, build, and audit.

## Recommended Action Order

1. Keep the target-owned gate authoritative and stock profiles, changed-path
   execution, evidence reuse, CI, analyzers, provider, and recipes inactive.
2. Fix downstream package closure and unchanged-managed-path planning upstream.
3. Fix changed-path dependency traversal and add projected regression coverage.
4. Define durable apply recovery and governed pre-finalization candidate packets.
5. Make policy cutovers target-prospective and strengthen evidence/resume checks.
6. Decide Architecture Kit direction separately with version range, mapping,
   parity, consumer proof, and readiness-gated opt-in if adoption is chosen.
7. Make Windows temp/cleanup and package whitespace validation hermetic.

## Deferred Items

- Architecture Kit adoption or explicit supersession of the prior proposal.
- CI/profile/evidence-reuse/provider/recipe activation.
- Upstream Issue or PR submission of the prepared feedback brief.
- Merge, push, Issue closure, Project mutation, release, and publication.

## Appendix

### Commands Run

```text
python -B .dev/ai-context/tooling/validate-target-ai-context.py --require-effective-rules --commit-range main..HEAD --workflow-id 2026-08-12-ai-context-v0-13-upgrade
python -B .ai/scripts/validate-assessment-artifacts.py
python -B .ai/scripts/validate-workflow-artifacts.py
python -B .ai/scripts/validate-ai-context-target.py --require-effective-rules
git diff --check
git status --porcelain=v2 --branch
```

### Notes

- Complete target gates ran outside the sandbox because Windows Temp ACLs can
  produce known environment-only failures inside it.
- Archive and sidecar identities, hashes, and verification outcomes are durable
  repository evidence; their original bytes remain outside the repository.
- The discussion branch was compared, not merged, and is not an ancestor of the
  upgrade branch.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260813-008/report.md`
- Stable finding references: `ASM-20260813-008#AIC-001` through `#AIC-010`
- Remediation owner: `ai-context-governance` for target mitigation and upstream
  framework maintainers for package defects.
- Related remediation workflow: `2026-08-12-ai-context-v0-13-upgrade`
- Verification assessment: `ASM-20260813-008`
- Remediation intentionally not performed by this skill: `yes`
