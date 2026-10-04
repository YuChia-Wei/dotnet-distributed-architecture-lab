# Current framework contract

This project-owned record identifies the selected local installation. The
[0.19.0 trial plan](../workflows/2026-10-04-framework-019-init/workflow-plan.md)
and [results](../workflows/2026-10-04-framework-019-init/results.md) own execution
and verification evidence.

## Selected installation

| Field | Selection |
| --- | --- |
| Framework release | `v0.19.0` |
| Source commit | `a66957e00aa447be887258fa9b55fd89e39e96dd` |
| Target branch | `codex/2026-10-04-framework-019-init` |
| Target starting revision | `1444d67` |
| Installation selection | [installation.json](../../.ai/custom/installation.json), version 2 |
| Managed inventory | [framework.lock](../../.ai/framework.lock), installer-owned |
| Skills | 18 managed skills, including `ai-context-init@0.2.0` |
| Knowledge | `engineering-common` and `dotnet-backend` |
| Runtime adapters | Codex and Claude, original skill names |
| Target bindings | 40 retained knowledge bindings for 20 request routes |
| Optional managed sub-agents | Not selected; existing six project-owned roles remain |

The [active registry](skills.md) links each installed skill. Read its actual
entry and selected operation before use. Runtime entries under `.agents/skills/`
and `.claude/skills/` are installer projections; presence does not establish
fresh-session discovery or actual execution.

## Project ownership and authority

[Target engineering rules](TARGET-ENGINEERING-RULES.md) retain fourteen complete
rule statements, their applicability, twenty routes, four customizations and
the target Git/attribution contract. Resolve the saved binding for a relevant
request; package installation does not itself adopt a rule.

[Framework configuration](../../.ai/custom/framework.json) retains the selected
artifact stores and constraints. [Custom roles](../../.ai/custom/roles/README.md)
and the [standards-promotion experiment](STANDARDS-PROMOTION-EXPERIMENT.md) are
project-owned, outside the official managed selection. The experimental skill
keeps the `standards-promotion` operation/config namespace; its purpose and
behavior acceptance remain pending.

## Local initialization trial

The direct 2026-10-04 owner request authorizes the stable update, removal of
selected non-project resources and execution of the new initialization skill.
It continues the work associated with target Issue #31; it does not update or
close that Issue. This trial is confined to the named local worktree branch.

`ai-context-init@0.2.0 initialize` reuses the existing product README, requirements,
AGENTS and retained collaboration policies. It fills missing navigation and
[first-task guidance](../guides/first-task.md). Those outputs are target-owned
documents. Repeating initialization checks for meaningful gaps and does not
regenerate satisfactory rules, inventory or product documents.

## Evidence boundaries and retained history

The [project configuration](../project-config.yaml) still marks framework
admission, routine local validation and CI as unconfigured. Issue #23's critical
gate remains unresolved. Document checks and installation evidence do not fill
those gates or prove application/runtime acceptance.

[RC3 main integration](RC3-MAIN-INTEGRATION.md),
[RC4 main integration](RC4-MAIN-INTEGRATION.md) and the
[2026-10-02 factual refresh](CONTEXT-REFRESH-2026-10-02.md) remain historical
evidence. Their integration and push authorizations do not authorize integration
or push of this trial. Issue #22's S6, runtime and upgrade/recovery experiments
remain `deferred-by-owner` within that historical adoption scope.

Actual checks, failures, omissions and current delivery state belong in the
trial results. Installing the skill, executing its instructions, agent discovery,
independent review, CI, main integration and publication are separate facts.
