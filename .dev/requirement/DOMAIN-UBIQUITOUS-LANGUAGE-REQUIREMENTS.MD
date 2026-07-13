# Domain Ubiquitous Language Requirements

## Metadata

- Version: 0.1
- Date: 2026-06-08
- Owner: YuChia-Wei
- Scope: In
  - Define a repository area for domain ubiquitous language templates, standards, and target-repository vocabulary.
  - Support DDD-style domain language without mixing it with technical glossary work.
  - Define how copied template context should avoid carrying source-repository domain terms into target repositories.
- Scope: Out
  - Do not create a broad technical glossary for DDD, Clean Architecture, Hexagonal Architecture, CQRS, or .NET backend terms in this requirement.
  - Do not define product-specific domain vocabulary for a real product.
  - Do not create a new terminology skill yet.

## Implementation Outcome

- Status: Implemented
- Completed: 2026-06-09
- Workflow: `.dev/workflows/2026-06-implementer-taxonomy-domain-language/`
- Result:
  - `.dev/domain-language/` now contains the human-facing boundary guide and templates;
  - `repo-structure-sync` treats filled domain language as target-repository truth;
  - technical glossary and terminology skill remain deferred.

The original requirement wording below is preserved as decision history. Future-tense acceptance criteria should be read as completed outcomes unless explicitly listed as deferred above.

## Context & Goals

This repository uses many DDD, Clean Architecture, Hexagonal Architecture, CQRS, and .NET backend concepts. Technical terminology may eventually need a glossary, but that work has source-of-truth and token-cost tradeoffs. The immediate need is narrower: establish how actual domain ubiquitous language should be stored and governed when this context framework is used in target repositories.

Domain ubiquitous language is different from a technical glossary. It describes the business/domain vocabulary of a specific target repository or bounded context. If this repository provides templates, it must avoid leaking historical or source-repository domain terms into new target repositories.

Goals:

- Establish a storage area for domain ubiquitous language templates and target-repository domain vocabulary.
- Keep domain language separate from technical glossary and implementation standards.
- Provide a template that target repositories can fill with their actual bounded-context language.
- Define migration rules for `repo-structure-sync` so copied source-repository domain terms are removed, rewritten, or explicitly marked as examples.
- Avoid creating a dedicated terminology skill before there is repeated terminology workflow demand.

## Personas

- Human maintainer
  - Wants a clear place to put target-repository domain language.
  - Wants to avoid confusing domain vocabulary with technical pattern vocabulary.
- AI agent
  - Needs to know whether a term is domain truth, technical vocabulary, template example, or stale copied context.
  - Must not invent target domain language from examples.
- Target repository team
  - Needs templates for bounded context vocabulary without inheriting this repository's historical domain terms.

## Functional Requirements

### FR-1: Create Domain Language Storage Areas

The repository should define a domain language storage structure.

Recommended structure:

```text
.dev/domain-language/
  README.MD
  templates/
    bounded-context-language-template.md
    domain-event-language-template.md
    aggregate-vocabulary-template.md
```

The `.dev/domain-language/` area should be human-facing and target-repository oriented.

If agent-facing reusable fragments are later needed, they should be separate from target domain truth.

### FR-2: Define Domain Language Boundary Rules

The domain language area should define:

- what counts as domain ubiquitous language;
- what counts as a template;
- what counts as stale copied source-repository vocabulary;
- how to distinguish business terms from technical terms;
- how to link to requirements, specs, ADRs, and architecture docs.

### FR-3: Provide Templates Only, Not Product Truth

This repository should provide templates for target repositories, not actual product vocabulary.

Templates should include sections such as:

- bounded context name;
- term;
- preferred English name;
- preferred Traditional Chinese name when human-facing usage is needed;
- definition;
- examples;
- not the same as;
- source evidence;
- related requirements/specs/events/aggregates;
- open questions.

### FR-4: Integrate With Repo Structure Sync

`repo-structure-sync` should treat domain language as target-repository truth.

When this framework is copied to another repository, `repo-structure-sync` should:

- remove source-repository domain vocabulary unless it is explicitly marked as a template example;
- initialize empty or placeholder domain language files when the target repo lacks domain terms;
- rebuild domain language only from target repo evidence or user-provided truth;
- avoid inventing terms from technical architecture examples.

### FR-5: Defer Technical Glossary

Technical glossary work should be deferred.

Deferred topics include:

- DDD / Clean Architecture / Hexagonal Architecture / CQRS pattern terms;
- .NET backend building block terms such as reactor, projection, repository, handler, archive, and inquiry;
- human-facing technical terminology guide.

Reason:

- Technical glossary can blur into implementation standards.
- It may not significantly reduce agent token usage.
- It may primarily help human learning, and team members can ask the AI directly when needed.

### FR-6: Avoid A Dedicated Terminology Skill For Now

The repository should not create a dedicated terminology skill yet.

Use existing skills:

- `ai-context-governance` for file placement, language policy, and context boundary management.
- `ddd-ca-hex-architect` for DDD semantic correctness.
- `repo-structure-sync` for target repo initialization and stale source-domain cleanup.
- `dev-workflow` for multi-stage implementation orchestration.

## Non-Functional Requirements

- Domain language documents should be concise enough for AI agents to read when needed.
- Templates should be human-facing and use Traditional Chinese Taiwan usage where helpful.
- Agent-facing rules should remain English if added under `.ai/`.
- Domain language must not become a substitute for requirements, specs, or implementation standards.
- The structure must be safe to copy into target repositories.

## Constraints & Assumptions

- This requirement intentionally defers technical glossary creation.
- This repository is a framework and knowledge base, not the source of truth for a real product domain.
- Target repositories may have their own domain language and should not inherit this repository's examples as truth.
- Current root README and agents docs already express the repository's framework purpose clearly enough; no root agents update is required in this requirement drafting pass.

## Domain / Business Rules

- Domain ubiquitous language belongs to the target product or bounded context.
- Template examples must be labeled as examples.
- Source-repository historical domain terms must not be treated as target repository truth.
- Technical pattern terms and domain terms must be stored and governed separately.
- AI agents must cite source evidence or mark assumptions when proposing domain terms.

## Acceptance Criteria

- A future implementation creates `.dev/domain-language/` with README and templates.
- The README explains the boundary between domain language, technical glossary, requirements, specs, and implementation standards.
- Templates support bounded context vocabulary, domain event vocabulary, and aggregate vocabulary.
- `repo-structure-sync` guidance is updated to treat domain language as target-repository truth.
- Technical glossary remains explicitly deferred.
- No dedicated terminology skill is created unless a later requirement justifies repeated terminology workflow automation.

## User Decisions Required

| Decision | Recommended approach | Why |
| --- | --- | --- |
| Storage root name | `.dev/domain-language/` | Clearer than glossary for target-repository ubiquitous language and avoids technical glossary confusion. |
| Include `.ai` agent-facing domain glossary now? | No | Domain language is target-repository truth and should start human-facing under `.dev`. |
| Create technical glossary now? | No | Risk of mixing terminology with implementation standards; token savings are uncertain. |
| Create terminology skill now? | No | Existing skills can govern this until repeated terminology workflow appears. |
| Update agents now? | No | Repository purpose is already clear; wait until domain-language structure exists and routing rules need a durable entry. |

## Recommended Next Skill

Use `dev-workflow` after user decisions are confirmed.

Expected downstream stages:

1. `ai-context-governance`: create domain language structure and update context boundary references.
2. `repo-structure-sync`: update migration boundary guidance for target repository domain language.
3. Optional `ddd-ca-hex-architect`: review DDD ubiquitous language semantics if templates include DDD-specific guidance.

## Repository Purpose Assessment

Current repository purpose is clear enough for this requirement stage.

Evidence:

- `README.md` states that the repository extracts and evolves software development knowledge, AI Agent context, skills, sub-agent prompts, and collaboration workflows.
- `README.md` states that the repository is not a product repository, but a portable AI collaboration framework.
- `AGENTS.md` states that the repository is an AI collaboration knowledge base and reusable context framework.
- `AGENTS.md` already separates universal AI context, tech-stack-specific context, and historical source-project facts.

Conclusion:

- Do not update `AGENTS.md`, `agents.zh-tw.md`, `README.md`, or `README.en.md` in this requirement-only pass.
- Reconsider root entry updates after the domain language structure and skill rename migration are implemented.

## References

- `README.md`
- `README.en.md`
- `AGENTS.md`
- `agents.zh-tw.md`
- `.dev/standards/AI-CONTEXT-BOUNDARY.md`
- `.ai/assets/skills/repo-structure-sync/references/migration-boundaries.md`
- `.dev/standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`
