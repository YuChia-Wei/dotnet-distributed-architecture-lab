# AGENTS.md

[Traditional Chinese](AGENTS.zh-TW.md)

This is the canonical English collaboration guide for the distributed-commerce lab. `AGENTS.zh-TW.md` is its Traditional Chinese (Taiwan) translation. A deeper `AGENTS.*` file governs its own subtree. Precedence is: direct user authorization, deeper guide, this guide, then general documents.

## Project and framework authority

This repository is a .NET distributed-commerce architecture lab. Products, Orders, Inventory and Procurement are its four current business bounded contexts. SupplierSandbox and SupplierMock are external-system examples; the two Vue frontends and YARP are current application surfaces. Use `MQArchLab.slnx`, project files, source, tests, Compose and current `.dev/` project records to verify a fact. `.dev/project-config.yaml` is a generated inventory and yields to those sources. Do not copy source-framework product facts into this target.

[Installation selection](.ai/custom/installation.json) records the selected stable `0.19.0` packages and target bindings; the [official lock](.ai/framework.lock) records their installed inventory. [Target engineering rules](.dev/ai-context/TARGET-ENGINEERING-RULES.md) own the retained fourteen full rule statements, twenty request routes, four customizations and target Git boundaries. Installed skills and common/.NET knowledge are separate from target adoption. A package or wrapper does not establish a rule's applicability or a validation pass. The official lock is installer-owned; never hand-edit it. Use only the saved selection and its installed original-name Codex and Claude entries.

The project-owned [experimental promotion skill](.ai/custom/skills/standards-promotion-experimental/SKILL.md) is available only for an explicitly selected trial. It is outside the official lock and distributed release products; purpose and behavior acceptance remain pending. The [2026-10-04 local installation and initialization results](.dev/workflows/2026-10-04-framework-019-init/results.md) are dated evidence, not new integration or push authority.

Historically, for Issue #22, the owner authorized a one-time destructive RC2 replacement and explicitly deferred S6, runtime and upgrade/recovery experiments. Record those checks as `deferred-by-owner`; static checks do not become behavioral acceptance. This does not restore or activate CI. Historical RC1 metadata, wrappers and backups are not current authority.

## Product decisions

- Inventory uses EF Core and its selected stock/reservation outbox boundaries. Products and Orders retain Dapper. Orders selects event sourcing. Procurement and the supplier lab have their own current requirements and operation guides.
- Preserve plain xUnit v3 with recognizable Given-When-Then tests and the explicit BDDfy opt-out. Select Moq or NSubstitute from the test project's actual configuration.
- Retired analyzer and runtime-validation projects remain inactive. Reusable examples, source includes and templates are guidance until this target adopts them.
- Keep target Issue-first authorization, LF policy, scoped `.codex/agents` tracking, actual AI attribution and the exact historical Git exception described in the target authority.

## Progressive loading and routes

Start with the request, Git/worktree state, this guide and named Issue or artifacts. Read `.dev/ARCHITECTURE.md`, `.dev/project-config.yaml`, the relevant requirements/specifications and operations guide when product facts matter. Select one skill or operation from the [saved installation](.ai/custom/installation.json) and the adopted routes in [target engineering rules](.dev/ai-context/TARGET-ENGINEERING-RULES.md). Read its installed [Codex](.agents/skills/) or [Claude](.claude/skills/) entry and only the references needed for the request. For AI context changes, use the ownership and language boundaries in this guide and the retained target rules. Code discovery prefers an available fresh code graph; verify material claims against tracked files, then use direct search if the graph is unavailable or incomplete.

AI context governance and migration route to `ai-context-governance`; audit routes to `ai-context-auditor`. Architecture, GWT design, code review, requirements, specifications, problem frames, implementation and compliance use their matching selected skills. Decision, lesson and PR authoring use `adr-author`, `lesson-author` and `pr-author`. Use `software-development-orchestrator` for needed development stages and specialist handoffs. Existing `.dev/workflows/` records retain their formats and historical scope; integration follows current user authorization and target Git rules. Generic skill instructions do not silently replace target .NET knowledge or effective rule predicates. Before .NET work, resolve the applicable target authority and selected knowledge binding; disclose unavailable specialist coverage. The selected `ai-context-init@0.2.0` fills missing collaboration foundations or refreshes selected project facts when requested; repeated initialization is a gap check over existing meaning, and installation does not execute it. Old `adr`, `lesson`, `pr`, legacy init and `ai-context-upgrader` implementations remain retired.

## Workflow, Git and validation

Use `.dev/TEAM-GIT-FLOW-RULES.MD` for branch and integration boundaries. When authorized work needs durable coordination or continuation, use the selected owning skill and the actual records under `.dev/workflows/`; keep historical formats and outcomes intact. Use a dedicated branch before material workflow edits. The [target Git message and attribution contract](.dev/ai-context/TARGET-ENGINEERING-RULES.md#target-git-message-and-attribution-contract) retains the project's commit requirements. Validate the complete planned message from a file when a suitable validator is available. Record actual model/runtime attribution; no target-local automated commit validator is configured.

Define observable acceptance criteria and use the narrowest meaningful checks. Report `passed`, `failed`, `blocked`, `deferred` and `not-applicable` truthfully. Keep independent review, CI, runtime execution, package installation, target rule adoption, push, PR, merge, Issue/Project state, tag and publication distinct. Reconcile target-owned authority before applying a framework change. Preserve unrelated changes, user data and historical evidence. Do not use fixture or static results as actual product/runtime evidence.

## Navigation and language

`.ai/` contains the selected managed skill and knowledge packages, explicit project configuration and installer-owned lock. `.agents/skills/` and `.claude/skills/` are runtime discovery entries. `.dev/` contains product truth, target authority, operations, workflows and human guides. `README.md` is the Traditional Chinese product entry; `README.en.md` is its English counterpart; `CLAUDE.md` is a thin runtime pointer.

This guide supplies the minimum collaboration baseline; initialization reuses it rather than creating a duplicate policy layer.

Agent-facing execution contracts prefer English; human-facing guides may use Traditional Chinese (Taiwan). Keep `AGENTS.zh-TW.md` structurally and normatively aligned with this file. Runtime entries remain projections of their installed package, never a second semantic owner.

## Repository reading map

| Task | Read when relevant |
| --- | --- |
| Understand product purpose and boundaries | [Product README](README.md), [requirements overview](.dev/requirement/distributed-commerce-bounded-context-overview.md), [architecture](.dev/ARCHITECTURE.md) |
| Change behavior or tests | [Behavior baseline](.dev/requirement/reconstructable-system-baseline.md), relevant [domain](.dev/specs/domains/) and [test](.dev/specs/tests/) specs, [target rules](.dev/ai-context/TARGET-ENGINEERING-RULES.md) |
| Select collaboration policy or check ownership | [Target rules](.dev/ai-context/TARGET-ENGINEERING-RULES.md), [project validation settings](.dev/project-config.yaml), the applicable operation guide |
| Begin a bounded read-only or small documentation task | [First-task guide](.dev/guides/first-task.md), including command sources, working directory, prerequisites and unrun status |
| Find project records or framework resources | [Project index](.dev/INDEX.md), [AI resource index](.ai/INDEX.MD) |

The first-task guide does not execute its examples. Product commands are discovered instructions until actual execution is recorded; the target framework admission, routine local and CI gates remain unconfigured as recorded in project settings.
