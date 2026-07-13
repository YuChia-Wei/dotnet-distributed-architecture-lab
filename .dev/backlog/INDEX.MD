# Backlog Index

This index catalogs durable work that must remain visible outside workflow
artifact directories. See [README.MD](README.MD) for ownership and lifecycle.

## Planned / Open

| Item | Priority | Summary | Decision / Handoff | Updated |
| --- | --- | --- | --- | --- |
| [TOOL-001](items/TOOL-001.yaml) | MEDIUM | Verify hosted Linux behavior and consider manifest-driven runner execution. | Decide Linux verification, runner redesign, both, or defer. | 2026-07-12 |
| [LANG-001](items/LANG-001.yaml) | MEDIUM | Refresh and reduce translation debt before strengthening semantic parity gates. | Decide priority after a refreshed candidate inventory. | 2026-07-12 |
| [GOV-001](items/GOV-001.yaml) | MEDIUM | Reconcile legacy workflow follow-ups against later completed work. | Read-only reconciliation first; promote only current work. | 2026-07-12 |
| [CAP-001](items/CAP-001.yaml) | LOW | Decide the ownership of technical glossary and terminology work. | Choose a skill, extend context guidance, or defer. | 2026-07-12 |
| [VAL-001](items/VAL-001.yaml) | LOW | Reassess deferred repository and dependency/version validation gaps. | Fresh development-tooling inventory required before planning. | 2026-07-12 |

## In Progress

No durable backlog item is currently in progress.

## Resolved

| Item | Priority | Resolution | Workflow | Updated |
| --- | --- | --- | --- | --- |
| [CTX-003](items/CTX-003.yaml) | HIGH | Remediated and independently verified all five CTX-001 findings with no regression. | [`2026-07-12-ai-context-truth-contract-remediation`](../workflows/2026-07-12-ai-context-truth-contract-remediation/workflow.yaml) | 2026-07-12 |
| [CTX-001](items/CTX-001.yaml) | HIGH | Completed the independent post-AIC-007 audit; five findings were handed to AI context governance. | [`2026-07-12-post-aic-007-ai-context-audit`](../workflows/2026-07-12-post-aic-007-ai-context-audit/workflow.yaml) | 2026-07-12 |
| [CTX-002](items/CTX-002.yaml) | HIGH | Removed the retired generated-script catalog entry and restored AI context validation. | [`2026-07-12-ctx-002-ai-index-repair`](../workflows/2026-07-12-ctx-002-ai-index-repair/workflow.yaml) | 2026-07-12 |
| [AIC-007](items/AIC-007.yaml) | HIGH | Required gates fail closed; Git-index executable modes and runner/manifest parity are validated with GWT fixtures. | [`2026-07-11-aic-007-fail-closed-validation`](../workflows/2026-07-11-aic-007-fail-closed-validation/workflow.yaml) | 2026-07-12 |
