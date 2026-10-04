# Target policy index

[AGENTS.md](../../AGENTS.md) owns the root reading order.
[Target engineering rules](../ai-context/TARGET-ENGINEERING-RULES.md) own adopted
rule statements and applicability; this index adds navigation only.

| Concern | Retained owner |
| --- | --- |
| Context placement and repository-backed evidence | [AI context boundary](AI-CONTEXT-BOUNDARY.md) |
| Canonical language and translation parity | [Language policy](AI-CONTEXT-LANGUAGE-POLICY.md) |
| Baseline, target and consumer ownership | [Ownership policy](AI-CONTEXT-OWNERSHIP.md) |
| Framework version and target upgrade provenance | [Version policy](AI-CONTEXT-VERSION-POLICY.md) |
| Assessment identity and records | [Assessment policy](ASSESSMENT-ARTIFACT-POLICY.md) |
| Workflow selection and authorization | [Workflow gate](WORKFLOW-GATE-POLICY.md) |
| Workflow locator, tasks and completion | [Artifact policy](WORKFLOW-ARTIFACT-POLICY.md) |
| Cross-session or runtime continuation | [Handoff policy](WORKFLOW-HANDOFF-POLICY.md), [machine contract](WORKFLOW-HANDOFF-POLICY.yaml) |
| Branch and integration boundaries | [Team Git flow](../TEAM-GIT-FLOW-RULES.MD) |
| Commit structure and actual attribution | [Commit policy](GIT-COMMIT-POLICY.md), [machine contract](GIT-COMMIT-POLICY.yaml) |
| Target technology choices | [Technology selection](TECHNOLOGY-SELECTION-POLICY.md), [selection schema](schemas/technology-selection.schema.yaml) |
| Existing workflow record templates | [Workflow locator](templates/workflow-locator-template.yaml), [handoff checkpoint](templates/workflow-handoff-checkpoint-template.yaml) |

The [project configuration](../project-config.yaml) retains required GitHub
work-item binding and merge gate, and unconfigured framework/local/CI validation.
Follow the exact applicable policy and recorded owner authorization; an index
entry, package installation or structural check is not a gate pass.
