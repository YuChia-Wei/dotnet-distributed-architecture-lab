## Metadata

- `plan_id`: `refactor-plan-2026-03-documentation-maintenance-refactor`
- `owner_skill`: `ddd-ca-hex-architect`
- `status`: `active`

## Context

- Problem statement:
  - `.dev/` and `.ai/` already provide strong collaboration scaffolding, but they do not yet provide enough project-specific operational and domain knowledge to maintain a distributed DDD + CA + Hex Architecture system end-to-end.
  - The current refactor workflow contracts are generic enough for artifacts, but the staged execution guidance is still code-centric. If used as-is, later stages could incorrectly optimize for code-safe slices instead of documentation-governance slices.
- Current scope:
  - Documentation system rooted in `.dev/` and `.ai/`
  - Refactor workflow usage for document completion and document restructuring
  - Excludes production code refactoring in `src/` and `tests/` for this workflow
- Why refactor now:
  - Missing requirement/spec/runbook materials weaken long-term maintainability more than missing prompts.
  - Java/Spring/JPA legacy terminology still leaks into .NET documentation and AI assets, increasing ambiguity for humans and agents.
  - Future implementation workflows need clearer document sources of truth before more code is generated or refactored.

## Target Direction

- Target architecture summary:
  - Treat documentation completion as a first-class refactor workflow, with stages defined by source-of-truth boundaries rather than by code modules.
  - Use `.dev/` for project truth, decision records, requirements, specs, operational knowledge, and workflow artifacts.
  - Use `.ai/` for portable agent assets and only the minimum repo-aware routing material needed to consume `.dev/`.
  - Make documentation maintenance explicit across four layers:
    1. governance and workflow
    2. domain and requirement truth
    3. distributed-system design and runtime operations
    4. AI asset alignment and validation
- Key constraints:
  - Must follow workflow mode under `.dev/refactor-workflows/`.
  - Must prioritize document refactor workflow definition before broad document execution because current execution guidance is code-centric.
  - Must preserve the `.dev/` vs `.ai/` placement rules already established in the repository.
  - Must not treat prompt growth as a substitute for missing project facts.
- Non-goals:
  - No production code or test refactoring in this workflow.
  - No ADR rewrites unless required to remove direct contradiction or obsolete stack language.
  - No bulk migration of every legacy term in one stage without an inventory and ownership map.

## Stages

### Stage 1
- Goal:
  - Define a document-first refactor workflow that adapts existing refactor artifacts and execution rules for documentation work.
- Scope:
  - Refactor workflow rules, stage taxonomy, validation criteria, and task conventions for document changes.
- Non-goals:
  - Do not execute bulk content changes across `.dev/` and `.ai/` yet.
  - Do not rewrite existing guides wholesale.
- Risks:
  - If the workflow definition remains too abstract, later stages will drift back into code-oriented slicing.
  - Overdesigning the workflow will create process overhead without improving maintainability.
- Recommended implementer:
  - `ddd-ca-hex-architect`

### Stage 2
- Goal:
  - Produce a documentation inventory and gap map for maintainability of the distributed system.
- Scope:
  - Catalog current documents in `.dev/` and `.ai/`, identify what is authoritative, what is duplicated, what is stale, and what is missing.
- Non-goals:
  - Do not resolve every issue found in the inventory during this stage.
- Risks:
  - Inventory can become a file list instead of a maintainability analysis if gaps are not tied to ownership and use cases.
- Recommended implementer:
  - `staged-refactor-implementer`

### Stage 3
- Goal:
  - Normalize documentation terminology and source-of-truth boundaries for the .NET stack.
- Scope:
  - Remove or quarantine Java/Spring/JPA legacy terminology where it misrepresents the active architecture.
  - Reconcile `project-config.yaml`, script READMEs, and workflow/guides that currently mix .NET and legacy vocabulary.
- Non-goals:
  - Do not rewrite historically valid ADR references that are intentionally preserved as translation context.
- Risks:
  - Over-aggressive cleanup could erase useful migration context.
  - Under-scoped cleanup would leave critical ambiguity in the highest-traffic documents.
- Recommended implementer:
  - `staged-refactor-implementer`

### Stage 4
- Goal:
  - Fill project-specific requirement and specification gaps for bounded contexts and aggregates.
- Scope:
  - Add requirement documents for business capabilities and non-functional constraints.
  - Add actual aggregate/use-case specs under `.dev/specs/`.
  - Ensure docs are organized by bounded context and aggregate ownership.
- Non-goals:
  - Do not generate code from the new docs in this workflow.
- Risks:
  - Specs may become templates without real domain decisions if upstream capability definitions remain vague.
- Recommended implementer:
  - `ddd-ca-hex-architect`

### Stage 5
- Goal:
  - Add distributed-system runtime knowledge required for maintenance.
- Scope:
  - Event catalog, context map, integration ownership, MQ topology, failure modes, replay/idempotency rules, and operational runbooks.
- Non-goals:
  - Do not turn runbooks into environment-specific deployment manuals unless tied to a real operating scenario.
- Risks:
  - Missing runtime documentation will continue to block incident response and safe refactoring even if requirements/specs improve.
- Recommended implementer:
  - `ddd-ca-hex-architect`

### Stage 6
- Goal:
  - Align `.ai/` assets and validation scripts with the completed documentation system.
- Scope:
  - Update `.ai` routing references, README guidance, and validation expectations so agents consume the new `.dev` truth correctly.
- Non-goals:
  - Do not add new prompt families unless a documented maintenance use case requires them.
- Risks:
  - If `.ai/` is not aligned, agents will continue routing through stale or code-centric heuristics.
- Recommended implementer:
  - `staged-refactor-implementer`

## Validation Strategy

- Reviewer checkpoints:
  - Stage 1: confirm workflow mode is explicitly usable for documentation work and no step assumes code-only outputs.
  - Stage 2: confirm every major documentation gap is tied to a maintenance scenario, not just a missing file.
  - Stage 3: confirm terminology cleanup preserves migration context while removing active ambiguity.
  - Stages 4-5: confirm new docs materially improve domain understanding and distributed-system operability.
  - Stage 6: confirm AI assets now route to the correct project truth.
- Tests/validation expectations:
  - Document-level validation should use artifact completeness, source-of-truth clarity, terminology consistency, and workflow usability.
  - When scripts are involved, validation may include targeted doc lint/search checks, but script additions are secondary to content correctness.

## Notes

- Open questions:
  - Should requirement/spec coverage be tracked per bounded context or per aggregate first.
  - Should runtime operations docs live under `.dev/requirement/`, `.dev/specs/`, or a new `.dev/operations/` area.
  - Whether code-review workflow needs a document-review specialization or a separate checklist.
- Dependencies:
  - Existing placement rules in `.ai/DIRECTORY-RULES.MD`
  - Existing workflow contracts in `.dev/guides/ai-collaboration-guides/AI-REFACTORING-SKILL-CONTRACTS.md`
  - Existing architecture constraints in `.dev/ARCHITECTURE.MD` and related ADRs
