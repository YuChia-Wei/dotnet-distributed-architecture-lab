# Diagnostic Contract

Use this skill for an observed failure or performance symptom. Select a bounded
subject and an expected-versus-actual observation before choosing a cause.
Record the environment, exact command, allowed output roots, experiment cost,
stop conditions, and existing authorization. A read-only investigation may run
tests only within those permissions; diagnostic intent is not permission to
change production data, deploy a patch, or weaken a guard.

## Falsification First

For each hypothesis, write the observation that would disprove it before running
the experiment. Name the observation scope and what the instrument could miss.

| Strength | Required observation | Permitted inference |
| --- | --- | --- |
| `deterministic-complete` | Instrument every relevant event in the declared finite scope; expected and observed opportunities agree. | Support or falsify within that scope. |
| `deterministic-bounded` | Intercept or enumerate every opportunity in a declared reproduction; explicitly bound wider applicability. | Support or falsify only for that reproduction. |
| `sampling-limited` | Sample a subset of opportunities or times. | Discovery or provisional support; absence remains inconclusive. |
| `not-executed` | No execution evidence. | Untested hypothesis only. |

Count *observation opportunities*, not just matching events: a complete scan may
observe zero matching events but must show that all relevant opportunities were
examined. Missing instrumentation, unknown coverage, or a stopped experiment is
inconclusive. Do not promote sampling to deterministic evidence by renaming its
strength. An independent reviewer checks the method and retained bytes.

Prefer a subprocess interceptor with exact argv counts to occasional process
snapshots; prefer executing the archive's embedded validator to inferring
package validity from an outer route check. Use static evidence to design an
experiment, not to fabricate an executed observation.

## Root-Cause Admission

`confirmed` requires a minimal reproduction with the same observed symptom,
at least one deterministically supported hypothesis, and a controlled
intervention that changes the predicted outcome while holding the relevant
conditions fixed. Record baseline, intervention, actual result, evidence, and
remaining limits. Explain how plausible alternatives were distinguished; an
unresolved competing explanation keeps the conclusion `unconfirmed`.

Do not require a repair to reproduce an incident. An isolated fixture,
intercepted call, or bounded configuration perturbation can isolate a cause
within existing experiment authority. If that authority or environment is
missing, report `blocked`, identify the missing evidence, and stop that action.

## Ownership And Handoff

| Owner | Responsibility |
| --- | --- |
| `diagnostic-analyst` | Symptom, falsification, reproduction, causal conclusion, repair proposal and regression binding. |
| `code-reviewer` | Review a selected code change against applicable standards; a finding alone does not prove an incident's root cause. |
| `local-change-implementer` | An authorized single local technical repair within its existing dependency radius. |
| `slice-implementer` | An authorized bounded implementation slice. |
| `ai-context-governance` | Framework context, routing, and source-release contract remediation. |

The repair handoff states the causal evidence, affected scope, suggested owner,
existing authorization reference if any, and a regression command or scenario.
It never grants permission. A proposed regression is not an executed passing
regression. Keep before/after evidence separate and return to diagnosis when a
repair fails to change the predicted symptom.
