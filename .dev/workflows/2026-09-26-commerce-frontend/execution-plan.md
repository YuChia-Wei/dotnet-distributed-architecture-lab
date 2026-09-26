# Execution ownership and continuation

created_at: 2026-09-26T06:15:44+00:00; updated_at: 2026-09-26T06:15:44+00:00

Workflow2026-09-26-commerce-frontend; Issue18; parent root integration owner. One workflow, one PR/rollback unit. Primary record `.dev/workflows-v2/wf-0fa43e8dc60f4683ae1036abde90494b.workflow.json`.

- T001 root: requirements, architecture, UI/API/GWT baseline and review criteria.
- T002 GPT-6 Sol/high: operations application, own `src/Frontend/Web` only; build/unit/component tests and truthful report.
- T003 GPT-6 Sol/high: administration application, own `src/Frontend/Admin` only; build/unit/component tests and truthful report.
- T004 GPT-6 Sol/high: bounded Microcks control adapter/tests, YARP/Compose frontend overlay, startup helper and runbook. Own `samples/SupplierMock/SupplierMock.WebApi`, `tests/SupplierMock.Tests`, `docker-compose`, `scripts/frontend-lab`, `.dev/operations/commerce-frontend.md`. Existing domain changes require parent review of concrete necessity.
- T005 root: integrate, review exact source, real Docker/browser journey acceptance, retain evidence and model observations. Provider/PR/merge/cleanup are lifecycle steps under owner authorization, no separate workflow.

One tracked writer per worktree. Workers are not alone in the repo and must preserve others' changes, remain inside ownership, read baseline docs plus applicable skill/target rules, and not push/PR/merge/Docker deploy/provider mutate. Parent owns commits outside worker scope and integration. Directly authorized ordinary fixes continue; no claims of testing until commands ran. Child runtime supports actual Sol attribution; parent configured gpt-6-astra/ultra. Cost/token data unavailable unless runtime supplies it; task differences preclude model ranking.

Scope discoveries: graph indexed but older and missing Procurement; exact source paths used after insufficient graph result. Existing main8213a9e and origin matched. Tool-created managed worktrees use F:/git-worktree. Old pilot checkout belongs to another workflow and remains untouched. Framework authority/pins remain unchanged; existing historical inventory omits recent Procurement and must yield to source/Compose. Frontend has no adopted technology-specific rule packet; generic slice method plus explicit requirements apply, do not invent .NET rules for Vue. T004 .NET work resolves current target selector before editing.
