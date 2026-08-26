# Feedback Brief For ai-collaboration-framework

## Status And Audience

This is a repository-local, evidence-backed feedback brief for maintainers of
`ai-collaboration-framework`. It is **prepared but not submitted**. No upstream
Issue, PR, release, comment, or repository mutation is authorized by this
workflow.

Evidence comes from the exact v0.6.0 → v0.13.0 downstream upgrade, retained
plans and receipts, independent fixed-commit audits, the finalized v0.13 target
state, and `gpt-5.6-sol`/`max` post-upgrade analysis.

## What Worked Well

- Exact-predecessor migrations preserved release contracts and made every
  intermediate failure recoverable from a durable Git checkpoint.
- Package archive, sidecar, payload, migration, plan, receipt, source commit,
  and target commit identities were consistently pinned.
- Required-path receipts caught drift the operation planner did not expose.
- Reconciliation acknowledgement preserved target bytes without pretending to
  authorize replacement.
- Staged finalization remained fail closed: authority changed only after
  independent audit; packets were published before state; the working receipt
  remained until finalized gates and packet post-checks passed.
- Thirteen explicit rules and twenty exact routes detected real pre-existing
  aggregate construction debt without weakening the rule.
- v0.13 removed the bundled provider cleanly and replaced it with reference-
  only, not-selected recipes without inferring activation.
- Independent audits caught false checksum, stale resume, nonexistent SHA/path,
  dirty worktree, and premature-finalization evidence. Failed results remain
  retained rather than overwritten.
- A SHA-pinned target overlay allowed honest downstream validation while all
  receipt-bound framework bytes stayed exact.

## Reproducible Framework Findings

| Priority | Finding | Observed behavior | Current workaround | Recommended acceptance test |
| --- | --- | --- | --- | --- |
| P0 | Raw EOL hashes create false reconciliation | v0.7/v0.8 produced LF/CRLF-only conflicts on Windows. | Repository LF attributes and explicit review. | LF package base checked out as CRLF must not become semantic conflict; binary/intentional CRLF changes must still fail. |
| P0 | Planner omits drifted managed paths unchanged between releases | v0.9 plan omitted 159 receipt-required mismatches: 127 EOL, 2 whitespace, 30 semantic. | Receipt allowlist exact-copied trusted payload bytes and recorded preimages/results. | Inspect every selected required path and emit reconcile when target differs, even if predecessor and incoming package bytes are identical. |
| P0 | Apply lacks durable recovery before the first write | v0.8 ACL failure left prefix mutations without a receipt or complete rollback. | Restore exact starting blobs and rerun only after clean read-back. | Persist a transaction journal first; test mid-write failure, process death, rollback failure, and ACL denial. |
| P0 | Downstream payload is not closed over its declared validation surface | v0.13 stock validator fails with 36 projection errors. The extracted package omits all 18 declared source-only entrypoints; the installed target has 17 absent because it retains the exact compare helper. | SHA-pinned target-applicable gate; explicit source-only exclusions. | From an isolated extracted package, validate every packaged runtime reference and run every declared portable CLI/test; all active dependencies must exist and source-only entries must be explicitly unavailable without breaking stock validation. |
| P0 | Changed-path dependency traversal can omit dependencies | Direct match is selected before recursive expansion, so the already-selected guard returns early. | Changed-path execution and evidence reuse remain inactive. | A direct match with transitive dependencies must execute every dependency exactly once with cycle protection. |
| P0 | No consumable pre-finalization remediation packet | v0.13 packets were stale until finalization, while finalization required a governed product fix. | Resolve equivalent fresh v0.12 packets, commit the bounded fix, cherry-pick, then post-check v0.13 packets. | Candidate packet must bind target HEAD, pending receipt, incoming catalogs, owner decision, and narrow scope; drift invalidates it and it never becomes live authority. |
| P1 | Installed predecessor validators can falsely pass incoming candidates | Retained v0.6 gates passed while incoming v0.7 enforcement reported ten missing fields. | Run incoming validators plus the target gate explicitly. | Finalization must prove incoming candidate-gate execution and stop when predecessor passes but incoming rejects. |
| P1 | Breaking commit grammar uses source time as target cutover | v0.12 policy retroactively rejected 32 valid target commits. | Target prospective cutoff after the last legacy commit; no history rewrite. | Preserve legacy grammar before target adoption and enforce issue-only/scope-only grammar afterward. |
| P1 | Commit cutover is undocumented | Release/migration guidance omitted the breaking boundary and no-history-rewrite procedure. | Target documentation and overlay. | Release notes must state old/new grammar, target cutoff selection, and compatibility path. |
| P1 | Receipt does not bind Git mode | Receipt verifies path/SHA but not index mode; v0.10 needed staging before `100755` was visible. | Shell-asset validation plus explicit staging. | Receipt schema and validator must fail a required executable-mode drift under documented Windows semantics. |
| P1 | Selected-input fingerprint is not reproducible downstream | Source selection inputs/profile are absent from extracted v0.11–v0.13 packages. | Trust archive checksum and release identity. | An extracted package alone must reproduce the selected-input fingerprint or verify a supplied proof. |
| P1 | Evidence/resume semantics are structurally under-validated | Several audits caught stale “commit next”, wrong/nonexistent SHA, and stale locator/index state. | Independent fixed-HEAD audits and manual synchronization. | Validate referenced SHAs, committed-versus-pending state, next action, locator/index timestamp, and lifecycle progression as one contract. |
| P2 | Profile-registry test imports source-only profile | v0.12/v0.13 downstream package lacks `.ai/distribution/profiles/dotnet-backend.yaml`. | Pin and exclude the exact source-scoped test. | Use a packaged fixture or mark the case source-only; isolated package discovery must pass. |
| P2 | Portable code-review routing test imports source-only module | v0.13 aborts before discovery with `ModuleNotFoundError: ai_context_package`. | Target static GWT1–7 projection; GWT8 recorded source-release-only. | Isolated package must run GWT1–7 and explicitly classify GWT8 without importing omitted source code. |
| P2 | Component ownership metadata disagrees | The version policy is lifecycle-core in the portable manifest and software-core in package inventory. | Both components are mandatory in this target; no optional inference. | Generate all ownership projections from one source and test optional selections. |
| P2 | Python fixture cleanup can leave unreadable ignored directories | `test_python_prerequisites.py` suppresses cleanup failures for repo-local `shadow-*` fixtures. | Remove only audit-created exact paths outside sandbox and re-read Git state. | Use an external temp root and fail cleanup visibly; passing tests must leave no fixture. |
| P2 | Package-native EOF blanks survive publication | Full `git diff --check main..HEAD` reports `common-rules.md` and `PRODUCT-SOURCE-PROJECTION-CONTRACT.md`. | Preserve receipt-bound bytes and report the diagnostic honestly. | Run full package-delta whitespace lint before publication. |

## Resolved Findings Worth Keeping As Regressions

- `AICU-V090-DOC-001`: v0.13 removed the dead
  `DotnetBackendValidation.Tests` instruction. Keep a negative test for retired
  target project names.
- Bundled mechanical-validation provider conflict: v0.13 removed the provider
  and retained reference-only, not-selected recipes. Keep absence/activation
  assertions across target entry docs and package manifests.
- `AICU-V013-AGGREGATE-CONSTRUCTION-001`: downstream effective rules found a
  target defect and the bounded repair passed. Keep the rule and replay tests.

## Target, Process, And Environment Findings

The following are useful lessons but must not be mislabeled as package defects:

- The four stale target-owned provider claims were a target truth/gate coverage
  defect, not an upstream package defect. They were corrected at `d985e0e` and
  independently accepted at `46928f4`.
- Commit `ad194beb...` omitted one assessment trailer. The exact SHA,
  assessment, and waived-error tuple is safely attested; history was not
  rewritten.
- Several checksum/resume/SHA/path errors were workflow evidence mistakes. The
  framework can improve structural validators, but the package bytes did not
  cause those individual claims.
- The target route-ID test initially omitted canonical JSON's terminal LF; the
  route IDs were correct and the target oracle was repaired.
- Aggregate constructor virtual dispatch was pre-existing product compliance
  debt discovered by the installed rule, not a v0.13 regression.
- Sandbox ACL, Windows Temp, Git Bash signal-pipe, symlink privilege, and
  `core.filemode=false` friction require portable test roots and clear platform
  semantics; identical host runs passed.
- Running Python without `-B` inside extracted packages created unmanifested
  `__pycache__`; validation should use an isolated cache or disable bytecode.

## Process Recommendations

1. Treat the operation plan as a proposal and the full required-path inventory
   as the authoritative postcondition.
2. Keep working receipt, durable evidence receipt, finalized authority, and
   receipt removal as separate states.
3. Add a resumable multi-hop driver that internally executes exact predecessor
   migrations and gates; do not replace them with a bulk latest-version copy.
4. Define “portable” as complete dependency closure in an actual downstream
   package, never merely successful execution in the source tree.
5. Make governance policy cutovers target-prospective.
6. Treat durable evidence as executable state: wrong hashes, stale next actions,
   and nonexistent refs must block even when technical tests pass.

## Suggested Upstream Issue Decomposition

1. `[Bug] Close downstream validation over the published package payload`
2. `[Bug] Expand changed-path dependencies before marking checks selected`
3. `[Bug] Plan reconciliation for drifted managed paths unchanged between releases`
4. `[Reliability] Persist an upgrade transaction journal before the first mutation`
5. `[Design] Support receipt-bound candidate rule packets during upgrade remediation`
6. `[Migration] Make breaking policy cutovers target-prospective and documented`
7. `[Integrity] Bind Git modes and reproducible selection inputs in package receipts`
8. `[Enhancement] Add a resumable multi-hop exact-predecessor upgrade driver`
9. `[Governance] Validate evidence SHAs, resume state, and assessment commit receipts`
10. `[Windows DX] Make validation hermetic across Temp, Git modes, CRLF, and bytecode`
11. `[Metadata] Generate component ownership from one source`
12. `[Regression] Keep retired provider commands and whitespace out of releases`

The broader layered rule/profile/Architecture Kit design should continue in the
existing discussion branch rather than being duplicated. This brief supplies
downstream implementation evidence; it does not publish that proposal.

## Evidence Entry Points

- Progressive report: [`upgrade-report.md`](upgrade-report.md)
- Per-version reports: [`01-v0.7.0-reconciliation.md`](01-v0.7.0-reconciliation.md)
  through [`07-v0.13.0-reconciliation.md`](07-v0.13.0-reconciliation.md)
- Developer impact: [`08-developer-impact-and-score.md`](08-developer-impact-and-score.md)
- Discussion comparison: [`09-discussion-branch-comparison.md`](09-discussion-branch-comparison.md)
- Current defect manifest:
  `../../../ai-context/tooling/target-gate-manifest.yaml`

## Authorization Boundary

Prepared locally only. No upstream submission, Issue, PR, release, comment,
merge, push, or Project mutation has been performed or authorized.
