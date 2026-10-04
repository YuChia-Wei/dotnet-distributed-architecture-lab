# AGENTS.md

[Traditional Chinese](AGENTS.zh-TW.md)

This is the canonical English collaboration guide for the distributed-commerce lab. `AGENTS.zh-TW.md` is its Traditional Chinese (Taiwan) translation. A deeper `AGENTS.*` file governs its own subtree. Precedence is: direct user authorization, deeper guide, this guide, then general documents.

## Project and framework authority

This repository is a .NET distributed-commerce architecture lab. Products, Orders, Inventory and Procurement are its four current business bounded contexts. SupplierSandbox and SupplierMock are external-system examples; the two Vue frontends and YARP are current application surfaces. Use `MQArchLab.slnx`, project files, source, tests, Compose and current `.dev/` project records to verify a fact. `.dev/project-config.yaml` is a generated inventory and yields to those sources. Do not copy source-framework product facts into this target.

[Current framework contract](.dev/ai-context/CURRENT-FRAMEWORK.md) identifies the selected installation and the retained orchestration restoration evidence. Prior main adoption remains recorded in the [RC3](.dev/ai-context/RC3-MAIN-INTEGRATION.md) and [RC4](.dev/ai-context/RC4-MAIN-INTEGRATION.md) integration evidence. [Target engineering rules](.dev/ai-context/TARGET-ENGINEERING-RULES.md) own the retained fourteen full rule statements, twenty request routes, four customizations and target Git boundaries. Installed skills and common/.NET knowledge are separate from target adoption. A package or wrapper does not establish a rule's applicability or a validation pass. The official lock is installer-owned; never hand-edit it. For managed packages, select only the saved, pinned candidate and the original-name Codex and Claude entries declared by the actual installation. The owner separately selected the project-owned `standards-promotion-experimental@0.1.1-alpha.1` copy under `.ai/custom/skills/`; use its separate experimental entry for an explicitly selected trial. Its copied tool retains the `standards-promotion` operation/config namespace. This copy is outside the official lock and distributed release products; purpose and behavior acceptance remain pending. The owner authorized the earlier restoration for main integration and push on 2026-10-01. The 2026-10-04 request selects the stable `0.19.0` local installation and `ai-context-init@0.2.0 initialize` trial on `codex/2026-10-04-framework-019-init`; it does not extend historical integration or push authority.

Historically, for Issue #22, the owner authorized a one-time destructive RC2 replacement and explicitly deferred S6, runtime and upgrade/recovery experiments. Record those checks as `deferred-by-owner`; static checks do not become behavioral acceptance. This does not restore or activate CI. Historical RC1 metadata, wrappers and backups are not current authority.

## Product decisions

- Inventory uses EF Core and its selected stock/reservation outbox boundaries. Products and Orders retain Dapper. Orders selects event sourcing. Procurement and the supplier lab have their own current requirements and operation guides.
- Preserve plain xUnit v3 with recognizable Given-When-Then tests and the explicit BDDfy opt-out. Select Moq or NSubstitute from the test project's actual configuration.
- Retired analyzer and runtime-validation projects remain inactive. Reusable examples, source includes and templates are guidance until this target adopts them.
- Keep target Issue-first authorization, LF policy, scoped `.codex/agents` tracking, actual AI attribution and the exact historical Git exception described in the target authority.

## Progressive loading and routes

Start with the request, Git/worktree state, this guide and named Issue or artifacts. Read `.dev/ARCHITECTURE.md`, `.dev/project-config.yaml`, the relevant requirements/specifications and operations guide when product facts matter. Follow [the active skill registry](.dev/ai-context/skills.md) for one selected skill or operation. Read its installed entry and only the references needed for the request. For AI context changes, read `.dev/standards/AI-CONTEXT-BOUNDARY.md` and `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`. Code discovery prefers an available fresh code graph; verify material claims against tracked files, then use direct search if the graph is unavailable or incomplete.

AI context governance and migration route to `ai-context-governance`; audit routes to `ai-context-auditor`. Architecture, GWT design, code review, requirements, specifications, problem frames, implementation and compliance use their matching selected skills. Decision, lesson and PR authoring use `adr-author`, `lesson-author` and `pr-author`. Use `software-development-orchestrator` for needed development stages and specialist handoffs. The target workflow policies and `.dev/workflows/` continue to own record formats and integration authority. Generic skill instructions do not silently replace target .NET knowledge or effective rule predicates. Before .NET work, resolve the applicable target authority and selected knowledge binding; disclose unavailable specialist coverage. The selected `ai-context-init@0.2.0` fills missing collaboration foundations or refreshes selected project facts when requested; repeated initialization is a gap check over existing meaning, and installation does not execute it. Old `adr`, `lesson`, `pr`, legacy init and `ai-context-upgrader` implementations remain retired.

## Workflow, Git and validation

Use `.dev/standards/WORKFLOW-GATE-POLICY.md` when work changes source-of-truth, AI context, routes or multiple stages. In workflow mode, use `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md`, `.dev/TEAM-GIT-FLOW-RULES.MD` and a dedicated branch before material edits. For commits, use `.dev/standards/GIT-COMMIT-POLICY.md` and its YAML authority. Validate the complete planned message from a file before committing when a suitable validator is available. Record actual model/runtime attribution; the RC1 pinned target validator has retired and no new target-local automated commit validator is configured.

Define observable acceptance criteria and use the narrowest meaningful checks. Report `passed`, `failed`, `blocked`, `deferred` and `not-applicable` truthfully. Keep independent review, CI, runtime execution, package installation, target rule adoption, push, PR, merge, Issue/Project state, tag and publication distinct. Reconcile target-owned authority before applying a framework change. Preserve unrelated changes, user data and historical evidence. Do not use fixture or static results as actual product/runtime evidence.

## Navigation and language

`.ai/` contains the selected managed skill and knowledge packages, explicit project configuration and installer-owned lock. `.agents/skills/` and `.claude/skills/` are runtime discovery entries. `.dev/` contains product truth, standards, target authority, operations, workflows and human guides. `README.md` is the Traditional Chinese product entry; `README.en.md` is its English counterpart; `CLAUDE.md` is a thin runtime pointer.

Agent-facing execution contracts prefer English; human-facing guides may use Traditional Chinese (Taiwan). Keep `AGENTS.zh-TW.md` structurally and normatively aligned with this file. Runtime entries remain projections of their installed package, never a second semantic owner.

## Repository reading map

| Task | Read when relevant |
| --- | --- |
| Understand product purpose and boundaries | [Product README](README.md), [requirements overview](.dev/requirement/distributed-commerce-bounded-context-overview.md), [architecture](.dev/ARCHITECTURE.md) |
| Change behavior or tests | [Behavior baseline](.dev/requirement/reconstructable-system-baseline.md), relevant [domain](.dev/specs/domains/) and [test](.dev/specs/tests/) specs, [target rules](.dev/ai-context/TARGET-ENGINEERING-RULES.md) |
| Select collaboration policy or check ownership | [Policy index](.dev/standards/INDEX.MD), [project validation settings](.dev/project-config.yaml), the applicable operation guide |
| Begin a bounded read-only or small documentation task | [First-task guide](.dev/guides/first-task.md), including command sources, working directory, prerequisites and unrun status |
| Find project records or framework resources | [Project index](.dev/INDEX.md), [AI resource index](.ai/INDEX.MD) |

The first-task guide does not execute its examples. Product commands are discovered instructions until actual execution is recorded; the target framework admission, routine local and CI gates remain unconfigured as recorded in project settings.
