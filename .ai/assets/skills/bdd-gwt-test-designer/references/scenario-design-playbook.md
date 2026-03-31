# Scenario Design Playbook

## Core Rules

- follow Given -> When -> Then order
- one scenario should test one main behavior
- each important Then should correspond to an explicit assertion
- use And only when it keeps the flow readable
- keep setup facts in Given, not in Then

## Repository Alignment

- testing stack is xUnit with BDDfy-style naming guidance
- no BaseTestClass
- BDD/Gherkin style here means scenario structure and naming, not mandatory `.feature` files
- when a requirement contains multiple acceptance criteria, map each AC to one or more scenarios

## Recommended Design Sequence

1. Name the scenario from business behavior
2. Define Given facts and required data
3. Define the single When trigger
4. Split expected results into explicit Then items
5. Add negative or boundary variants only when behavior changes

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
