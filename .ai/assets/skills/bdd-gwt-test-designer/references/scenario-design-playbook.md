# Scenario Design Playbook

## Core Rules

- follow Given -> When -> Then order
- one scenario should test one main behavior
- each important Then should correspond to an explicit assertion
- use And only when it keeps the flow readable
- keep setup facts in Given, not in Then
- use the shared GWT handoff contract to preserve scenario/data-row identity,
  concrete inputs, expected-value sources and explicit unknowns for implementation

## Repository Alignment

- preserve Given-When-Then scenario structure; do not replace this skill's scenario output with Arrange-Act-Assert (3A)
- select testing conventions from explicit target decisions and applicable installed profile rules; the common skill does not select a runner, mocking library or DI API
- use `technology_selection` from the skill spec to load only the selected profile's test-design route after effective-rule preflight; the .NET route retains its xUnit/BDDfy defaults and explicit opt-out semantics
- distinguish confirmed requirement behavior from reverse-engineered current behavior; conflicts require a decision, not a silent requirement rewrite
- `.feature` files are planned/optional rather than mandatory. Default output remains scenario notes; design a `.feature` artifact when one is supplied or explicitly requested, or when the target profile selects a feature runner
- do not infer or select a feature runner/package
- when a requirement contains multiple acceptance criteria, map each AC to one or more scenarios

## Recommended Design Sequence

1. Name the scenario from business behavior
2. Define Given facts and required data
3. Define the single When trigger
4. Split expected results into explicit Then items
5. Add negative or boundary variants only when behavior changes
6. Map source AC IDs to scenarios and identify observable assertions and controllable preconditions
7. Explain why the selected test level supplies the required evidence; a mock cannot establish a real integration result

## Test Level Hints

- aggregate test:
  domain invariants, domain events, entity state changes
- use case test:
  command/query handling, repository interaction, orchestration
- reactor test:
  event reaction, integration event handling, projection updates
- controller test:
  request/response, validation, status code behavior
- integration test:
  environment/config/messaging/database interaction

## Recommended Output Placement

- aggregate-focused scenarios -> `.dev/specs/tests/<domain>/aggregate/`
- use case or handler scenarios -> `.dev/specs/tests/<domain>/use-cases/`
- repository, database, MQ, gateway scenarios -> `.dev/specs/tests/<domain>/integration/`
- cross bounded context scenarios -> `.dev/specs/tests/cross-domain/`
- end-to-end user journeys -> `.dev/specs/tests/e2e/`

`app-services/` and `domain-services/` are optional categories. Use them only when the test target is explicitly that service type.

## Ambiguity Handling

If a rule is ambiguous:

- state the ambiguity explicitly
- propose 1-2 interpretation options
- mark the scenario as provisional instead of pretending certainty
