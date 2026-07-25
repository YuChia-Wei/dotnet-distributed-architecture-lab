# Reference Documents (.NET)

These documents are technical references, not code examples or generation templates.
Use them as lookup material while migrating or generating code.

## Contents

### ezddd-import-mapping.md
Historical source terminology mapped to current repository contracts.
Do not copy its placeholder namespaces into target code.

### reactor-pattern-guide.md
Reactor/handler patterns for Wolverine + ezDDD, including naming, structure,
and testing guidance.

### ezspec-test-template.md
BDD testing template using BDDfy + xUnit (Gherkin-style naming), including
Rule grouping and fixture-based DI.

### nuget-dependencies.md
Recommended NuGet package groups for the stack (Wolverine, EF Core, testing).

## How This Differs from Other Folders

- `examples/[pattern]/` = concrete pattern examples
- `generation-templates/` = full module templates
- `reference/` = pure technical reference

## Usage Tips

1. Treat these docs as a dictionary, not a tutorial.
2. If a reference conflicts with actual library APIs, update it.
3. Treat historical package names as provenance, not future package commitments.
