# GWT Test Implementation Review

Use with the test route, its fresh effective `TEST-GWT-001` / `TEST-BDDFY-001`
rules, the canonical [test standard](../standards/coding-standards/test-standards.md)
and the [handoff contract](../../../shared/GWT-TEST-HANDOFF-CONTRACT.md).

Follow the selected scenario/data row through the test entry point and actual
step bodies. Check that material Given values remain visible, When invokes the
real subject with the designed inputs, asynchronous work completes, and every
Then maps to an assertion of that operation's observable outcome. Check the
selected BDDfy/default or explicit opt-out evidence without guessing from syntax.

Use these defect probes only when their conditions apply:

| Suspicious implementation | Evidence needed before a finding |
| --- | --- |
| `Given...` contains the expected-result assertion | The assertion is scenario verification rather than a fixture validity guard, and the designed When/Then responsibility is lost. |
| Empty/fabricated `When...` and a default result | The real subject never executes; a zero/false/null assertion can pass on initialization alone. |
| `Then...` calls the command/query again | The assertion observes another invocation rather than the captured When result; distinguish permitted read-only observation from repeating the trigger. |
| Assertions only check non-null/success | A required amount, state, exception detail or interaction outcome is missing. |
| Expected value is recalculated with the subject algorithm | The expected outcome lacks an independent source and can repeat the same defect. |
| Async step is unawaited or blocks | The selected runner does not await completion, or `.Wait()` / `.Result` creates blocking behavior. Do not infer runner behavior from a Task-returning name. |
| Several theory rows share one identifier | Results cannot be mapped to the selected source cases; shared parameterization itself is valid. |
| A report says all scenarios passed | Actual results are absent, filtered, skipped, zero-discovery or belong to other code/profile inputs. |

Report actionable source-backed findings with the affected test/step and missing
outcome. Do not demand a specific helper spelling, one assertion per English
sentence, or separate test methods for equivalent parameterized rows. The
permitted compact exception-contract form remains valid. Runtime passes and
structural checks support review; they do not replace this semantic inspection.
