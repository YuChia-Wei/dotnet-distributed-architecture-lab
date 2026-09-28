# External API testing team delivery

## Authority and execution boundary

Owner requested Traditional Chinese team presentation, architecture/sequence diagrams and reconciliation of current repository documentation on 2026-09-28. Owner explicitly authorized Issue creation, necessary records, PR, main integration and cleanup. Issue #20 binds AC01–AC05.

The owner separately approved a single manual documentation delivery record while the installed 0.19.0-rc.1 framework admission remains pending in Issue #15. This is a target-owned delivery record, not a manually fabricated v2 package record, framework invocation, admission, or policy adoption. Managed packages, bindings, gate status and previous completed workflow evidence stay unchanged. The orchestrator instructions were read but its operations are not invoked.

## Scope and acceptance

- AC01: Editable PPTX and PDF suitable for a roughly 20-minute team introduction, with speaker/demo guidance and primary-source citations.
- AC02: Maintainable architecture and sequence diagrams cover routing, native engines versus custom controls, per-request mock/proxy selection, timeout/reconcile, receiving/outbox/Inventory deduplication, and sales reservation.
- AC03: Reconcile current architecture, inventory, context map, event/topology documentation and discovery links. Explicitly delimit the older reconstruction baseline instead of implying it describes all newer modules.
- AC04: Validate diagrams, slides, links, inventory and bounded semantic accuracy against source/config or official references. Historical runtime results are historical, not rerun acceptance.
- AC05: Reviewed PR merged to main, Issue closed, own branches/worktrees removed. Docker/data and protected observability preserved; owner later permits starting dev services only if useful for screenshots.

Excluded: business behavior changes, dependency upgrades, production authentication implementation, framework activation, performance/model-cost claims and full clean-room reconstruction.

## Tasks and delegation

All rows belong to this workflow, use owner_skill=project-documentation-delivery, template_source=.dev/standards/WORKFLOW-ARTIFACT-POLICY.md, template_version=1.0. Exact invocation and result messages are retained in the conversation. Each worktree has one tracked writer. Root is final integration owner.

| task_id | Deliverable | Executor | model | reasoning_effort | status | Dependency |
| --- | --- | --- | --- | --- | --- | --- |
| T001 | Architecture/sequence/comparison/demo guide | /root/team_guide_author | gpt-6-sol | high | in_progress | Approved Issue #20 |
| T002 | Editable presentation, PDF and speaker notes | /root/team_slide_author | gpt-6-sol | high | in_progress | Approved Issue #20 and source baseline |
| T003 | Current repo document reconciliation | /root/repo_doc_reconciliation | gpt-6-sol | high | in_progress | Approved Issue #20 |

Tasks are independent production units. Review, checks and provider delivery are lifecycle steps, not invented extra development tasks. Task timestamps are the creation/update metadata below until the next progress checkpoint. Root retains its effective configured fallback attribution separately where active runtime identity is unavailable.

## Source and discovery baseline

Base main/origin/main: f2bb5750fb01b4508cdae8328becc6581212a4ab. No source/config behavior changes planned. MCP graph was queried first; it lacks Procurement/SupplierMock/frontend coverage and returns old three-context architecture. It is discovery only; use explicit Git-tracked src/Procurement, src/Inventory, src/Order, samples/SupplierMock, samples/SupplierSandbox, src/BC-Contracts, MQArchLab.slnx and docker-compose paths for current evidence. No absence conclusion comes from the stale graph.

## Review and continuation

Current action: await the three bounded Sol deliverables; root checks source claims, renders every diagram, inspects slide images, reconciles inventories/links, and repairs findings before integration. No runtime test pass is inferred from a documentation check. Publish/merge only after concrete delivery artifacts and review are complete, under existing owner authorization. Preserve actual failed checks and residuals in acceptance-report.md.

One branch remains the coherent delivery/rollback unit; default no-ff integration applies. Supporting worktrees/commits belong to this same workflow, not separate workflows.

created_at: 2026-09-28T23:11:20.7417376+08:00
updated_at: 2026-09-28T23:11:20.7417376+08:00
