# Design observable Given-When-Then scenarios

## Establish the behavior source

Bind bounded behavior, requirement/specification/acceptance IDs and source
revision/status, or exact conversational source when no document exists.
Separate approved behavior from observed code, assumptions and proposed rules.
Contradictions require an owner decision; do not silently turn current behavior
into approved requirements. For ambiguity, give one or two interpretations and
label affected scenarios provisional.

Use target-selected test conventions, permissible evidence and requested
format. This package has no language, runner, mocking library or DI extension;
do not infer one from a file suffix. Report unavailable selected guidance and
leave the affected required specialist judgment unresolved.

Default to scenario notes. If the user supplies/requests `.feature`, or an
explicit target decision selects that artifact, render the same scenarios as
Gherkin Feature/Scenario or Scenario Outline/Examples. Preserve tags, row
identity and relevant supplied structure. Designing the file does not select a
runner or authorize code, package installation or execution. A formal test
specification remains a separately selected authoring artifact; GWT wording
alone does not switch this operation into that responsibility.

## Build the scenarios

1. Extract behaviors and ACs. Map every in-scope AC to scenarios or an explicit
   gap. Give each scenario a stable ID and behavior-oriented name; use a clearly
   local ID when no source ID exists.
2. State the real subject and justified test level. Identify controlled
   dependency boundaries and those needing real infrastructure.
3. Write concrete Given data/state, permissions, time and dependency responses.
   Put setup facts here. Identify isolation, nondeterminism and unknown values.
4. Write one primary When with its inputs. If behavior needs an action sequence,
   make it intentional and explicit; do not combine unrelated triggers to reduce
   scenario count.
5. Write each important Then/And as an observable value, relation, state, event,
   error or exception contract, with the source of its expected value. Replace
   vague "works correctly" with what an observer can assert. Do not learn an
   expected value from the algorithm under test.
6. Add relevant positive, boundary, invalid-input and specified failure/recovery
   variants. Include duplicates, ordering, timeout or cancellation only where
   meaningful. Preserve Given -> When -> Then rather than replacing scenario
   output with Arrange-Act-Assert.
7. Self-check coverage, assertions and feasibility. Mark deferred cases and
   missing rules explicitly. Scenario text is not execution evidence.

Examples tables may share a scenario when each row has a stable identity and
consistent precondition/action/assertion responsibilities. Split rows when
these differ materially. Preserve each row's source and expected result. Use
And for clarity, not to conceal unrelated outcomes.

## Select a test level that can prove the outcome

| Boundary | Typical evidence need |
| --- | --- |
| Domain object/aggregate | Invariants, state transitions and domain events. |
| Application use case | Input/result, orchestration and application-owned effects. |
| Reaction | Event handling, projection/update and specified duplicate/failure behavior. |
| API/controller | Request/response, validation and status/error mapping. |
| Integration | Actual database, messaging, gateway, environment/configuration interaction. |
| Journey/cross-context | Coupled behavior across the necessary real boundaries. |

These are method choices, not mandatory folders or framework classes. A mock
can isolate orchestration but cannot establish the real dependency's behavior.
Prefer the smallest credible fixture; explain why it suffices and expose any
required integration evidence that a cheap substitute cannot supply.

## Output and handoff

Return inputs/assumptions, scenario set, assertion/setup notes, AC-to-scenario
coverage and unresolved/deferred cases. For each scenario preserve:

- Scenario/data-row ID, name, source path or inline reference, revision/status
  and existing requirement/AC IDs.
- Test level, real subject and controlled boundaries.
- Concrete Given, primary When and every observable Then/And.
- Expected-value sources, uncertainty and fixture/evidence limits.

Persist only to a caller-selected authorized destination with an available
editor. There is no required spec directory or store. If placement is undecided,
return prose and an optional suggestion suited to the target.

For separately authorized implementation, carry the design and existing
permission to the bounded implementation owner. Do not invent future test
paths, review results or passing outcomes. The receiver returns a compact
mapping: scenario/data row -> source/AC -> actual test file/identifier ->
Given/When/Then steps and outcome assertions -> actual execution status/evidence.
One assertion may cover equivalent outcomes with explanation; distinct outcomes
need appropriate assertions. Helper names or assertion counts do not prove
coverage. The receiver must not drop a Then, weaken expected behavior, narrow
data silently or mock the subject itself.

Optional specialist/implementation collaboration is not an installation
prerequisite; return the semantic handoff when absent. Design, implementation,
review and execution remain separate states. An author applying
[review criteria](review.md) records self-check, not independent acceptance or
specification compliance.
