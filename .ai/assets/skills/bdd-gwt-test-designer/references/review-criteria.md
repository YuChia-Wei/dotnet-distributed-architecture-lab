# Scenario Review Criteria

Use with the shared artifact design/review contract. Review scenario artifacts;
route defects in executable test or production code to `code-reviewer`.

| Criterion | Evidence to inspect |
| --- | --- |
| Acceptance traceability | Map every AC to scenarios and every claimed scenario to a requirement or explicitly labeled assumption. Report missing/contradictory coverage. |
| Implementation handoff | Preserve scenario/data-row IDs, source revision/status, concrete inputs and expected-value sources under the shared GWT handoff contract. Future code or execution locations remain unknown until the receiving owner supplies them. |
| Observable outcomes | Each important Then names an observable result and an assertable value, relation or state. "Works correctly" is insufficient. |
| Controlled preconditions | Given supplies data, state, permissions, time and dependency outcomes required for reproducibility. Identify nondeterminism and unknown setup. |
| Behavior isolation | One primary When and behavior; split unrelated outcomes when their triggers differ. Assertions test contracts rather than copying private algorithm steps. |
| Boundaries and failure | Cover meaningful limits, invalid inputs and specified failure/recovery behavior. Add duplicate, ordering, timeout or cancellation cases only when relevant. |
| Test level | Justify which boundary needs a unit, use-case, integration or journey test. A mocked dependency cannot establish a real integration claim. |
| Cost and tooling | Prefer the smallest credible fixture. Select concrete conventions from target evidence; GWT design does not require a particular package. |

Retain valid alternative scenario wording and test layers when they prove the
same acceptance. Flag a missing requirement as a question, not an invented
expected result. Suggested new scenarios must cite their requirement or carry
an explicit provisional label. Hand requirement changes to `requirement-author`,
production/test-spec changes to `spec-author`, architecture ambiguity to
`ddd-ca-hex-architect`, and authorized concrete test work to `slice-implementer`.
