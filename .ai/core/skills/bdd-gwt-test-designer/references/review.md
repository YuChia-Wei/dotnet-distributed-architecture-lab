# Review a fixed scenario artifact

Bind the artifact path/version and digest, or quote bounded inline scenarios.
Record requirements/ACs, source revision/status, coverage and target conventions
separately. Leave the artifact unchanged. For authorized revision, finish this
review before [designing the revision](design.md); later review binds that new
subject.

| Criterion | Inspect for |
| --- | --- |
| Traceability | Each scenario has a source requirement or labeled assumption; each in-scope AC has coverage or a gap. Preserve scenario/data-row IDs and source status. |
| Observable assertions | Every important Then names an assertable value, relation, state, event or error with an independent expected-value source. |
| Controlled setup | Given supplies data, permissions, time, state, dependency outcomes and isolation; nondeterminism/unknowns are visible. |
| Behavior focus | One main When, or a justified sequence, tests a contract rather than copying private algorithm steps. |
| Boundaries/failures | Meaningful edge values and specified failure/recovery are covered; speculative cases are not invented requirements. |
| Evidence level | The selected boundary can prove the behavior; a mock is not real integration evidence. |
| Handoff | Stable IDs, concrete data, expected outcomes and unresolved inputs survive into implementation; future locations/results are not invented. |
| Cost/conventions | Fixtures are proportionate; conventions are explicitly target-selected without imposing a runner/package. |

Missing requirement authority or selected specialist guidance limits the affected
judgment. This package has no technology extension. Keep required specialist
acceptance unresolved instead of presenting common-method coverage as a pass.
Valid alternative wording or test levels may prove the same acceptance.

For each finding give artifact location, criterion/source, evidence, triggering
condition, impact, severity rationale, uncertainty and a bounded correction.
Distinguish defects, questions and optional improvements. Suggested scenarios
cite their source or remain provisional. Return subject, sources, findings,
criterion/AC coverage, exclusions and missing inputs. No findings means none
supported within inspected coverage, not compliance.

Choose and justify the classification:

- `self-check` when the reviewer authored or repaired the artifact.
- `review; independence not established` when authorship or required evidence
  is unknown.
- `independent-review` only with evidenced distinct author, fixed subject,
  read-only reviewer and applicable target independence requirements.

Different prompts/models and a hash alone do not prove independence. This
package mandates no review packet. Preserve separate target acceptance and
state actual inspections and limits.

This operation reviews scenario artifacts. Executable-test review must follow
actual step/helper calls, check that the real action runs and assertions inspect
every designed outcome. GWT comments, names, compilation and a green run alone
cannot establish fidelity. Do not claim such code review or execution from
scenario text.

Return optional handoffs for requirement decisions, architecture, formal-spec
authoring or bounded test implementation with source, exact question/correction
and existing permission. Other skills are not required to finish this review.
A handoff grants no new authority, creates no test results and rewrites no
source requirement.
