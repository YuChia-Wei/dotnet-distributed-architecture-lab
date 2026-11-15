# Gherkin files in a .NET target

Create or maintain `.feature` files when supplied by requirements, explicitly
requested, or selected by the target's Gherkin runner profile. Their presence in
installed knowledge does not enable a runner or create target tests. C# tests
retain GWT under the [test standard](test-standards.md),
including an explicitly selected BDDfy opt-out.

## Knowledge and target artifacts

| Artifact | Location and responsibility |
| --- | --- |
| Shared expression and design examples | [Common BDD knowledge](../../engineering-common/bdd/README.md); instructional resources, without executable bindings. |
| Target scenario design | `.dev/specs/tests/`; source/AC IDs, assertion mapping, boundary, fixture needs and unresolved outcomes. |
| Official target Gherkin | `tests/Features/`; maintained scenarios linked from the test design. |
| Step bindings and fixtures | The selected test project; connect steps to the real subject and meaningful assertions. |

Use `test-designer` when available for scenario design. Preserve supplied source
and scenario IDs. Copy an example only after adapting its behavior to accepted
target requirements; knowledge examples are not target specifications or tests.

## Target file layout

Use kebab-case names and the smallest meaningful behavior scope:

- `tests/Features/<domain>/<use-case>.feature`
- `tests/Features/cross-domain/<flow>.feature`
- `tests/Features/e2e/<journey>.feature`

Keep official features outside domain source code and `.dev/specs/tests/`.
Place bindings and support under the owning test project's `Steps/`, `Fixtures/`
and `Support/` directories. Select Reqnroll or another runner only through the
actual target profile; writing scenarios does not install one.

## Scenario and verification guidance

Use the [Gherkin expression guide](../../engineering-common/bdd/gherkin.md) and
[example feature](../../engineering-common/bdd/examples/library-renewal.feature).
For DDD, CA or selected Inbox/Outbox behavior, read the
[boundary guide](../../engineering-common/bdd/architecture-boundaries.md) and
[.NET messaging contract](../integration/messaging/transactional-messaging-standards.md).
Parsing, binding, executing and proving the specified outcomes are separate checks.
