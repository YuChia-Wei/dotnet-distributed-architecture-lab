# Target-Selected On-Demand Mechanical Validation

This directory is reference-only material. It is not an executable validation
provider, package, project, or activation record. The framework ships no
compilable analyzer or runtime-validation project and selects no .NET SDK on
behalf of a target repository.

## Default State

- Delivery: `reference-only`
- Selection: `not-selected`
- Compilable payload: `none`
- Framework SDK requirement: `none`
- Activation inference: `forbidden`

Presence of these files does not mean that an analyzer, configuration test, or
CI gate exists in the target. A target owner must make and evidence a separate
selection before creating any project or wiring.

## Provider Contract

[`provider-contract.yaml`](provider-contract.yaml) keeps the optional
Engineering Guardrails recommendation separate from target selection. Its stable
capability ID is `dotnet.mechanical-validation`, not a package identity. The
canonical package ID, version, feed, and identity evidence remain unknown or
`null`; this framework therefore has no real-provider readiness, compatibility,
or execution claim.

| State | Bounded meaning |
| --- | --- |
| `declined` | A target has explicitly declined adoption. The official recommendation and fallback templates remain available; no readiness or execution claim exists. |
| `not-selected` | The default state. The target has an exact mechanical-validation capability gap, fallback templates are available, and automatic installation or selection is forbidden. |
| `selected-unavailable` | A target selected the capability but lacks exact package identity, version, feed, fresh readiness, or compatibility proof. Execution is prohibited. |
| `synthetic-readiness-proven` | A synthetic record proves the schema transition only. It cannot prove real-provider execution; that claim remains rejected without an exact real execution receipt. |

Readiness, compatibility, and execution receipts have separate types and
SHA-256 digest requirements. They must be supplied by the target after its own
selection; none is shipped here.

## Retained Reference Material

| Material | Evidence tier | Bounded claim |
| --- | --- | --- |
| [`provider-contract.yaml`](provider-contract.yaml) and [`provider-contract.schema.yaml`](provider-contract.schema.yaml) | `reference-only` | Define recommendation, selection, unavailable-provider, receipt, and fail-closed state semantics without identifying a package. |
| [`templates/provider-selection.template.yaml`](templates/provider-selection.template.yaml) | `reference-only` | A copy becomes a target-owned selection/evidence record; it starts `not-selected`. |
| [`templates/minimal-diagnostic-analyzer.cs.template`](templates/minimal-diagnostic-analyzer.cs.template) | `reference-only` | A bounded target-owned analyzer starting point; it contains no selected diagnostic behavior. |
| [`templates/minimal-diagnostic-analyzer-test.cs.template`](templates/minimal-diagnostic-analyzer-test.cs.template) | `reference-only` | A target-owned GWT test starting point with unresolved target test/harness choices. |
| [`templates/code-fix-decision.md`](templates/code-fix-decision.md) | `reference-only` | Records a target decision to decline, defer, or implement any code fix; no fix is supplied here. |
| [`diagnostic-mapping.yaml`](diagnostic-mapping.yaml) | `reference-only` | Preserves DBA1001-DBA1017 enforcement labels and semantic-source pointers; it does not prove an implementation. |
| [`recipes/analyzer-project.md`](recipes/analyzer-project.md) | `reference-only` | Describes target-owned adoption from the templates without choosing provider delivery, SDK, Roslyn, or test versions. |
| [`recipes/analyzer-severity.editorconfig.snippet`](recipes/analyzer-severity.editorconfig.snippet) | `reference-only` | Preserves the former severity baseline as an editable target decision. |
| [`recipes/projection-registration-test.md`](recipes/projection-registration-test.md) | `reference-only` | Preserves the marker-based EF model-registration test pattern without a framework runtime library. |

Canonical standards and the engineering-rule catalog remain the semantic
owners. Diagnostic IDs, snippets, project paths, packages, and CI commands are
bindings only.

## Target-Owned Selection Flow

1. Copy the selection template into a target-owned location and record the
   bounded capability and diagnostic subset. Do not select every mapping by
   default.
2. Keep `not-selected`, `declined`, and `selected-unavailable` distinct. A
   recommendation never selects or installs a provider.
3. If a provider is selected, record exact provider identity, delivery, fresh
   readiness, and compatibility evidence separately before allowing execution.
4. Copy the analyzer and test starting templates into target-owned source, then
   implement and test only the selected rules against the target's actual type
   system, architecture profile, and exceptions.
5. Apply target-owned project wiring, severity, warnings-as-errors, and CI
   commands.
6. Retain an exact real execution receipt bound to the target commit before
   claiming that the capability is active. A synthetic readiness record does
   not satisfy this step.

The framework does not create target source, edit `Directory.Build.props`,
`.editorconfig`, or project files, or evaluate an activation state. Copied
templates become target-owned rather than framework-owned implementation.
Missing target evidence remains `not-selected`, `selected-unavailable`, or
`unresolved`; reference presence is never executable proof.

## Compatibility Responsibility

The target owner must verify the selected SDK, target framework, Roslyn API,
compiler, build host, provider identity, package versions, analyzer severity,
and test framework. These recipes have no independent binary-compatibility
claim. A future framework-owned package, tool, contract assembly, or compiled
CLI requires a separate owner-approved lifecycle.
