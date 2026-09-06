# AI Context Audit Report

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260906-001`
- `assessment_type`: `ai-context-verification`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-09-06`
- `created_at`: `2026-09-06T23:17:00+08:00`
- `updated_at`: `2026-09-06T23:17:00+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `dotnet-mq-arch-lab`
- `subject_branch`: `codex/2026-09-06-ai-context-v0-16-0-upgrade`
- `subject_commit`: `c0abe9c2ce288abf2b83edce1806fefb63b5886e`
- `previous_assessment`: `.dev/assessments/ASM-20260830-003/report.md`
- `workflow_refs`: `2026-09-06-ai-context-v0-16-0-upgrade`
- Analysis model: `GPT-5`, reasoning effort unspecified

## Executive Summary

- Overall assessment: the finalized v0.16.0 AI context is internally coherent,
  preserves the four target customizations, and is safe for local closeout.
- Overall score: `8.6/10`.
- Decision: `healthy-with-followups`.
- Verification verdict: `SAFE-TO-CLOSE-LOCAL-V0.16.0-WORKFLOW`.
- Primary strengths: supported direct route, conflict-free 70-operation package
  delta, 34/34 target tests, finalized terminal receipt, 15/15/15 canonical and
  runtime skill parity, and no product-source change.
- Primary risks: downstream stock validation is still not package-closed; the
  target projection must precede the sealed transaction; canonical candidate
  identity and presentation-order APIs remain brittle; the transient receipt is
  419,182 bytes and 8,812 lines.

The package apply engine remains dramatically faster than v0.14.0, but the
end-to-end upgrade is not yet operationally simple. Two fail-closed rollbacks
and one no-write finalization rejection were needed to discover lifecycle
preconditions. Those failures preserved data and never advanced authority, but
they imposed real operator cost and should be treated as framework-improvement
evidence rather than target-repository defects.

## Scope

### Included AI Context Surfaces

- The exact v0.16.0 package-managed delta under `.ai/**`, runtime wrappers,
  framework-managed guides, and governance policies.
- Final target provenance, customization ledger, effective-rule state, and
  content-addressed route packets.
- Sealed package transaction, target-validation receipt, terminal receipt,
  immutable Git subject, and timing observations.

### Default Exclusions

- `src/**`
- `tests/**`, `test/**`
- product implementation trees
- generated dependency trees

### Additional Exclusions

- Product architecture or .NET code review.
- Fixing the findings discovered by this assessment.
- Push, pull request, merge, Issue closure, tag, Release, or publication.

### Code Review Handoff

- Requested: `no`.
- Paths not scanned: product source and test implementation trees.
- Recommended skill: `code-reviewer` only if a later .NET review is requested.

## Methodology And Evidence

### Pass A: Independent Baseline

- Evidence used: public release identity, package manifest, direct transition,
  three sealed transactions, target gate output, candidate authorities,
  terminal receipt, fixed commit, Git diff, and runtime wrapper inventories.
- Checks performed: package/route identity, operation classification, authority
  non-advancement on failure, target-truth preservation, terminal binding,
  effective-rule readiness, skill parity, product-path exclusion, and timing.

### Pass B: Repository-Aware Skill Review

- Policies and skills used: `ai-context-auditor`, `ai-context-upgrader`,
  `ai-context-governance`, assessment policy, workflow policy, and the
  target-owned validation overlay.
- Checks performed: semantic-customization continuity, active alias retirement,
  downstream applicability, Git checkpoint boundaries, and truthful reuse of
  expensive validation evidence.

### Delegation

- Sub-agents used: `no`.
- Assigned surfaces: none; the user did not request delegation, so the audit was
  performed sequentially in the current governed workflow.

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| Package transaction and fixed Git subject | transaction `48d34abf...55f22`; commit `c0abe9c2...5886e` | finalized and fixed | AI context only; product code excluded | transaction success does not prove stock source-only checks | plan, receipt, journal, terminal receipt, Git tree, and command output |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Package-managed delta | 70 operations | agent runtimes and maintainers | selected v0.16.0 components | finalized | 47 replacements, 17 additions, 6 removals; no conflict |
| Runtime skills | 15 canonical, 15 Codex, 15 Claude | agent runtimes | active skill routing | aligned | retired alias entry files are absent |
| Effective rules | 13 rules, 20 packets | governed action skills | target-specific normative state | ready | compact `r-*` packet names replace legacy `ROUTE-*` names |
| Transaction receipt | 419,182 bytes, 8,812 lines | upgrade recovery and validation | transient target surface | pending cleanup | excluded from the fixed commit and retained only through final gate |
| Product paths | 0 changed | product runtime | `src/**`, `tests/**` | untouched | product tests were not rerun |

## Strengths

1. v0.15.1 to v0.16.0 is an explicitly supported direct edge, and all 70
   package operations were automatic with no ignored or unresolved path.
2. Fail-closed transaction handling prevented both stale target-gate projection
   and incorrect candidate-authority identities from advancing provenance.
3. The final transaction binds its plan, packet, decision, target-validation
   receipt, resulting authority digests, and immutable terminal receipt.
4. Final provenance is v0.16.0 at admitted package commit
   `4d1a5c7d039618f007784679d9968c357347272b`; all four target customizations
   remain finalized and audit-bound.
5. Canonical, Codex, and Claude skill registries are aligned at 15 entries; the
   new `diagnostic-analyst` is present and retired alias wrappers are absent.
6. The target gate passed all 34 tests in about 2.1 seconds without rerunning
   product build or tests, consistent with the impact-based validation policy.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIC-001 | MEDIUM | The generic `validate-ai-context.py` projection is still not downstream-applicable because the package omits 24 source-only references. | v0.16.0 target-gate manifest and projection tests | Every downstream upgrade still needs a version-pinned target overlay instead of one package-native gate. | Make the published validation surface package-closed or publish a first-class downstream profile; retain the explicit target overlay until then. | upstream framework maintainer; `ai-context-governance` |
| AIC-002 | MEDIUM | Target-owned validation projection changes must be checkpointed before package apply; changing them inside a sealed transaction invalidates unrelated-write receipt binding. | rolled-back transaction `61c2245c...3e84`; checkpoint `73e54368...ea2da` | A correct target adaptation can force a full rollback if discovered after apply. | Add a planner preflight that emits all target-owned projection deltas before transaction sealing. | upstream framework maintainer; `ai-context-upgrader` |
| AIC-003 | MEDIUM | Candidate authority uses canonical document digests, while schema validation also depends on YAML mapping presentation order; a sorted JSON candidate has the same canonical identity but is not directly finalizable. | rolled-back transaction `d43203b4...90ee`; no-write finalize rejection; matching JSON/YAML canonical digests | The API permits identity-correct candidates that fail late for presentation-only reasons. | Provide one official candidate serializer/digest helper and validate schema order before sealing the decision. | upstream framework maintainer; `ai-context-upgrader` |
| AIC-004 | LOW | Windows rollback of executable-mode paths still requires repeated durable resume steps. | terminal rollback journals for the two superseded transactions | Recovery is safe but noisy and increases operator time. | Normalize Git-mode verification on Windows or batch resumable rollback progress without weakening durability. | upstream framework maintainer |
| AIC-005 | MEDIUM | The schema-2 transient pending receipt is 419,182 bytes and 8,812 lines for a 70-operation upgrade. | `.dev/AI-CONTEXT-APPLY-PENDING.yaml`; Git-admin terminal evidence | It creates conspicuous working-tree noise and is easy to commit accidentally even though it must not become durable target authority. | Add an explicit checkpoint/final-cleanup command and consider a compact content-addressed receipt projection. | upstream framework maintainer; `ai-context-governance` |

## Upgrade-Time Comparison

| Version | Package operations | Measured fast-path evidence | Operational interpretation |
| --- | ---: | --- | --- |
| v0.14.0 | 188 | apply about 87 minutes | unacceptable per-file transaction cost baseline |
| v0.15.0 | 50 | apply about 45 seconds | append-only progress produced a decisive improvement |
| v0.15.1 | 6 | planning about 18 seconds; fixed overhead dominated | patch content was small and low-risk |
| v0.16.0 | 70 | planning about 22.2 seconds; identical applies about 32.3-34.2 seconds; target gate about 2.1 seconds | file-application performance remains good, but end-to-end closeout complexity regressed |

The comparison supports two separate conclusions. The low-level file update
problem seen in v0.14.0 is no longer present. The upgrade workflow still needs
improvement because target projection ordering, authority serialization, Windows
rollback replay, and the large transient receipt turned a roughly two-minute
clean path into a much longer supervised session.

## Baseline And Skill Comparison

### Confirmed

- The v0.15 performance improvement remains present in the v0.16 apply engine.
- Target-owned product and governance truth survives the upgrade.
- Active orchestration now uses `software-development-orchestrator` and target
  initialization uses `ai-context-init`; retired aliases remain historical only.

### Added By Repository-Aware Review

- Upgrade performance and upgrade operability must be tracked separately.
- The transient receipt is a real usability and accidental-commit hazard even
  though it is valid transaction evidence.
- Canonical content identity does not by itself guarantee schema-valid mapping
  presentation for finalization.

### Downgraded Or Deferred

- Stock validation closure remains deferred to the upstream framework.
- No product test result is reused as proof of AI-context-only changes.

### Overturned

- The assumption that conflict-free package operations imply a simple upgrade
  was overturned by the three late lifecycle preconditions.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Public package and route identity | passed | ZIP SHA-256 `d136b69e...c5c85d`; direct v0.15.1-to-v0.16.0 edge |
| Incoming package validation | passed | 650 manifest-covered files; 18 portable entrypoints |
| Package apply | passed | 70/70 operations; transaction `48d34abf...55f22`; no conflict |
| Target gate | passed pre-finalization and after transient cleanup | 34/34 tests; finalized journal-only run passed in about 7.2 seconds |
| Authority finalization | passed | readiness `ready`; terminal receipt raw SHA-256 `5793b97d...d8bdc` |
| Skill and wrapper parity | passed | 15 canonical / 15 Codex / 15 Claude |
| Product path scope | passed | no `src/**` or `tests/**` diff |

### Skipped Validation

- Product build and tests were not rerun because the upgrade changes no product
  source or test-result surface.
- The package-native generic validator is not presented as passing; its exact
  downstream non-applicability remains finding `AIC-001`.

## Recommended Action Order

1. Persist this assessment against fixed commit `c0abe9c2...5886e`.
2. Run the full final target gate with the transient receipt present.
3. Clear the transient receipt and rerun the terminal journal-only target gate.
4. Complete and commit the local workflow closeout.
5. Track `AIC-001` through `AIC-005` as upstream upgrade-operability input before
   claiming that future updates require no special supervision.

## Deferred Items

- Upstream closure of generic downstream validation.
- First-class target-projection preflight and candidate serialization helper.
- Windows rollback-resume and transient-receipt ergonomics.
- Push, pull request, merge, Issue closure, tag, Release, and publication.

## Appendix

### Commands Run

```text
python -B .dev/ai-context/tooling/validate-target-ai-context.py --allow-unfinalized --workflow-id 2026-09-06-ai-context-v0-16-0-upgrade
git diff --check
git diff --name-only -- src tests
git status --short
```

### Notes

- Git-admin transaction evidence was read outside the sandbox.
- The report separates proven file-apply time from total operator elapsed time;
  it does not infer an unrecorded final apply-only duration.
- The fixed subject deliberately excludes the transient pending receipt.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260906-001/report.md`
- Stable finding references: `ASM-20260906-001#AIC-001` through `#AIC-005`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: `2026-09-06-ai-context-v0-16-0-upgrade`
- Verification assessment: `ASM-20260906-001`
- Remediation intentionally not performed by this skill: `yes`
