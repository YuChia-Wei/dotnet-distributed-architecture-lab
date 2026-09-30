# Project Knowledge Index

This catalog describes the distributed-commerce lab's current project knowledge. Reusable package guidance is linked separately; folder presence does not prove adoption or execution.

## Project entries and adopted policies

- [Purpose and boundary](README.MD), [architecture](ARCHITECTURE.md) and `project-config.yaml` (generated inventory; verify source facts).
- [Target engineering rules](ai-context/TARGET-ENGINEERING-RULES.md), [trial framework contract](ai-context/CURRENT-FRAMEWORK.md) and [selected skill registry](ai-context/skills.md).
- [Standards navigation](standards/INDEX.MD), [Git flow](TEAM-GIT-FLOW-RULES.MD), [workflow gate](standards/WORKFLOW-GATE-POLICY.md), [workflow artifacts](standards/WORKFLOW-ARTIFACT-POLICY.md), [workflow handoff](standards/WORKFLOW-HANDOFF-POLICY.md) and [Git commits](standards/GIT-COMMIT-POLICY.md).

## Requirements, specifications and decisions

- [Current technology requirements](requirement/TECH-STACK-REQUIREMENTS.MD), [four-context overview](requirement/distributed-commerce-bounded-context-overview.md) and [reconstruction requirements](requirement/reconstructable-system-baseline.md).
- [Specs](specs/README.MD) and [spec catalog](specs/INDEX.MD): target production, test and reconstruction contracts; [current system extensions](specs/current-system-extension.md).
- [Procurement production specs](specs/domains/procurement/README.md) and [test specs](specs/tests/procurement/README.md).
- [ADR catalog](adr/INDEX.md): retained accepted/superseded project decisions.
- [Problem frames](problem-frames/INDEX.md): retained Orders/Inventory frames and target semantic tags.

## Actual operations and training

- [Operations area](operations/README.MD), [context map](operations/context-map.md), [event catalog](operations/event-catalog.md), [MQ topology](operations/mq-topology.md) and [runbooks](operations/runbooks/README.MD).
- [Procurement/supplier lab](operations/procurement-supplier-lab.md) and [commerce frontends](operations/commerce-frontend.md).
- [External API testing guide](guides/external-api-testing/README.md); presentation and supporting deliverables remain under `presentations/external-api-testing/`.

## Retained work and reusable authoring

- [Ordinary workflows](workflows/README.MD) and [workflow catalog](workflows/INDEX.MD) remain project-owned and manually governed; historical owners do not restore a portable orchestrator. Remaining backlog items and skill-owned record stores retain their own authority; owner-deleted generic backlog/v2 navigation is not recreated.
- [AI packages](../.ai/INDEX.MD), [engineering-common guidance](../.ai/core/knowledge/engineering-common/README.md) and [.NET guidance](../.ai/core/knowledge/dotnet-backend/README.md).
- [Requirements authoring](../.ai/core/skills/requirement-author/references/requirement-guide.md), [spec authoring](../.ai/core/skills/spec-author/references/spec-guide.md) and [ADR guidance](../.ai/core/skills/adr-author/references/WHEN-TO-CREATE-ADR.MD). Target-customized spec/test guidance remains under specs/.
- [Domain-language templates](../.ai/core/knowledge/engineering-common/domain-language/README.MD) and [operations authoring](../.ai/core/knowledge/engineering-common/README.md) replace generic .dev scaffolds. Package templates do not establish project vocabulary or operational facts.
