# Spec Compliance Rules (Dotnet)

## Purpose (100% Gate)
- Spec compliance is mandatory after problem-frame execution and before completion.
- Overall compliance **must be 100%**. If any category < 100%, the task is NOT complete.

## Scope & Inputs
- Problem frame path: `.dev/problem-frames/{domain}/{frame-type}/{use-case}/`
- Supported frame types:
  - **CBF** (CommandedBehaviorFrame)
  - **SWF** (SimpleWorkpieceFrame)
- Always read `frame.yaml` to detect frame type and resolve spec file locations.

## Required Spec Files
- `frame.yaml`
- `machine/machine.yaml`
- `machine/use-case.yaml`
- Aggregate spec:
  - CBF: `controlled-domain/aggregate.yaml`
  - SWF: `workpiece/aggregate.yaml`
- Scenarios:
  - CBF: `acceptance.yaml`
  - SWF: `requirements/*.yaml`

## Compliance Matrix (What Must Reach 100%)
### Common (CBF + SWF)
- Use Case input fields
- Service preconditions
- Aggregate behavior signature
- Domain event attributes
- Error handling policies
- Constraints (C1–Cn)
- Then-condition assertions (every `then` is asserted)

### CBF-Only
- Frame concerns coverage (FC1–FC6)
- Scenario coverage (all scenarios mapped to tests)
- Contract checks (PRE/POST/INV)
- ezSpec GWT semantic alignment (Given/When/Then/And)

### SWF-Only
- Acceptance criteria (AC1–ACn) coverage
- Entity method contracts (if defined in aggregate spec)

## Validation Levels
- **L1 Existence**: required items are implemented and test-covered.
- **L3 Contract Semantics**: `require/ensure/invariant` semantics match spec.
- **L4 GWT Semantics**: Gherkin-style steps (BDDfy) match scenario intent and order.

## Production Code Mapping (.NET)
- Use case input and handlers: `src/Application/<Aggregate>/UseCases/{Commands|Queries}/`
- Domain aggregate: `src/Domain/<Aggregate>/Aggregates/<Aggregate>.cs`
- Domain events: `src/Domain/<Aggregate>/Events/`
- Entities/ValueObjects: `src/Domain/<Aggregate>/{Entities|ValueObjects}/`
- Outbox/EF Core integration (if required): `src/Infrastructure/` (exact location per project config)

## Test Code Mapping (.NET)
- Use case tests: `src/tests/Application/<Aggregate>/UseCases/`
- Contract tests: `src/tests/Domain/<Aggregate>/Contracts/<Aggregate>ContractTests.cs`
- Controller tests: `src/tests/Api/Controllers/<Aggregate>/`

## Testing Style Requirements
- **xUnit + BDDfy with Gherkin-style naming (no `.feature` files)**
- **No BaseTestClass**
- **NSubstitute** for mocks
- Each scenario has a corresponding test method
- Each `then` condition has a dedicated assertion
- Event publication checks must be async-safe (awaitable, no sleep)

## Failure Conditions (Any One Fails the Gate)
- Any category coverage < 100%
- Any scenario/AC missing a test
- Any `then` missing an assertion
- Any constraint/concern missing verification
- Any contract PRE/POST/INV missing or semantically mismatched
- GWT order mismatch (Given → When → Then → And)
- Tests depend on forbidden patterns (BaseTestClass, inline debug logging)

## Output Expectations
- Report must list missing items with spec references and target code paths.
- Remediation actions must be specific (file, method, assertion needed).

## Notes
- Spec compliance is enforced regardless of architecture mode (inmemory/outbox/eventsourcing).
- Preserve DDD/CA/CQRS/ES/Outbox concepts as defined in shared rules.
