# Implementation Plan: Publish Product Stock Deducted Event

**Branch**: `001-publish-product-stock` | **Date**: 2025-09-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `C:\Github\YuChia\dotnet-mq-arch-lab\specs\001-publish-product-stock\spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
This feature will implement the logic for deducting product stock after an order is placed. The `SaleProducts.Consumer` will handle the `OrderPlaced` event, deduct stock, and publish a `ProductStockDeducted` event on success or a `ProductStockDeductionFailed` event on failure. The `SaleOrders.Consumer` will then consume these events to update the order status accordingly.

## Technical Context
**Language/Version**: C# / .NET 8
**Primary Dependencies**: WolverineFx, MediatR, Marten, RabbitMQ, xUnit, ASP.NET Core
**Storage**: PostgreSQL
**Testing**: xUnit
**Target Platform**: Linux (Docker)
**Project Type**: Web Application (backend services)
**Performance Goals**: N/A for this feature.
**Constraints**: N/A
**Scale/Scope**: This feature is scoped to the Order and Product services.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 3 (BC-Contracts, SaleProducts, SaleOrders)
- Using framework directly? Yes (WolverineFx, ASP.NET Core)
- Single data model? Yes, for events.
- Avoiding patterns? Yes, no unnecessary patterns introduced.

**Architecture**:
- EVERY feature as library? The logic will be within existing service projects, which aligns with the existing architecture.
- Libraries listed: `Lab.MessageSchemas.Products` (new), `SaleProducts.Applications`, `SaleProducts.Domains`, `SaleOrders.Applications`.
- CLI per library: N/A
- Library docs: N/A

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes, tasks will be ordered to write tests first.
- Git commits show tests before implementation? This will be followed during implementation.
- Order: Contract→Integration→E2E→Unit strictly followed? Yes.
- Real dependencies used? Yes, tests will use a real test database.
- Integration tests for: new libraries, contract changes, shared schemas? Yes, for the new events.
- FORBIDDEN: Implementation before test, skipping RED phase. Yes.

**Observability**:
- Structured logging included? Yes, will be added.
- Frontend logs → backend? N/A
- Error context sufficient? Yes, failure events will include a reason.

**Versioning**:
- Version number assigned? N/A for this feature.
- BUILD increments on every change? N/A
- Breaking changes handled? No breaking changes.

## Project Structure

### Documentation (this feature)
```
specs/001-publish-product-stock/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
│   └── ProductStockEvents.cs
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 2: Web application (when "frontend" + "backend" detected)
# This project is structured by bounded context, not frontend/backend.
src/
├── BC-Contracts/
│   └── Lab.MessageSchemas.Products/ (NEW)
├── Order/
│   ├── DomainCore/
│   │   └── SaleOrders.Applications/ (MODIFIED)
│   └── Presentation/
│       └── SaleOrders.Consumer/ (MODIFIED)
└── Product/
    ├── DomainCore/
    │   ├── SaleProducts.Applications/ (MODIFIED)
    │   └── SaleProducts.Domains/ (MODIFIED)
    └── Presentation/
        └── SaleProducts.Consumer/ (MODIFIED)
```

**Structure Decision**: The existing project structure will be used.

## Phase 0: Outline & Research
Completed. See `research.md`.

## Phase 1: Design & Contracts
Completed. See `data-model.md`, `contracts/`, and `quickstart.md`.

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Create a new project `Lab.MessageSchemas.Products` for the new integration events.
- Add the `ProductStockDeducted` and `ProductStockDeductionFailed` event definitions.
- In `SaleProducts.Applications`, create a `DeductStockCommand` and its handler.
- The handler will perform the stock deduction logic and publish the success or failure event.
- In `SaleProducts.Consumer`, modify the `OrderPlaced` event handler to dispatch the `DeductStockCommand`.
- In `SaleOrders.Consumer`, create new handlers for `ProductStockDeducted` and `ProductStockDeductionFailed` events.
- These handlers will update the order status.
- Add unit and integration tests for all new logic.

**Ordering Strategy**:
1.  Create the new `Lab.MessageSchemas.Products` project and events.
2.  Write integration tests in `SaleOrders.Consumer` that expect the order status to be updated. These will fail initially.
3.  Write integration tests in `SaleProducts.Consumer` that expect the stock deduction events to be published. These will fail initially.
4.  Implement the `DeductStockCommand` and its handler in `SaleProducts.Applications`.
5.  Implement the event handlers in `SaleOrders.Consumer`.
6.  Make all tests pass.

**Estimated Output**: ~15-20 tasks.

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
No violations.

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
