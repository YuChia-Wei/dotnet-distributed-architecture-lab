# Implementation Plan: Cancel Sale Order


**Branch**: `002-saleorder` | **Date**: 2025-09-15 | **Spec**: [link to spec.md]
**Input**: Feature specification from `C:\Github\YuChia\dotnet-mq-arch-lab\specs\002-saleorder\spec.md`

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
This feature adds the functionality to cancel a sales order. When an order is canceled, its status is updated in the database, and an `OrderCancelled` integration event is published to the message queue.

## Technical Context
**Language/Version**: C# (.NET 8)
**Primary Dependencies**: Wolverine, Marten
**Storage**: PostgreSQL
**Testing**: xUnit
**Target Platform**: Docker Container
**Project Type**: Web Application
**Performance Goals**: N/A
**Constraints**: The cancellation operation must be idempotent.
**Scale/Scope**: This feature will be part of the existing `SaleOrders` bounded context.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 1 (SaleOrders.WebApi)
- Using framework directly? Yes
- Single data model? Yes
- Avoiding patterns? Yes

**Architecture**:
- EVERY feature as library? Yes, this will be part of the SaleOrders.Applications library.
- Libraries listed: SaleOrders.Applications - Application services for sales orders.
- CLI per library: N/A
- Library docs: N/A

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes
- Git commits show tests before implementation? Yes
- Order: Contract→Integration→E2E→Unit strictly followed? Yes
- Real dependencies used? Yes
- Integration tests for: new libraries, contract changes, shared schemas? Yes
- FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- Structured logging included? Yes
- Frontend logs → backend? N/A
- Error context sufficient? Yes

**Versioning**:
- Version number assigned? N/A
- BUILD increments on every change? N/A
- Breaking changes handled? N/A

## Project Structure

### Documentation (this feature)
```
specs/002-saleorder/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: Option 2: Web application

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context**: None.
2. **Generate and dispatch research agents**: None needed.
3. **Consolidate findings** in `research.md`: No research needed.

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - The `Order` entity in `SaleOrders.Domains` will be updated with a `Status` property and a `Cancel()` method.
2. **Generate API contracts** from functional requirements:
   - A `PATCH` endpoint will be added to `SaleOrders.WebApi`: `/api/orders/{orderId}/cancel`.
3. **Generate contract tests** from contracts:
   - A new test class `CancelOrderTests` will be added to `SaleProducts.Tests`.
4. **Extract test scenarios** from user stories:
   - A new integration test `CancelOrder_Should_Publish_OrderCancelled_Event` will be added.
5. **Update agent file incrementally**: N/A

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Create a new command `CancelOrder` and its handler in `SaleOrders.Applications`.
- Add a `CancelOrder` endpoint to `OrdersController` in `SaleOrders.WebApi`.
- Define the `OrderCancelled` integration event in `Lab.MessageSchemas.Orders`.
- Implement the `CancelOrder` command handler to:
  - Load the order.
  - Call the `Order.Cancel()` method.
  - Save the updated order.
  - Publish the `OrderCancelled` event.
- Add a `Status` property to the `Order` entity.
- Add integration tests to verify the cancellation logic and event publication.

**Ordering Strategy**:
- TDD order: Tests before implementation
- Dependency order: Domain, Application, Infrastructure, Presentation

**Estimated Output**: 5-7 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
|           |            |                                     |

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [X] Phase 0: Research complete (/plan command)
- [X] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [X] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*