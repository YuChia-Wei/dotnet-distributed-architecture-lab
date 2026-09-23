# Implement one local change

## Confirm the semantic radius

Identify one primary class/object/method/local symbol/query, one operation,
expected behavior and its source, permitted files/module, direct dependencies,
direct call sites and immediate tests. Authorization and target requirements
serve different purposes: permission to edit does not define correct behavior.
Preserve unrelated work and the target's accepted architecture.

Suitable operations include extracting a method, renaming a local symbol,
fixing bounded logic, simplifying an object interaction or adjusting a local
SQL/ORM implementation. A behavioral fix needs its intended behavior stated;
otherwise preserve behavior. Do not combine independent goals.

Several direct call-site files do not force a slice. A private implementation
helper type can remain local only if it preserves accepted target, radius,
behavior, responsibility, dependency direction, lifetime and transaction
boundary. A new type's existence or line count alone decides nothing.

A public/domain type, interface or responsibility/dependency/lifetime/transaction
change belongs to a bounded slice under an accepted design. Missing or changed
architecture, compatibility, module/aggregate or business-language decisions
need their owner's decision before dependent edits. Public DTO/API/event or
ubiquitous-language renames are not local symbol renames. Broad namespace
restructuring, cross-module behavior and multi-aggregate cleanup exceed this
local method. Return a concrete handoff rather than executing beyond scope.

When the target, operation or radius is unknown, resolve that bounded question
first. An unexplained runtime failure may need diagnosis before choosing a
repair; a diagnostic finding does not grant implementation authority.

## Execute the smallest coherent edit

1. Inspect the target, direct uses and relevant tests. Use applicable
   target-owned rules and only explicitly selected technology guidance. This
   package provides no ambient language, ORM, DI or test framework baseline.
2. State what changes and what behavior/contracts must remain stable. Identify
   hidden side effects, lifetime, transaction or data-semantics risks before
   treating a seemingly small edit as local.
3. Apply the single operation and required direct call-site changes. Prefer an
   applicable IDE refactoring if available and permitted; review its actual
   edits. Do not treat a tool's success as proof the radius stayed bounded.
4. Update immediate tests when needed to protect the changed contract and
   within authority. Avoid unrelated cleanup or implementation-mirroring tests.
5. Run the narrowest meaningful authorized target checks. Obtain the actual
   command, working directory, prerequisites and allowed output scope from
   target evidence. No default product command or package is supplied here.
6. Inspect the diff and actual touched radius. Stop dependent edits if an
   unaccepted semantic/architecture decision or wider operation emerges.

An unavailable editor blocks implementation. Missing selected specialist rules
block the corresponding decision. Missing test tools, environment or command
authority means those checks are blocked or not run; it is not permission to
invent a command, broaden credentials or call the implementation verified.
Continue other authorized work only if the missing item is not its prerequisite.
Existing permission remains valid; do not ask again just because an optional
handoff is used.

## Return the result

Report target/operation, expected behavior source, actual files/direct call
sites/tests touched and why they fit the radius. State compatibility and any
prevented expansion or unresolved decision. For each relevant check include
actual command/context and result, or precise not-run/blocked/deferred reason.
Preserve failures beside later results. A proposed regression, compilation or
zero discovered tests is not proof of changed-behavior coverage.

Keep output in the conversation or a caller-selected authorized destination.
No workflow, rule packet, record store or other installed skill is required
by this method. Optional review or slice/architecture collaboration receives
scope, sources, current evidence and existing permission. A local implementation
result is not independent review or specification compliance, and it grants no
push, PR, merge, publication or target decision authority.
