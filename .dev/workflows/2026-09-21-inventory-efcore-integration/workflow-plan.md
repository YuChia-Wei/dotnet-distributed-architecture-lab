# Inventory EF Core integration

## Workflow Metadata

- `workflow_id`: `2026-09-21-inventory-efcore-integration`
- `plan_id`: `development-plan-2026-09-21-inventory-efcore-integration`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-09-21-inventory-efcore-integration`
- `base_branch`: `main`
- `status`: `completed`
- `created_at`: `2026-09-21T08:53:07+08:00`
- `updated_at`: `2026-09-21T08:53:07+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- Work item: #14. User authorization: 2026-09-21 conversation (implementation, Docker verification, merge and push main).

## Outcome and scope

Inventory becomes the EF Core practice bounded context; Products and Orders retain Dapper. Integrate the already finalized v0.18 upgrade and existing sample history. Preserve API/event contracts, stored rows, reservation idempotency and stock/outbox atomicity. See [design](design.md).

## Execution and delivery choice

One cohesive delivery and one implementation task: persistence mapping/adapters/DI and behavioral tests share one rollback and integration boundary. Workflow value is the explicit persistence architecture decision, independent review handoff, Docker validation and durable continuation state; validation and Git operations are lifecycle steps, not invented tasks. Branch starts from the pushed sample checkpoint `a27fdb3`, which descends from unchanged main `76ffd24`; existing upgrade PR #13 is already merged there. Preserve that history and use `--no-ff` into main.

## Stages and authorization

1. Architecture: `ddd-ca-hex-architect`, design mode, direct; accepted owner direction, routine transaction choices documented here.
2. Implementation: `slice-implementer`, generic refactor, INV-001; scope authorized by owner request.
3. Validation and review: target test execution and `code-reviewer`; no spec-compliance claim (not selected).
4. Integration: after passing checks merge main and push, both explicitly authorized. Tracking closure is separate.

## Evidence and execution ownership

Parent is integration owner. Routine read-only discovery delegated to `/root/inventory_persistence_map`; writes prohibited. Exactly one tracked writer at a time. No terminal/independent acceptance is inferred from discovery. Architecture and implementation effective rules resolved with verified freshness at v0.18.0. The initial architecture CLI used invalid selector spelling; corrected to the registered architecture/direct/dotnet-backend/architecture-decision route before design. Rules are unchanged.

## Validation strategy

- Deterministic Inventory tests and solution build.
- Opt-in actual PostgreSQL tests for stock/outbox atomicity, rollback, reservation replay and races; extend coverage for EF mapping/query/DI as needed.
- Existing `mqarchlab-pr5-integration` Compose (base + override + verification), preserve volumes; rebuild affected hosts/test image and exercise real Kafka commerce flow.
- Existing EF/Wolverine sample remains a native transaction teaching reference; its unchanged sample has historical 16/0/0 evidence, which is not a fresh integration pass.
- Target gate: `.dev/ai-context/tooling/validate-target-ai-context.py`, workflow artifacts and prospective commit range. Routine local policy is manual, CI unconfigured; these are explicit lifecycle checks.
- Full/long-running checks require clean committed subject and delegated execution contract; focused checks may run inline.

## Progress and handoff

Implementation and selected verification complete; see the completion evidence below. Final integration uses the closeout commit after its fresh checks, followed by merge and remote read-back.

## Completion evidence

Updated: 2026-09-21T09:19:42+08:00. INV-001 implementation and verification completed. [Verification record](evidence/verification.json) retains actual command results, original failures and corrections. At `cc25513626d1dea72aba56a5ce4a9541f12cef65`: all 122 .NET tests passed (Inventory 47, native sample 16, remaining product/domain tests 59), zero failures/skips. Commerce and both parallel-work modes passed. Non-author reviewer `/root/inventory_review` found no CRITICAL, MUST FIX or SHOULD FIX issues within the declared source/test/design scope. Source inspection confirmed Products, Orders and SQL schema files unchanged.

The first aggregate's product checks and target checks passed, but its commit-range command applied this workflow ID to inherited commits. Corrected target-owned commit checks passed 25 inherited/current commits and the one current-workflow commit separately. The failed aggregate is retained truthfully; a final frozen aggregate will use the corrected selection. The initial SDK cache and runner profile failures are retained, with material corrections documented.

This completion closes implementation/verification work, not an unobserved Git/provider event. Integration remains the explicitly authorized next step: verify this closeout commit, merge `--no-ff` into up-to-date main, validate the merge identity and push/read back origin/main. Final command receipts stay in ignored artifacts so recording the result does not mutate the validated tree. Issue #14 closeout remains a separate tracking decision.
