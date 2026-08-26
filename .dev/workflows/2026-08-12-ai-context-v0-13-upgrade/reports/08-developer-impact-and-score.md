# v0.13 Post-Upgrade Developer Impact And Score

## Assessment Basis

- Installed authority: `REL-v0.13.0`, source commit
  `8584337b47295da1af914180baf2b3f815b9dcc7`.
- Audited target checkpoint:
  `46928f4379f57a7bec155056aacdf6dbcf070f81`.
- Analysis model: `gpt-5.6-sol`, reasoning effort `max`.
- Final technical audit: `SAFE-TO-PROCEED`; complete target gate passed outside
  the sandbox over 56 commits, with 41/41 target-overlay tests and two
  Windows-symlink privilege skips.
- Scope: AI collaboration context, workflow/governance, package behavior,
  validation, routing, effective rules, sub-agent/external-task contracts, and
  target settings. Product code was not generally reviewed; only the separately
  authorized `AGGREGATE-ES-001` remediation evidence is included.

## Verdict

The installed v0.13 context is **healthy with material follow-ups: 7.8/10**.
It is substantially safer and more auditable than the v0.6 baseline. The main
cost is operational: downstream validation still needs a target-owned overlay,
the exact-predecessor route produced many checkpoints, and current rule packets
are correct but broader than truly task-minimal context.

## Weighted Score

The six subscores are an evidence-weighted **qualitative judgment**, not an
empirical benchmark. To make later reassessment consistent, each dimension uses
these anchors: `10` = native, complete, low-friction behavior with no material
mitigation; `8` = reliable behavior with bounded, documented mitigation; `6` =
usable but recurring manual or target-specific work; `4` = common work is
blocked or routinely unsafe; `0` = absent or unusable. Intermediate decimals
reflect the evidence in the rationale column. The weighted arithmetic is exact;
the judgment inputs remain subject to reviewer calibration.

| Dimension | Weight | Score | Weighted result | Rationale |
| --- | ---: | ---: | ---: | --- |
| Safety | 25% | 9.2 | 2.30 | Fail-closed receipts, authority digests, explicit approval boundaries, independent audits, and packet freshness are strong. |
| Clarity | 15% | 7.5 | 1.13 | Canonical/target ownership is much clearer, but package projection and policy cutover exceptions remain complex. |
| Developer ergonomics | 15% | 6.6 | 0.99 | Direct mode and routing improved; repeated checkpoints, overlays, and Windows-specific friction remain costly. |
| Portability | 15% | 7.2 | 1.08 | Provider-neutral contracts and SDK-free recipes help, but the stock downstream package is not self-validating. |
| Validation reliability | 20% | 8.3 | 1.66 | Target gates and negative tests are strong; stock projection, changed-path selection, and fixture cleanup remain defective. |
| Upgradeability / maintainability | 10% | 6.7 | 0.67 | Exact evidence is excellent, but seven mandatory hops and several metadata-only audit cycles are expensive. |
| **Total** | **100%** |  | **7.83 → 7.8/10** | |

## What Improved

1. **Authorization and stop boundaries are explicit.** GitHub work-item binding
   provides traceability and work authorization, but does not imply merge,
   push, release, Issue closure, or publication permission. Missing receipts,
   stale rule state, unverified audits, or unresolved semantic decisions stop
   the applicable action.
2. **Workflow use is proportional.** Small coherent changes may remain direct;
   durable multi-stage work receives a branch-first locator, exact task state,
   validation evidence, and resumable checkpoints. Workflow completion remains
   separate from integration and publication.
3. **Target authority is machine-checkable.** Provenance identifies the exact
   release and source commit. Four versioned CUST records preserve target
   governance, validation, repository truth, and execution-provenance deltas.
4. **Effective rules fail closed.** Thirteen explicit baseline dispositions and
   twenty wildcard-free routes publish digest-bound packets. Missing, stale, or
   unrecognized routes cannot silently fall back to broad document scanning.
5. **Role execution is provider-neutral.** Direct execution is the default;
   sub-agent delegation requires bounded scope, capability match, material
   value, acceptable cost/risk, and actual invocation evidence.
6. **Code-review context is more selective.** v0.13 routes review references by
   scope, type hierarchy, path, and fallback instead of always loading a broad
   duplicated checklist.
7. **Analyzer/provider activation is honest.** Target-owned analyzer projects
   were retired. v0.13 removed the bundled provider and leaves only six
   reference-only, `not-selected` on-demand recipe assets. File presence does
   not imply package, build, CI, or runtime activation.
8. **Independent audit has real authority.** Audits stopped false checksum,
   stale resume, nonexistent SHA/path, dirty-tree, and premature-finalization
   claims. Failed findings remain preserved instead of being relabeled after a
   later success.

## Changed Operating Rules And Details

| Area | Effective v0.13 behavior | Developer consequence |
| --- | --- | --- |
| Authorization | Required work-item binding gates governed execution. The independently required merge gate gates integration; merge, push, and release remain separate decisions. | Record the online work item before mutation. Do not treat the Issue as merge authority or the merge gate as execution authority. |
| Workflow | Direct, assessment, and workflow modes are distinct; workflow artifacts need branch, timestamps, exact resume state, and a clean checkpoint. | Use workflow mode only when resumability or approval state is material; keep active `next_action` truthful after every commit. |
| Commit titles | Prospective titles use one discriminator: `type(#1)` or `type(scope)`, never literal `|`. | Existing history is preserved by a target cutover; new commits must use the new grammar. |
| Commit bodies | Workflow commits require `Why`, `What`, `Validation`, and `Workflow`; assessment commits require the matching `Assessment-Id`; AI trailers preserve model/reasoning labels. | A technically correct commit can still fail the governance gate if evidence trailers are incomplete. |
| Assessments | Conversation-only analysis writes nothing; durable audits use immutable `ASM-YYYYMMDD-NNN`, stable findings, exact subject refs, and no remediation authority. | Auditors report and stop; governance/implementation owners perform approved fixes. |
| Validation profiles | `fast`, `pr`, `release`, `closeout`, and `nightly-full` plus JSONL evidence/reuse metadata are installed. | They remain inactive here because the stock projection and selector are not reliable downstream. |
| Local/CI settings | Local routine validation is `manual`; CI is `unconfigured`; evidence reuse is inactive. | Run the target-owned gate explicitly. A future CI mode requires a separate owner decision. |
| Skills | Sixteen canonical skills remain; fourteen active skills plus thin `dev-workflow` and `repo-structure-sync` compatibility aliases. | New work routes to canonical `software-development-orchestrator` and `ai-context-init`; historical ownership is not rewritten. |
| Sub-agents | Delegation is optional, bounded, and evidence-backed; direct execution remains preferred when sufficient. | Do not spawn agents merely for parallelism; preserve exact ownership and completion evidence when delegated. |
| External tasks | Long validation uses pinned clean commits, exact argv, terminal-only completion, one schema-valid report, ignored artifacts, and no polling/repair/secrets. | A callback or late log is not success without the final validated receipt. |
| Effective rules | Every action route must resolve a fresh packet before governed implementation. | Stale provenance, ledger, catalog, state, or packet digest blocks mutation. |
| Package upgrade | Planner output is a proposal; the required-path receipt is the stronger postcondition. | Review all reconciliations, retain receipts, and validate with incoming plus target-applicable gates. |
| Provider/recipes | Bundled provider is removed; on-demand recipes are reference-only and not selected. | Do not add analyzer packages, project wiring, severity, CI, or runtime integration without a new explicit decision. |

## Release-By-Release Behavioral Change

| Version | Material change |
| --- | --- |
| v0.7 | Added task `model`/`reasoning_effort`, stronger handoff/outcome contracts, AI commit trailers, and a fourth execution-provenance CUST. |
| v0.8 | Added required GitHub work-item binding/merge gate, Python prerequisite and entrypoint registries, skill-local scripts, and validation activation policy. |
| v0.9 | Added engineering identities/catalogs, effective state and packets, provider-neutral role execution, target technology decisions, and the SHA-pinned target validation overlay. |
| v0.10 | Added named validation profiles, retained logs, privacy-minimized JSONL evidence, reuse-by-input metadata, and timeout/resource/environment records. |
| v0.11 | Added the canonical-product/projection boundary, changed-path selection, and validation evidence schema 2.0; the dependency-expansion defect prevents activation. |
| v0.12 | Changed commit grammar to issue-only or scope-only, added lessons/file-disposition checks, and introduced the profile-registry projection defect. |
| v0.13 | Added portable target-version policy, compact code-review routing, exact external-task envelopes, bundled-provider removal, SDK-free recipes, and updated aggregate rule ownership language. |

## Current Friction And Risks

- Stock target validation still fails with 36 package-projection errors. The
  target gate is therefore authoritative, version-pinned, and explicit that
  stock validation did not pass.
- The stock code-review routing test is declared portable but imports omitted
  source-only `ai_context_package.py`; the target runs applicable GWT1–7.
- Changed-path dependency expansion can omit dependencies, so changed-path
  profiles and evidence reuse remain inactive.
- Every one of the twenty effective routes currently loads all thirteen rules.
  This is safe but not yet the task-minimal projection envisioned by the model.
- The v0.12 commit-policy cutover and one exact historical assessment waiver
  require a permanent fail-closed target overlay.
- A governed pre-finalization v0.13 remediation packet was unavailable. The
  safe workaround consumed equivalent fresh v0.12 packets, then post-checked
  fresh v0.13 packets after finalization.
- The exact-predecessor route required seven upgrades and 56 commits before
  analysis closeout. Independent audits were valuable, but several cycles were
  metadata-only corrections of stale resume or identity evidence.
- Windows exposed CRLF false conflicts, Temp ACL failures, unavailable symlink
  privileges, Git executable-mode staging friction, and package bytecode
  hygiene issues.
- `test_python_prerequisites.py` suppresses cleanup errors for repository-local
  fixtures; a passing run can leave an unreadable ignored `shadow-*` directory.
- Two package-native EOF blank lines remain receipt-bound and make a full-range
  `git diff --check main..HEAD` fail, even though checkpoint-scoped diffs pass.

## Defect Disposition

Resolved by exact later evidence:

- `AICU-V090-DOC-001` — dead analyzer command replaced by v0.13 recipe guidance.
- Bundled provider conflict — provider removed; reference-only recipes retained.
- `AICU-V013-AGGREGATE-CONSTRUCTION-001` — bounded product repair passed 13/13
  domain tests, full solution build evidence, independent audit, and fresh
  packet post-check.
- `AICU-V013-TARGET-PROVIDER-TRUTH-001` — four target-truth surfaces and GWT012
  synchronized, then independently accepted at `46928f4`.

Active or mitigated, not upstream-closed:

- `AICU-V010-PROJECTION-001`
- `AICU-V011-SELECTION-001`
- `AICU-V012-PROFILE-REGISTRY-PROJECTION-001`
- `AICU-V012-COMMIT-CUTOVER-001`
- `AICU-V012-COMMIT-DOC-001`
- `AICU-V013-ROUTING-PROJECTION-001`
- `AICU-V013-COMPONENT-OWNERSHIP-001`
- `AICU-V013-PREACTION-PACKET-BOOTSTRAP-001`

## Recommended Next Decisions

1. Keep stock profiles, changed-path execution, evidence reuse, CI, analyzers,
   providers, and recipes inactive until the corresponding upstream defects are
   fixed and a separate owner decision enables them.
2. Require the target-owned gate for all governed AI-context changes.
3. Prioritize downstream package closure, changed-path dependency traversal,
   full required-path planning, durable apply recovery, and pre-finalization
   remediation packets upstream.
4. Decide separately whether Architecture Kit remains the intended analyzer
   provider. If yes, define version range, mapping, parity, consumer proof, and
   readiness-gated opt-in. If no, explicitly supersede the prior proposal.
5. Fix repository-local fixture cleanup by using an external writable temp root
   and failing cleanup visibly instead of suppressing errors.

## Authorization Boundary

This assessment does not authorize CI/profile/reuse/provider activation,
Architecture Kit adoption, merge, push, Issue closure, Project mutation, or
upstream submission.
