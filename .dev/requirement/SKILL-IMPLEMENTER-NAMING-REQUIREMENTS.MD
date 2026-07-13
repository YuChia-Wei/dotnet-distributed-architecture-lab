# Skill Implementer Naming Requirements

## Metadata

- Version: 0.3
- Date: 2026-06-08
- Owner: YuChia-Wei
- Scope: In
  - Rename and clarify implementation skills around a scope-first taxonomy.
  - Define `slice-implementer` and `local-change-implementer` responsibilities.
  - Convert command/query/reactor implementers from independent skills into slice modes/references unless a later spec proves they must remain separate.
  - Record the current test implementer discussion without creating a test skill yet.
- Scope: Out
  - Do not implement the rename in this requirement.
  - Do not modify runtime wrappers, canonical skill registry, or dev-workflow profile yet.
  - Do not create new executable test skill in this requirement.

## Implementation Outcome

- Status: Implemented
- Completed: 2026-06-09
- Workflow: `.dev/workflows/2026-06-implementer-taxonomy-domain-language/`
- Result:
  - `slice-implementer` and `local-change-implementer` are active top-level skills;
  - command, query, and reactor rules are `slice-implementer` mode references;
  - old implementer skill names and wrappers were removed without aliases;
  - `test-implementer` remains deferred.

The original requirement wording below is preserved as decision history. Items described as future work or open decisions should be interpreted through this implementation outcome and the completed workflow.

## Context & Goals

The current `staged-refactor-implementer` and `tactical-refactor-implementer` names can mislead AI agents. In other projects, agents recommended refactor implementer skills for work that started from new requirements, bug fixes, validation failures, or review remediation. The problem is not that the work never includes refactoring. The problem is that `refactor` is a technique or intent, not the safest primary routing category for all code changes.

This repository needs implementation skill names and routing rules that describe the safe change boundary. Architecture roles such as command, query, and reactor should become implementation modes or references under the bounded slice implementer unless a later spec proves they need independent skill identity.

Goals:

- Reduce incorrect routing of feature, fix, and remediation work into refactor-only skills.
- Keep generic implementation skill count small.
- Use a scope-first classification model for implementer skills.
- Describe implementation skills by bounded slice or local blast radius.
- Preserve command/query/reactor rules as modes, playbooks, or references under the slice implementer.
- Decide whether test authoring needs a dedicated skill or should remain part of existing BDD/spec/implementation flows.

Success means a future `dev-workflow` execution can rename and update the affected skills without re-opening the basic naming rationale.

## Personas

- Human maintainer
  - Wants skill names that match how work is actually requested.
  - Needs clear decisions before skill migration changes many files.
- AI agent
  - Needs routing rules that distinguish work intent from change scope.
  - Must not treat every code change as refactoring.
- Downstream project user
  - Wants to use these skills in product repositories without confusing feature work, bug fixes, and pure refactoring.

## Functional Requirements

### FR-1: Rename Refactor Skills Into Scope-First Implementers

The repository should rename generic refactor implementer skills to neutral scope-oriented names.

Decided naming:

| Current skill | Recommended new name | Meaning |
| --- | --- | --- |
| `staged-refactor-implementer` | `slice-implementer` | Implements one bounded implementation slice that may be feature, fix, remediation, cleanup, refactor, command, query, reactor, or generic. |
| `tactical-refactor-implementer` | `local-change-implementer` | Implements one local code change around a class, object, method, symbol, or direct call sites. |

The final names must avoid implying that the skill is only for behavior-preserving refactoring.

### FR-2: Use Scope-First Routing With Mode-Based Architecture Roles

Implementer routing should be scope-first:

1. `dev-workflow` decides whether implementation is needed.
2. `slice-implementer` handles a bounded implementation slice.
3. `slice-implementer` selects a mode/reference such as command, query, reactor, generic, remediation, or refactor.
4. `local-change-implementer` may handle small local technical changes inside or outside a slice.

The future implementation should treat command/query/reactor as `slice-implementer` modes/references, not independent top-level implementer skills, unless a later spec identifies a non-mergeable specialist contract.

### FR-3: Separate Work Intent From Scope And Mode

Implementation prompts and task artifacts should distinguish intent, scope, and mode.

Intent examples:

- `feature`
- `bug-fix`
- `review-remediation`
- `validation-failure-remediation`
- `behavior-correction`
- `refactor`
- `cleanup`

Scope examples:

- `local`
- `slice`
- `architecture-level`

Mode examples:

- `command`
- `query`
- `reactor`
- `generic`
- `refactor`
- `remediation`

Routing should choose the skill primarily by safe scope, then record intent and mode in the task or prompt.

### FR-4: Convert Architecture-Role Implementers Into Slice Modes/References

The repository should migrate the following implementer skills into `slice-implementer` modes or references:

- `command-use-case-implementer`
- `query-use-case-implementer`
- `reactor-implementer`

Their existing constraints and playbooks should be preserved unless a later discussion explicitly changes them.

Expected mode/reference structure:

```text
.ai/assets/skills/slice-implementer/references/modes/
  command-use-case.md
  query-use-case.md
  reactor.md
  generic-slice.md
```

Rationale:

- Command/query/reactor are important architecture roles, but they are still bounded implementation slice variants.
- Keeping them as modes avoids mixing architecture-role skill names with scope-based skill names.
- This is easier to explain to a team: one bounded slice implementer, with architecture-specific modes.

### FR-5: Define Local Change As Lower-Level Technical Execution

`local-change-implementer` should be a lower-level local execution skill. It can be invoked directly for small edits, or by `slice-implementer` when a slice contains local class/object/symbol changes.

`local-change-implementer` handles:

- single class/object/method/symbol changes;
- direct call-site updates;
- coding style or small technical corrections;
- local SQL/ORM implementation adjustments;
- behavior-preserving local refactoring.

It must stop and hand off when it discovers:

- class extraction;
- interface extraction;
- new abstraction boundary;
- dependency direction changes;
- domain language changes;
- multi-module behavior changes.

### FR-6: Update Dev Workflow Routing

The future implementation must update `dev-workflow` capability routing so code changes are routed by scope, intent, and mode instead of refactor-oriented categories.

`dev-workflow` should classify:

1. current entry point;
2. work intent;
3. implementation scope;
4. slice mode, if any;
5. owner skill or local sub-skill.

### FR-7: Remove Old Skill Names Without Alias

The future rename should remove old skill names instead of keeping deprecated aliases.

The migration should:

- delete old canonical skill directories and runtime wrappers as part of the rename;
- update active registries, wrappers, guides, and `dev-workflow` profile references;
- leave historical workflow artifacts unchanged unless a short migration note is useful;
- rely on git history for recovery if a deleted skill name needs to be inspected later.

### FR-8: Defer Test Implementer Skill

The repository should not create a test author, test writer, or test implementer skill in this workflow.

Current decision:

- test documentation and design should remain covered by `bdd-gwt-test-designer` and related spec workflows;
- a future executable test skill, if needed, should likely be named `test-implementer`;
- the likely responsibility would be analyzing classes or behaviors without adequate tests and creating executable tests;
- details are not mature enough to include in the current implementation rename workflow.

Deferred candidate:

| Candidate | Meaning | Current status |
| --- | --- | --- |
| `test-implementer` | Finds missing executable test coverage and adds tests for existing behavior or changed behavior. | Deferred; needs separate requirement. |

## Non-Functional Requirements

- Naming must be understandable to humans without reading long descriptions.
- Agent-facing canonical specs should remain English.
- Human-facing guides should use Traditional Chinese Taiwan usage.
- Migration may remove old runtime skill names directly; compatibility aliases are not required.
- Reference updates must be validated with search.
- The final implementer taxonomy should be easy to explain as scope-first with mode-specific references.

## Constraints & Assumptions

- This requirement assumes the current repository purpose is clear enough and does not require a root `AGENTS.md` rewrite.
- The migration will affect `.ai/assets/skills/`, `.agents/skills/`, `.claude/skills/`, `.dev/guides/ai-collaboration-guides/`, skill registries, and `dev-workflow` profile references.
- Historical workflow artifacts should not be rewritten solely to replace old skill names.
- The future implementation should be driven by `dev-workflow` and likely executed with `ai-context-governance` for skill registry and wrapper migration.
- Original skill restrictions should be preserved during rename/mode migration unless explicitly changed in a later spec.

## Domain / Business Rules

- Implementer skill names should use a scope-first classification model.
- `refactor` is an intent or implementation technique, not the default category for all code changes.
- `slice-implementer` must not redefine architecture direction.
- A local change implementer must not expand into a multi-module redesign.
- `slice-implementer` must not silently broaden the agreed slice.
- If local change work requires extracting a class, extracting an interface, changing dependency direction, or changing domain language, it must stop and escalate to architecture review or a larger change-slice workflow.
- Command/query/reactor implementation rules should be preserved as slice modes/references.

## Acceptance Criteria

- The future implementation has a migration plan for replacing `staged-refactor-implementer`, `tactical-refactor-implementer`, `command-use-case-implementer`, `query-use-case-implementer`, and `reactor-implementer`.
- The new top-level implementer names are based on safe change scope, not refactor-only or architecture-role terminology.
- `dev-workflow` routing distinguishes intent, scope, and slice mode.
- Old skill names are removed directly, or any retained alias is justified against the current no-alias decision.
- Test implementer is explicitly deferred and not mixed into the rename workflow.
- Command/query/reactor rules are preserved as `slice-implementer` references or modes.
- `local-change-implementer` can be invoked by `slice-implementer` for local technical changes and has explicit escalation rules.
- Updated files pass reference search and whitespace validation.

## User Decisions Required

| Decision | Recommended approach | Why |
| --- | --- | --- |
| Final new name for `staged-refactor-implementer` | `slice-implementer` | Short, scope-first, and suitable for feature, fix, remediation, refactor, command, query, reactor, or generic slices. |
| Final new name for `tactical-refactor-implementer` | `local-change-implementer` | Names local blast radius clearly and naturally. |
| Keep deprecated aliases? | No | The repository is still being actively organized and git history is enough for recovery. |
| Create test skill now? | No | Boundary overlaps are not resolved yet. |
| If test skill is created later, preferred term? | `test-implementer` | The possible gap is executable test creation, while BDD/test design is already covered. |
| Keep command/query/reactor as independent implementer skills? | No, migrate to `slice-implementer` modes/references | Scope-first taxonomy is easier to explain and avoids mixing classification axes. |

## Open Decisions

| Decision | Current concern | Suggested next step |
| --- | --- | --- |
| Exact mode/reference file structure | Needs implementation-level detail. | Define in spec or dev-workflow plan before moving files. |
| Whether `local-change-implementer` remains a standalone runtime skill or only a sub-skill | It can be useful directly, but also acts as lower-level execution for slices. | Keep it as standalone unless implementation complexity proves otherwise. |
| Whether test implementation deserves a future skill | The likely need is executable test creation, not test design. | Defer to separate requirement for `test-implementer`. |

## Recommended Next Skill

Use `dev-workflow` after user decisions are confirmed.

Expected downstream stages:

1. `spec-author`: decide whether an implementation spec is needed for the migration file map and mode contracts.
2. `dev-workflow`: plan and execute the implementer taxonomy migration.
3. `ai-context-governance`: execute confirmed skill rename/move migration and wrapper/index sync.
4. Optional `ddd-ca-hex-architect`: review command/query/reactor mode contracts if architectural constraints become ambiguous.

## References

- `.ai/assets/skills/staged-refactor-implementer/skill.yaml`
- `.ai/assets/skills/tactical-refactor-implementer/skill.yaml`
- `.dev/guides/ai-collaboration-guides/STAGED-REFACTOR-IMPLEMENTER-SKILL-GUIDE.md`
- `.dev/guides/ai-collaboration-guides/TACTICAL-REFACTOR-IMPLEMENTER-SKILL-GUIDE.md`
- `.ai/assets/skills/dev-workflow/references/capability-profile.md`
- `.ai/assets/skills/dev-workflow/references/routing-playbook.md`
- `.ai/assets/skills/command-use-case-implementer/skill.yaml`
- `.ai/assets/skills/query-use-case-implementer/skill.yaml`
- `.ai/assets/skills/reactor-implementer/skill.yaml`
