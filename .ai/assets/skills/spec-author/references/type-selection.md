# Type Selection

Use:

- `use case spec JSON` when describing production behavior, input, aggregate, repository, output
- `entity spec markdown/json` when describing aggregate or value-object structure
- `adapter spec JSON` when describing controller/API behavior
- `test spec markdown` when describing validation scenarios

A formal test-spec request remains with `spec-author`, including when its
selected document contains Given-When-Then scenarios. Use the target test-spec
contract and retain supplied scenario IDs and source links.

If the requested output is only scenario notes, a GWT matrix or assertion design,
use `bdd-gwt-test-designer`. Missing scenario design may be a bounded input
handoff; do not redesign complete accepted scenarios or replace the formal
spec artifact solely because GWT words occur in it.
