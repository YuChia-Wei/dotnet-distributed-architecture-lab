# Target-Selected On-Demand Mechanical Validation

This directory is recipe-only reference material. It is not an executable
validation provider, package, project, or activation record. The framework
ships no compilable analyzer or runtime-validation project and selects no .NET
SDK on behalf of a target repository.

## Default State

- Delivery: `reference-only`
- Selection: `not-selected`
- Compilable payload: `none`
- Framework SDK requirement: `none`
- Activation inference: `forbidden`

Presence of these files does not mean that an analyzer, configuration test, or
CI gate exists in the target. A target owner must make and evidence a separate
selection before creating any project or wiring.

## Retained Reference Material

| Material | Evidence tier | Bounded claim |
| --- | --- | --- |
| [`diagnostic-mapping.yaml`](diagnostic-mapping.yaml) | `reference-only` | Preserves DBA1001-DBA1017 enforcement labels and semantic-source pointers; it does not prove an implementation. |
| [`recipes/analyzer-project.md`](recipes/analyzer-project.md) | `reference-only` | Describes target-owned analyzer project creation and wiring without choosing an SDK or Roslyn version. |
| [`recipes/analyzer-severity.editorconfig.snippet`](recipes/analyzer-severity.editorconfig.snippet) | `reference-only` | Preserves the former severity baseline as an editable target decision. |
| [`recipes/projection-registration-test.md`](recipes/projection-registration-test.md) | `reference-only` | Preserves the marker-based EF model-registration test pattern without a framework runtime library. |

Canonical standards and the engineering-rule catalog remain the semantic
owners. Diagnostic IDs, snippets, project paths, packages, and CI commands are
bindings only.

## Target-Owned Selection Flow

1. Record the target capability and rule subset that needs mechanical
   enforcement. Do not select every mapping by default.
2. Create the analyzer or configuration-test project in a target-owned path.
3. Select the target framework, .NET SDK, Roslyn or test package versions, and
   compatibility range from target evidence.
4. Implement and test the selected rules against the target's actual type
   system, architecture profile, and exceptions.
5. Apply target-owned project wiring, severity, warnings-as-errors, and CI
   commands.
6. Record exact build/test results and the target commit before claiming that
   the capability is active.

The framework does not copy source into the target, edit `.slnx`,
`Directory.Build.props`, `.editorconfig`, or project files, or evaluate an
activation state. Missing target evidence remains `not-selected` or
`unresolved`; reference presence is never executable proof.

## Compatibility Responsibility

The target owner must verify the selected SDK, target framework, Roslyn API,
compiler, build host, package versions, analyzer severity, and test framework.
These recipes have no independent binary-compatibility claim. A future
framework-owned package, `dotnet tool`, contract assembly, or compiled CLI
requires a separate owner-approved lifecycle.
