# Repository Structure Sync Report

## Metadata

- workflow_id: `2026-07-13-repo-structure-sync`
- owner_skill: `repo-structure-sync`
- status: `completed`
- created_at: `2026-07-13T21:12:28+08:00`
- updated_at: `2026-07-13T21:12:28+08:00`
- template_source: `.ai/assets/skills/repo-structure-sync/references/output-contract.md`
- template_version: `1.0`

## 1. Docs Updated

- Rebuilt root `README.md` and added `README.en.md` from current product facts.
- Corrected repository identity and navigation in `AGENTS.md` and `agents.zh-tw.md` while preserving framework collaboration rules.
- Rebuilt `.dev/ARCHITECTURE.md`, tech-stack requirements, `.dev` indexes, workflow discovery, and operations/spec discovery boundaries.
- Restored target-specific Products, Orders, and Inventory requirements, production specs, test designs, operations docs, and the Orders place-order problem frame from Git history, then updated obsolete contract terminology and status claims against current code.

## 2. Project Config Generated or Deferred

Generated `.dev/project-config.yaml` from the canonical repo-structure-sync shape using solution, project, source, test, tool, and Compose evidence. Historical credentials, connection strings, ports, unrelated frontend claims, and source-repository database facts were not restored.

## 3. Inferred or Missing Truth

- RabbitMQ inventory request/reply is incomplete because Inventory has no RabbitMQ `inventory.requests` listener.
- `products.integration.events` is configured, but current Product use cases are not confirmed to publish product integration events.
- Inventory has no test project; several restored test specs are explicitly marked planned or partial.
- Retry, dead-letter, replay, idempotency, and some consumer ownership remain incomplete.
- `Lab.SharedKernel` is an empty placeholder project.

## 4. Template Facts Removed or Preserved

- Removed copied source-repository backlog items and their broken workflow references.
- Removed residual empty source-workflow directories from the working tree; retained two target legacy workflows and the current locator-backed workflow.
- Kept the Payments problem frame absent because no Payments source, contract, project, or test evidence exists.
- Preserved reusable `.ai` assets, governance standards, skill routing, and runtime wrappers.
- Restored executable Git modes for the 14 retained shell assets required by the refreshed context validator.

## 5. Recommended Next Step

- Use `spec-compliance-validator` only when a specific restored behavior is selected for a 100% implementation/test compliance gate.
- Use a bounded development workflow to complete RabbitMQ reservation routing or intentionally retire the incomplete profile.
- Add Inventory tests and promote planned test specs as implementation work is authorized.

## Validation

- `git diff --cached --check`
- JSON parse: 10 domain specs
- YAML parse: `.dev/project-config.yaml` and five Orders problem-frame files
- obsolete restored terminology scan: no matches
- `python .ai/scripts/validate-workflow-artifacts.py`
- `python .ai/scripts/validate-ai-context.py`
- `python .ai/scripts/validate-shell-assets.py`
- `.ai/scripts/check-all.sh --quick`: 6/6 required checks passed; analyzer tests 47/47 and validation tests 2/2 passed
