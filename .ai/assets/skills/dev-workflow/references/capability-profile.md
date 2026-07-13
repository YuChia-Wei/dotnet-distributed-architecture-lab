# Dev Workflow Capability Profile

This profile maps generic `dev-workflow` capability slots to this repository's concrete skills and local conventions.

Machine-readable source: [capability-profile.yaml](capability-profile.yaml). This
document explains the profile; the YAML file owns deterministic slot mappings.

The core `dev-workflow` skill should stay publishable. Repository-specific skill names belong in this profile.

## Profile Identity

- Profile name: `ai-collaboration-prompts-dotnet-backend`
- Repository role: AI collaboration knowledge base and .NET backend context framework
- Workflow artifact root: `.dev/workflows/<workflow-id>/`
- Commit policy: `.dev/standards/GIT-COMMIT-POLICY.md`
- Workflow gate policy: `.dev/standards/WORKFLOW-GATE-POLICY.md`

## Capability Mapping

| Capability slot | Local skill | Use when |
| --- | --- | --- |
| `workflow-orchestration` | `dev-workflow` | The task needs stage planning, workflow artifacts, skill routing, validation checkpoints, or commit checkpoints. |
| `requirements` | `requirement-author` | Rough notes, stakeholder inputs, or code facts need to become `.dev/requirement/`-aligned requirement docs. |
| `specification` | `spec-author` | Requirement truth needs to become retained specs under `.dev/specs/`. |
| `problem-framing` | `problem-frame-author` | Requirement, spec, code, or tests need a first problem-frame draft. |
| `architecture` | `ddd-ca-hex-architect` | The task needs DDD, Clean Architecture, CQRS, ports/adapters, bounded context, aggregate, or .NET backend architecture direction. |
| `test-design` | `bdd-gwt-test-designer` | The task needs Given-When-Then scenarios, assertion points, or test design notes. |
| `implementation` | `slice-implementer` | A bounded implementation slice is ready, using command, query, reactor, generic, remediation, or refactor mode as needed. |
| `local-change` | `local-change-implementer` | A local class, object, method, symbol, SQL/ORM, or direct-call-site technical change is ready. |
| `review` | `code-reviewer` | .NET backend code or dotnet-backend implementation guidance needs review. |
| `compliance-validation` | `spec-compliance-validator` | Problem-frame workflows need a 100% coverage gate. |

## Quality Boundary

- This profile covers the software and product development lifecycle only. AI context audit, AI context governance, documentation-only cleanup, and repository initialization use their own skill-owned workflow contracts.
- Full local workflow quality depends on the mapped downstream skills and repository standards.
- If a mapped skill is unavailable, `dev-workflow` should switch that stage to fallback-mode instead of pretending the specialist review, design, or implementation was performed.
- Fallback-mode output is suitable for planning, handoff, and minimum viable checklist coverage. It is not equivalent to a specialist skill result.

## Profile Update Rules

- Add or change mappings in `capability-profile.yaml`, then synchronize this explanatory table before changing runtime wrappers or root routing tables.
- Keep capability names generic.
- Keep local skill names in this profile or root routing docs, not in the portable core contract.
- If a downstream skill is renamed, update this profile and run reference searches.
