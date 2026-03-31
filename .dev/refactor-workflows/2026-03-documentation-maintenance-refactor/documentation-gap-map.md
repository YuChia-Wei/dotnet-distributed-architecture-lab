# Documentation Inventory and Gap Map

## Metadata

- Workflow: `2026-03-documentation-maintenance-refactor`
- Stage: `Stage 2 - document inventory and gap map`
- Scope: `.dev/` and `.ai/`
- Goal: evaluate whether the current documentation system is sufficient to maintain a distributed DDD + CA + Hex Architecture system

## Assessment Scale

- `Sufficient`: enough to support ongoing maintenance with only local improvements
- `Partial`: useful foundation exists, but a maintainer still lacks critical truth
- `Conflicting`: guidance exists but is ambiguous, stale, or internally inconsistent
- `Missing`: no usable project truth for this maintenance domain

## Domain Inventory

| Domain | Current State | Assessment | Evidence | Maintenance Impact |
| :--- | :--- | :--- | :--- | :--- |
| Documentation governance and placement rules | Strong folder separation and placement rules exist | `Sufficient` | `.ai/DIRECTORY-RULES.MD`, `.ai/INDEX.MD`, `.dev/README.MD`, `.dev/guides/README.MD` | Maintainers can usually decide where new knowledge belongs |
| Refactor workflow artifact model | Plan/task/report structure exists and now explicitly supports document workflow | `Sufficient` | `.dev/refactor-workflows/README.MD`, `AI-REFACTORING-SKILL-CONTRACTS.md`, `AI-COLLABORATION-WORKFLOW-GUIDE.md` | Multi-stage doc work can be tracked without inventing ad hoc structure |
| Architecture principles | Repo-wide DDD + CA + CQRS + Hex + MQ-first constraints are documented | `Partial` | `.dev/ARCHITECTURE.MD`, `.ai/assets/skills/ddd-ca-hex-architect/references/architecture-playbook.md`, ADR index | Enough to preserve direction, not enough to explain current system reality per bounded context |
| ADR coverage | ADR set is broad and useful | `Partial` | `.dev/adr/INDEX.md` plus ADR files | Decision history exists, but maintainers still need synthesized system maps and current-state docs |
| Project structure and layering | Strong structure guidance exists | `Sufficient` | `.dev/standards/project-structure.md` | Useful for implementation placement and dependency direction |
| Requirements | Only guide/template level coverage exists | `Missing` | `.dev/requirement/REQUIREMENT-GUIDE.MD`, `.dev/requirement/TECH-STACK-REQUIREMENTS.MD` | No project-specific business capabilities, personas, acceptance criteria, or NFR truth |
| Specifications | Only guide/organization rules exist; no real specs found under `.dev/specs/` | `Missing` | `.dev/specs/SPEC-GUIDE.MD`, `.dev/specs/SPEC-ORGANIZATION-GUIDE.MD` | Agents and maintainers cannot trace use cases and aggregates from authoritative specs |
| Bounded context map and ownership | No clear current-state context map or ownership matrix found | `Missing` | no dedicated context-map or ownership docs under `.dev/` | Hard to maintain BC boundaries, integration ownership, and language separation |
| Event catalog and MQ topology | Architecture says MQ-first, but no consolidated event catalog or topic/queue ownership docs were found | `Missing` | architecture/playbook mention MQ-only, but no catalog doc under `.dev/` | High risk for integration drift, replay ambiguity, and contract sprawl |
| Runtime operations and incident handling | No operational runbooks or failure-mode docs found | `Missing` | no `.dev/operations/`, runbook, replay, dead-letter, or idempotency playbooks found | Distributed-system maintenance remains under-documented |
| Lessons learned / maintenance feedback | Lessons area is empty | `Missing` | `.dev/lessons/` empty | Failures and refactor learnings are not being fed back into the knowledge base |
| Coding and implementation standards | Rich standards/examples/guides exist | `Partial` | `.dev/standards/`, `.dev/guides/design-guides/`, `.dev/guides/implementation-guides/` | Strong for implementation patterns, weak for project-specific maintenance truth |
| AI asset portability and routing | Strong reusable asset structure exists | `Sufficient` | `.ai/assets/`, `.ai/assets/skills/`, `.ai/assets/sub-agent-role-prompts/`, `.ai/assets/shared/` | Agent reuse is well-supported |
| AI asset alignment with current .NET reality | Legacy Java/Spring/JPA terminology remains in high-traffic docs and scripts | `Conflicting` | `.dev/project-config.yaml`, `.ai/scripts/README.md`, Spring/JPA references in guides/scripts | Humans and agents can misread which rules are active vs historical |
| Validation and review automation | Many scripts/checks exist, but several still expose legacy names or pending translation status | `Conflicting` | `.ai/scripts/check-all.sh`, `.ai/scripts/code-review.sh`, `.ai/scripts/README.md` | Validation exists, but trust is reduced when names and semantics do not match the active stack |

## Key Findings

### 1. The repository is strong on workflow scaffolding but weak on project truth

The current docs explain how to collaborate, structure code, and route AI work. They do not yet explain the current business capability map, bounded context boundaries, aggregate ownership, or operational behavior of the distributed system in enough detail for maintenance.

### 2. Missing requirement/spec content is the highest-value gap

The absence of real requirement docs and real aggregate/use-case specs means later code refactors or AI-driven implementation will continue guessing from structure rules instead of from project truth.

### 3. Distributed runtime maintenance is under-documented

MQ-first integration is a hard constraint, but there is no consolidated event catalog, topology map, replay policy, idempotency guide, or dead-letter/runbook material. This is the largest maintainability gap for a distributed system.

### 4. .NET and legacy Java terminology are still mixed

The repo contains real .NET guidance, but active docs still include `jpa`, `spring`, `bean`, and `jdbc` wording in places that appear operational rather than historical. This weakens source-of-truth clarity.

### 5. The lessons feedback loop is missing

Without documented lessons or incident summaries, the doc system cannot accumulate operational knowledge over time.

## Prioritized Gaps

### Priority 0: source-of-truth ambiguity

- Normalize `.NET` vs legacy Java/Spring/JPA terminology in current-state docs
- Clarify when a document is historical translation context versus active guidance

### Priority 1: requirement and spec truth

- Add project-specific requirement docs by business capability or bounded context
- Add actual aggregate/use-case specs under `.dev/specs/`

### Priority 2: distributed-system runtime knowledge

- Add context map
- Add event catalog and contract ownership matrix
- Add MQ topology and integration ownership
- Add idempotency, replay, retry, dead-letter, and operational runbooks

### Priority 3: maintenance feedback capture

- Start populating `.dev/lessons/` with incident, migration, and refactor lessons

### Priority 4: AI alignment

- Update `.ai` assets and validation guidance to consume the newly created `.dev` truth
- Remove legacy names from high-traffic script docs where they misrepresent active behavior

## Proposed Stage Mapping

| Next Stage | Focus | Primary Output |
| :--- | :--- | :--- |
| Stage 3 | Terminology normalization and source-of-truth cleanup | edited guides/config/script docs with explicit active-vs-historical wording |
| Stage 4 | Requirement/spec completion | project-specific requirement docs and aggregate/use-case specs |
| Stage 5 | Distributed runtime maintenance docs | context map, event catalog, MQ topology, runbooks |
| Stage 6 | AI asset alignment | updated `.ai` guidance and validation/routing references |

## Recommended Document Additions

### Under `.dev/requirement/`

- bounded-context capability overview
- project-wide non-functional requirements
- integration constraints and ownership

### Under `.dev/specs/`

- aggregate directories with entity/usecase specs
- controller/adapter specs where API or consumer behavior matters

### New documentation area to consider

- `.dev/operations/`
  - event-catalog.md
  - mq-topology.md
  - replay-and-idempotency-guide.md
  - dead-letter-runbook.md
  - incident-response-checklist.md

## Exit Criteria for the Overall Workflow

This documentation refactor should only be considered complete when:

- maintainers can locate the active source of truth for each bounded context
- requirement/spec docs exist for the main business capabilities
- distributed runtime behavior is documented enough for troubleshooting and safe change planning
- `.ai/` assets route to active .NET truth without misleading legacy terminology
- new incidents and refactor learnings have a durable home in the documentation system
