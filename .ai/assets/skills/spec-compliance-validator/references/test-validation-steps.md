# Test Validation Steps (Dotnet)

Rule IDs: `TEST-GWT-001`, `TEST-BDDFY-001`, `TEST-MOCK-001`, `TECH-SELECT-001`.

## Purpose
Provide a repeatable checklist to verify tests comply with mandatory Given-When-Then rules, the default xUnit + BDDfy profile or an explicit project opt-out, spec-compliance requirements, and repository conventions.

## Scope
- Use case tests
- Contract tests
- Controller tests
- Reactor/Outbox tests (if applicable)

## Pre-Check (Mandatory)
- Tests use **Given-When-Then structure and naming**. BDDfy is the default profile, but an explicit project decision may opt out of the package.
- Unit, use-case, and integration tests do not substitute Arrange-Act-Assert (3A) for GWT.
- `.feature` assets are optional unless supplied/requested or required by an explicitly selected target feature-runner profile; never infer a runner/package.
- **No BaseTestClass** or shared test base types.
- Resolve the target `testing.mocking` selection; default to **NSubstitute**.
- No debug logging (Console.WriteLine / ad-hoc logs).

## Step 1: Locate Tests by Type
- Use case tests: `src/tests/Application/<Aggregate>/UseCases/`
- Contract tests: `src/tests/Domain/<Aggregate>/Contracts/`
- Controller tests: `src/tests/Api/Controllers/<Aggregate>/`

## Step 2: Scenario Coverage (CBF)
- Every `acceptance.yaml` scenario has a corresponding test method.
- Test name/DisplayName maps to `scenario.name` or `scenario.id`.
- `Given → When → Then → And` order is preserved.

## Step 3: Acceptance Criteria Coverage (SWF)
- Every AC in `requirements/*.yaml` has a test case.
- Each `then` condition has a dedicated assertion.

## Step 4: Gherkin-Style Step Semantics
For each scenario:
- **Given** steps map to explicit test setup state.
- **When** steps execute the use case/handler under test.
- **Then** steps assert outputs, state changes, and events.
- **And** steps add additional assertions (not just comments).

## Step 5: Domain Event Validation
- Event publication is verified with async-safe assertions.
- No `Thread.Sleep` / blocking waits for events.

## Step 6: Mocking Rules
- Mocks/stubs use the resolved target mocking selection.
- When no target selection exists, use NSubstitute.
- Do not mix mocking libraries without an explicit migration decision.
- Verify interactions for external boundaries (repositories, message bus, clocks, etc.).

## Step 7: Contract Test Rules
- Pure xUnit (no DI container / no test host).
- Each command method has a dedicated contract test class.
- Each precondition has a corresponding `Assert.Throws<PreconditionViolationException>`.

## Step 8: Controller Test Rules
- Use WebApplicationFactory or equivalent.
- Verify HTTP status codes and response DTO shape.
- DTOs are independent files (not inner classes).

## Step 9: Report Outcome
- If any rule fails, list:
  - Spec reference (scenario/AC/precondition)
  - Test file + method
  - Missing assertion or step
- Gate is **100%**; any missing item fails compliance.
