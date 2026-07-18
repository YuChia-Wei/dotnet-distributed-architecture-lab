# AI Context Audit Report

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `1.0.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-10T18:22:49+08:00`

## Metadata

- `report_id`: `ASM-20260718-001`
- `report_type`: `post-remediation`
- `owner_skill`: `ai-context-auditor`
- `workflow_id`: `2026-07-18-ai-context-v0-4-upgrade`
- `related_plan_id`: `AICUP-004`
- `status`: `final`
- `audit_date`: `2026-07-18`
- `created_at`: `2026-07-18T21:12:00+08:00`
- `updated_at`: `2026-07-18T21:12:00+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `1.0.0`
- `repository`: `dotnet-mq-arch-lab`
- `branch`: `codex/2026-07-18-ai-context-v0-4-upgrade`
- `subject_commit`: `21c6b61973ef444013baf6a9b4adc822c2729aa8`
- `previous_report`: `.dev/workflows/2026-07-18-ai-context-v0-4-upgrade/reports/01-audit-report.md`

## Executive Summary

- Overall assessment: The target has a coherent, validated v0.4.0 AI context with explicit downstream provenance and no release-blocking drift.
- Overall score: `9/10`
- Decision: `healthy-with-followups`
- Primary strengths: exact-case root routing; canonical/runtime wrapper parity; explicit technology selections; 568-path package accounting; 65 unique, existing, provenance-recorded target overrides; and a 100% target gate.
- Primary risks: two source-release-only regression suites remain packaged and documented as directly runnable even though their excluded dependencies make those commands fail in a downstream installation.

## Scope

### Included AI Context Surfaces

- Root collaboration and identity entries.
- `.ai/**`, `.agents/**`, and `.claude/**`.
- `.dev/**` governance, provenance, indexes, workflows, and validators.
- `.github/**` collaboration declarations.

### Default Exclusions

- `src/**`
- `tests/**`, `test/**`
- product implementation trees
- generated and dependency trees

### Additional Exclusions

- Product behavior and architecture claims were not revalidated from implementation.
- Historical workflow prose was evidence only and was not treated as current normative truth.

### Code Review Handoff

- Requested: `no`
- Paths not scanned: `src/**`, `tests/**`
- Recommended skill: `code-reviewer` only if a separate product-code review is requested.

## Methodology And Evidence

### Pass A: Independent Baseline

- Evidence used: root entries, current indexes, canonical asset registries, wrapper trees, provenance, shell registry, workflow locator, and deterministic validation output.
- Checks performed: ownership and navigation clarity; active versus historical boundaries; wrapper/canonical separation; local override integrity; language and exact-case routing; fail-closed gate composition; and downstream portability.

### Pass B: Repository-Aware Skill Review

- Policies and skills used: `ai-context-auditor`, `AI-CONTEXT-BOUNDARY`, `AI-CONTEXT-LANGUAGE-POLICY`, workflow artifact policy, assessment artifact policy, and v0.4.0 provenance contracts.
- Checks performed: repository validators, wrapper parity, assessment/workflow structure, shell registry parity, package path accounting, and source-only dependency review.

### Delegation

- Sub-agents used: `no`
- Assigned surfaces: none.

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Root entries | 3 collaboration entries plus repository README pair | mixed | repository | active | English canonical agent guide and derived Traditional Chinese guide route with exact v0.4.0 casing |
| `.ai/**` | part of 652-file audit allowlist | agent | reusable framework | active | 14 canonical skills and 32 canonical manifests validated |
| `.dev/**` | part of 652-file audit allowlist | mixed | target truth and governance | active/historical by index | target provenance and technology selections are explicit |
| Runtime wrappers | 14 Codex and 14 Claude skill directories | runtime | derived adapters | active | canonical/runtime parity passed |

## Strengths

1. `.dev/AI-CONTEXT-SOURCE.yaml` pins `REL-v0.4.0` to commit `5af1db672928f9d51f55fee04183ad27b79fb9f8`, records the governed v0.3.0 predecessor, and accounts for 65 unique existing downstream override paths.
2. `validate-ai-context.py` passes exact-case navigation, wrapper parity, canonical manifest, language-policy, ownership, and capability-routing checks.
3. `check-all.sh` passes all 19 selected required checks, including 49 analyzer tests, 2 configuration validation tests, and 5 BuildingBlocks behavior tests.
4. The target records repository-backed technology choices without replacing architecture invariants or silently imposing the profile mocking default.
5. Source, workflow, assessment, product, and generated boundaries remain distinct and discoverable.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIC-001 | MEDIUM | The installed `.ai/scripts/README.md` lists source-release version-governance and package-builder tests as directly runnable, while the package excludes their required release registry/tags and `ai_context_package.py` module. | `.ai/scripts/README.md:87-128`; direct execution produced missing Git refs/release records and `ModuleNotFoundError`; target `check-all.sh` intentionally selects only the applicable manifest validator and safe-apply suite. | A maintainer following the script README can mistake expected downstream incompatibility for target corruption, and future runner synchronization could reintroduce failing source-only checks. | Mark these commands source-only in the packaged README/profile or stop packaging the dependent test files; keep the current target runner override until an upstream release resolves the contract. | `ai-context-governance` for accepted-residual recording; source framework release follow-up |

## Baseline And Skill Comparison

### Confirmed

- Independent navigation, provenance, wrapper, and validation checks found no release-blocking ambiguity.
- Both passes identify the source-only test documentation/package boundary as the only active residual.

### Added By Repository-Aware Review

- The repository policy explains why the target runner override is valid: packaged compatibility does not imply semantic endorsement, and target-owned shell composition retains precedence.

### Downgraded Or Deferred

- The source-only test mismatch is `MEDIUM`, not `HIGH`, because the target required gate excludes the invalid commands, the applicable validators pass, and provenance records the override.
- Product source and test adequacy remain outside this audit.

### Overturned

- No baseline finding was overturned.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state | passed | subject commit `21c6b61973ef444013baf6a9b4adc822c2729aa8` was clean before assessment artifacts |
| Registry and wrapper parity | passed | 14 canonical skills; 14 Codex and 14 Claude wrapper directories |
| Path and reference checks | passed | 23 active indexes and exact-case root routes validated |
| Schema / structured file parse | passed | workflow, provenance/version, shell asset, and assessment structures validated |
| Repository context checks | passed | full gate 19/19 and solution build 0 errors |

### Skipped Validation

- Semantic translation parity was not asserted by the structural validator.
- Product source and product tests were excluded by the audit boundary.
- Windows symlink creation was unavailable for one safe-apply fixture; the suite reported the case as skipped and all other 13 safe-apply cases passed.

## Recommended Action Order

1. Close the current target upgrade as healthy with `ASM-20260718-001#AIC-001` recorded as a non-blocking accepted residual.
2. Correct the source v0.4.x package profile or packaged script README so source-only release/package tests cannot be mistaken for downstream requirements.
3. Revisit the target override only when a later governed package resolves that upstream contract.

## Deferred Items

- Product architecture and code quality review require a separate `code-reviewer` request.
- Physical solution-folder migration, Observability/AOP design, and NuGet publication remain outside the v0.4.0 upgrade.

## Appendix

### Commands Run

```text
python .ai/scripts/validate-ai-context.py
python .ai/scripts/validate-ai-context-versions.py
python .ai/scripts/validate-shell-assets.py
python .ai/scripts/validate-workflow-artifacts.py
python .ai/scripts/validate-assessment-artifacts.py
python .ai/scripts/tests/test_ai_context_exact_case_paths.py
python .ai/scripts/tests/test_profile_projection_contract.py -v
bash ./.ai/scripts/check-all.sh
dotnet build MQArchLab.slnx --no-restore
rg --files -uu AGENTS.md CLAUDE.md AGENTS.zh-TW.md .ai .agents .claude .dev .github
```

### Notes

- The audit assessed committed target state, not the source repository's post-tag main branch.
- The prior baseline report remains unchanged.

## Lifecycle Handoff

- Baseline report path: `.dev/workflows/2026-07-18-ai-context-v0-4-upgrade/reports/01-audit-report.md`
- Remediation owner: `ai-context-governance`
- Remediation report path: `.dev/workflows/2026-07-18-ai-context-v0-4-upgrade/reports/02-remediation-report.md`
- Post-remediation assessment path: `.dev/assessments/ASM-20260718-001/report.md`
- Remediation intentionally not performed by this skill: `yes`
