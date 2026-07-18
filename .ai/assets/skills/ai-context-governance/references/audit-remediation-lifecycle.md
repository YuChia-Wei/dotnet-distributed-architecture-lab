# AI Context Audit Remediation Lifecycle

Canonical ownership rule: `ASSESSMENT-ARTIFACT-001`.

Use this lifecycle after an `ai-context-auditor` assessment identifies findings and the user authorizes remediation. A transient conversation-only analysis may inform the decision, but remediation starts a durable governance workflow; it does not retroactively turn transient analysis into an assessment artifact.

## Ownership

| Phase | Owner | Artifact |
| --- | --- | --- |
| Baseline assessment | `ai-context-auditor` | `.dev/assessments/<baseline-id>/report.md` |
| Triage and remediation | `ai-context-governance` | tasks and `reports/remediation-report.md` |
| Independent verification | `ai-context-auditor` | `.dev/assessments/<verification-id>/report.md` |
| Closure | `ai-context-governance` | final workflow/task state and remediation report |

The auditor remains read-only with respect to the context being assessed. Governance must not rewrite or copy the baseline report or author the independent verification conclusions.

## Lifecycle

1. Create or switch to the dedicated governance workflow branch, then create the locator, plan, and initial tasks from governance-owned templates.
2. Register or request the baseline assessment, link it from the workflow, and preserve its report without remediation claims.
3. Triage every finding by severity, owner, dependency, disposition, and validation need.
4. Remediate only authorized findings in bounded tasks and update each task after durable progress.
5. Build `reports/remediation-report.md` as an evidence ledger, not as an independent audit.
6. Request `ai-context-auditor` to re-run the relevant checks and create a new verification assessment on the active workflow branch.
7. Reconcile baseline finding references against remediation and verification assessment evidence.
8. Close the workflow only when every finding has an explicit status and all required validation, commit, and deferral evidence is recorded.

## Resume Safety

Before stopping because of budget, approval, or tool limits:

- update `updated_at` in the locator, plan, and active task;
- record the last completed step and exact next action;
- persist validation output or command summaries already obtained;
- list dirty or staged files and commit state;
- keep unresolved decisions explicit instead of recomputing them later.

On resume, read `workflow.yaml`, the plan, the active task, the linked baseline assessment, the remediation report, and any verification assessment before re-auditing the repository.

For a push-only handoff, resume from the pushed workflow branch. If a checkpoint was merged before completion, start from the updated target on the next dedicated continuation branch. Record the handoff in locator/plan history and keep unfinished findings active.
