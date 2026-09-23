# Target framework binding and current checks

Owner decision: [the direct Issue 15 gate decision](../workflows/2026-09-23-framework-rc1-pilot/reconciliation-proposal.md#direct-target-gate-adoption-decision).
This document describes the selected target contract. Consult
[framework-binding.json](framework-binding.json) for its actual state.
A preparation or blocked state prohibits activation; file presence is insufficient.

## Authority and installation identity

The managed installation is identified by the exact candidate metadata and
installer-written .ai/framework.lock. A versioned candidate is not a published
release, release tag, or a verified stable upgrade route. The binding pins the
candidate selection/inventory/build bytes and, after successful installation,
the actual lock and complete engine pin. Never hand-edit the lock.

Retained provenance.yaml, customizations.yaml, effective-rules.yaml, both rule
catalogs and the twenty effective-rule packets identify the v0.18-derived target
rule and legacy-package baseline. They do not identify the new installation.
Their original versions, dates, meanings and hashes remain intact. Current
installation and target rule baseline are distinct explicit authorities.

The four retained customizations remain binding:

| Customization | Current target responsibility |
| --- | --- |
| CUST-DOTNET-MQ-GOVERNANCE | Issue-first scope, repository truth, scoped runtime metadata tracking, LF policy, explicit routes |
| CUST-DOTNET-MQ-VALIDATION | Applicable checks, exact dependency/authority pins, truthful outcomes and independent target review |
| CUST-DOTNET-MQ-REPO-TRUTH | Product and bounded-context architecture; retired tools remain inactive |
| CUST-DOTNET-MQ-EXECUTION-PROVENANCE-ADOPTION | Actual AI attribution, target cutover timestamps and the one exact historical attestation |

Package installation cannot override these subjects. In particular, Inventory's
EF Core and Products/Orders' Dapper choices remain separate. Preserve plain xUnit
v3 with GWT and the target BDDfy opt-out; select Moq or NSubstitute from the test
project's actual authority. Generic framework examples are not new target decisions.

## Codex routes and retained .NET rules

The candidate selects all eighteen packages and only its generated Codex adapter.
The thirteen replaced old Codex and thirteen old Claude entry directories are
withdrawn only with exact archived bytes outside active discovery. The old
ai-context-init/upgrader duties are retained only for their original published
legacy formats and recovery; they are not entry points for the new candidate.
Claude does not support this candidate. The target's active registry and root
instructions must state these boundaries before readiness can be established.

The new generic packages contain no built-in .NET extension. For target .NET work,
use the package's current instructions together with the target's explicit rule
binding. The binding's route_bindings select these existing target dimensions:

| Current package | Retained capability / modes and file types |
| --- | --- |
| slice-implementer | implementation: command, query, reactor, generic; selected C# production/test rows |
| local-change-implementer | local-change/direct: C# production/test, project, SQL, YAML configuration |
| code-reviewer | review/direct: .NET mixed review or C# review |
| bdd-gwt-test-designer | test-design/direct: Gherkin or C# test |
| spec-author | specification/direct: specification Markdown or JSON |
| ddd-ca-hex-architect | architecture/direct: architecture decision |
| requirement-author | requirements/direct: requirement Markdown |
| problem-frame-author | problem-framing/direct: problem-frame YAML |
| spec-compliance-validator | compliance-validation/direct: problem frame and .NET |

All twenty rows retain technology_profile=dotnet-backend, all fourteen loaded
rule IDs, their normative statements/digests and conditional applicability.
A loaded rule is not automatically applicable to every artifact; preserve its
actual predicate and selected evidence. Resolve the exact row before the governed
action. Unknown or mismatched dimensions fail closed; do not borrow an unrelated
architecture/review row for a different package.

The other nine packages have explicit project scope and no existing .NET selector:
adr, ai-context-auditor, ai-context-governance, diagnostic-analyst, lesson,
local-backlog, pr, software-development-orchestrator and standards-promotion.
This does not waive relevant target governance, product truth or decision authority.

For .NET code review, resolve the packet first, then load retained
.ai/assets/skills/code-reviewer/references/review-routing.yaml and only its selected
target-owned .NET references. For slice modes retain the selected old
slice-implementer mode/role/playbook dependencies as target implementation guidance,
without activating their old top-level skill wrapper or automatically spawning roles.
The retained compliance rules' 100% .NET gate remains separate from the new CBF
tool's structural record validation. Structural success alone is not .NET compliance.

## Explicit configuration and existing data

The seven configured packages use .ai/custom/framework.json only when explicitly
passed as project_config. The tools do not discover it automatically. Every
public request must name project_root, the installed package_root and that config.
Instruction-only packages have configuration=null and receive no invented settings.

New stores are .dev/lessons/records, .dev/adr/records, .dev/knowledge/promotions,
.dev/pull-requests, .dev/local-work-items, .dev/workflows-v2 and
.dev/problem-frames/records. Existing historical records keep their formats/paths.
README files are not records. Query success must include partial=false; explain
reports configuration with capability not-probed, not write readiness.

Lesson accept, ADR decide and promotion decisions require separately configured,
real project evidence. No decision adapters are fabricated by this pilot. Read
and ordinary draft capabilities do not grant decision authority. GitHub Issues
remain authoritative for this workflow; optional local backlog records do not
replace them or authorize external provider changes.

## Selected current verification

Run the target-owned command with the caller-selected immutable binding digest:

    python -I -B .dev/ai-context/tooling/validate-current-framework.py --binding-sha256 <review-subject-binding-sha256> --git-range <accepted-base>..HEAD

The command checks exact candidate/lock/managed bytes, eighteen Codex routes,
withdrawn entry history, retained target authority/dependency bytes, all twenty
actual resolver calls and the unchanged target Git overlay. Changing the binding
or its expected digest is a reviewed authority change, not automatic re-pinning.
A digest proves identity, not user approval.

Supporting validation also includes the seven installed public configuration/read
surfaces, relevant new record schema/behavior checks, raw candidate-to-index-to-
fresh-checkout parity, and this workflow's actual state. Python >=3.11,<4,
PyYAML >=6,<7, jsonschema >=4.18,<5 and referencing where required are checked as
actual runtime prerequisites for the selected package tools.

Independent review is a separate mandatory admission gate against one immutable
target subject, including the binding, current root/routes, custom configuration,
gate implementation and validation evidence. Follow the retained target role and
review-subject/lease contract selected for this adoption. A parent inventory or
this command's selected-checks-passed result cannot substitute for that review.
Any unresolved finding, missing/failed/pending review, subject/authority drift or
dirty admission checkout keeps activation pending.

Keep the old validate-target-ai-context.py and its pinned manifest/tests unchanged
as v0.18 historical and legacy-package support. Its old wrapper projections,
old backlog/workflow layout and package provenance do not validate the candidate.
Legacy assessment/workflow/shell validators retain their named historical scope;
a zero-check dependency result is not candidate dependency evidence. Source U001
does not suspend any target obligation. Report every selected check and residual
truthfully instead of relabeling old-package checks as current passes.
