# RC1 and retained target disposition

Subject: target worktree `F:/framework-next/rc2-mq-adoption` at baseline `06d9b37f55505b321a2d6b32cfd0fe4946c22721`. This inventory records planning and subsequent file disposition; it is not target validation or an acceptance receipt. The final fixed RC2 catalog/subset was installed through official API2 plan/apply from product commit `aad927328c20b08c8445e8ad1792eadd8ecc3466`; the installer-owned lock was read back at raw SHA-256 `c9a47c945f19fe869696c514003f7eb64ad0219b8f4a315fde4b1d7eaa7ea15f`.

## Removed tracked RC1 installation and control plane

The writer verified each absolute target was contained in the assigned worktree and had no reparse descendants, then removed only Git-tracked bytes: `.ai/core/`, `.ai/framework.lock`, the RC1 candidate/binding/provenance/effective-state/20 packets/retained inventory, the v0.18 runtime backup, 18 `framework-*` Codex entries, four old init/upgrader entries across Codex and Claude, and `.dev/ai-context/tooling/` including its pinned Git validator. The complete normative statements and applicability of fourteen rules, twenty target routes and four customizations were first copied into `.dev/ai-context/TARGET-ENGINEERING-RULES.md`. No new lock, selection, receipt or pass was invented.

## Initial replacement classification before official installation

| Existing tracked root | Inventory | Current use and replacement requirement |
| --- | ---: | --- |
| `.ai/assets/skills/` | 199 files | Old framework skill specs; RC2 selected 18 packages are expected to replace active skill instructions. Check target-only role dependencies before deleting. |
| `.ai/assets/tech-stacks/` | 195 files | Old .NET reusable content; RC2 `dotnet-backend` knowledge has a source inventory of 229 files, but exact catalog/subset and member parity are pending. Target-owned effective rules already have independent authority. |
| `.ai/assets/shared/` | 28 files | Old shared framework contracts; RC2 `engineering-common` covers selected content, but retained agent/policy references must be reconciled. |
| `.ai/assets/sub-agent-role-prompts/` | 13 files | Six `.codex/agents` entries, one `.claude/agents` entry and one `.github/agents` entry currently load these target-configured role contracts. Keep or explicitly relocate/retire them; do not orphan live entries. |
| `.ai/assets/templates/` and `.ai/assets` root docs | 7 files | Old reusable source templates and directory guidance; inspect current consumers before removal. |
| `.ai/scripts/` | 54 files | Target standards still name assessment, dependency, workflow and handoff validators, and `check-all.sh --critical`. Keep the required minimal code/dependency closure or revise those policy commands only after equivalent target authority is decided. |
| `.dev/guides/ai-collaboration-guides/` | 30 files | Old human skill/runtime guides; current project product guides are elsewhere. Check incoming skill/user-guide replacement and live links. |
| `.dev/standards/AI-CONTEXT-BOUNDARY.md` | 1 file | Contains valid evidence, ownership and ambiguity rules alongside obsolete `.ai/assets` paths and v0.18 packet assertions. Preserve normative meaning and edit only obsolete destinations after final layout is known. |
| `.dev/standards/AI-CONTEXT-OWNERSHIP.*` and `AI-CONTEXT-VERSION-POLICY.md` | 3 files | Old framework-source registry/version policy; target rule IDs and decisions have moved to project authority. Check remaining cross-references before deletion. |

## Verified live references requiring disposition

- `.codex/agents/{bounded-routine-worker,context-translator,evidence-report-synthesizer,fixed-head-independent-auditor,reconciliation-worker,semantic-governance-analyst}.toml`, `.claude/agents/context-translator.md` and `.github/agents/context-translator.agent.md` name old role contracts.
- `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md`, `DEPENDENCY-VERSION-CONSISTENCY-POLICY.md`, `WORKFLOW-ARTIFACT-POLICY.md`, `WORKFLOW-HANDOFF-POLICY.md` and `WORKFLOW-HANDOFF-POLICY.yaml` call old `.ai/scripts` paths.
- `.dev/standards/{templates,examples,rationale}/` indexes point to old .NET assets that appear in the new knowledge source; exact installed member mapping is pending.
- Historical workflows/assessments and the new Procurement, Frontend and external API documentation remain distinct from active framework files. They are not removed merely because an agent helped write them.

Automatic approval review rejected a broad deletion of the listed old trees before exact replacement proof, citing possible active target tooling. It separately rejected a shortened rewrite of the AI-context boundary and standards/guides indexes because it could discard valid policy. The writer has not split or reissued either rejected action. The later final disposition below supersedes this initial classification; retain the failed and rejected attempts as distinct historical evidence.


## Final disposition update

- All 442 tracked `.ai/assets/` files were removed after the selected RC2 core
  skills, common/.NET knowledge, both adapters, and target-owned roles were
  present; the frozen fourteen-rule authority and forty selection bindings
  preserve the target's adopted semantics.
- Of 54 tracked `.ai/scripts/` files, 47 obsolete source/RC1 entries were
  removed. Four current target policy validators plus
  `python_prerequisites.py`, a four-entry registry and directory README remain.
  The future current-framework gate is explicitly unconfigured, not passed.
- The source-era `AI-CONTEXT-OWNERSHIP.yaml` registry was removed while the
  ownership policy's stable identity, strength, precedence and fail-closed
  invariants were retained with RC2 knowledge/catalog and target-authority paths.
- Broad removal of all 30 human-facing guides was rejected by automatic
  approval review. A later per-file use and caller inventory established a
  narrower disposition: five guides for retired source-era skills or routes
  (`DEV-WORKFLOW-SKILL-GUIDE`, `REPO-STRUCTURE-SYNC-SKILL-GUIDE`,
  `REQUIREMENT-AND-SPEC-DESIGNER-STRATEGY`, `AI-CONTEXT-INIT-SKILL-GUIDE`,
  `AI-CONTEXT-UPGRADER-SKILL-GUIDE`) were removed; the other 25 remain as
  current human guidance with obsolete paths or unsupported template claims
  corrected. The orchestrator guide was replaced against the selected RC2
  skill contract because its prior routing and task-JSON semantics no longer
  described the selected package.
- Recent Procurement, Frontend, external API and other product documents were
  preserved. The obsolete RC1 candidate/history/tooling copies were removed,
  while current project configuration and the eight configured agent/runtime
  entries retain their actual dispatch semantics through `.ai/custom/roles/`.
