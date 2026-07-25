# Dependency Version Consistency Policy

## Purpose

This policy defines the deterministic offline dependency and runtime-version
gate for this AI context framework. The gate proves that repository-owned
declarations agree with each other. It does not claim that a selected version
is current, vulnerability-free, or suitable for a target product.

## Required Offline Contract

`python .ai/scripts/validate-dependency-versions.py` is a required repository
gate and must run without network access.

In the source framework repository it enforces:

- every direct Python requirement uses one exact `name==version` pin;
- root `requirements.txt` and
  `.ai/distribution/templates/requirements.txt` are byte-identical mirrors;
- GitHub workflows install Python dependencies through the root
  `requirements.txt`, rather than repeating package versions inline;
- all `actions/setup-python` steps declare the same exact Python version and
  satisfy the repository minimum of Python 3.11;
- direct `PackageReference` declarations in framework-managed
  `tools/**/*.csproj` use exact versions, and a repeated package ID resolves to
  one version across those projects;
- `global.json` declares an exact SDK version whose major version can build the
  highest concrete `netN.0` target used by the managed tools.

`netstandard` targets do not require SDK-major equality. A newer SDK may build a
lower `netN.0` target; the gate fails only when the selected SDK is too old for
a managed tool.

## Installed-Repository Applicability

Source distribution controls and release workflows are not installed target
truth. Their checks apply only when the source requirements template is
present. An initialized target still executes the validator and checks any
framework-managed `tools/**/*.csproj` plus its selected `global.json`, without
requiring source-only workflows or distribution templates.

The validator deliberately does not inspect target product package selections
outside `tools/`. Product dependency policy, central package management, and
technology selection remain target-owned.

## Online Advisory Boundary

Package currency and vulnerability information depends on mutable registries
and advisory databases. Such checks may run separately as visible advisory
evidence, but their absence or network failure must not be represented as an
offline consistency failure or success. A release claim must name any online
tool, database, timestamp, and executed environment explicitly.

## Runner And Portability Contract

`.ai/scripts/check-all.sh` retains its existing literal multiline declaration
format. `shell-assets.yaml` owns the set of required child scripts and commands,
and `validate-shell-assets.py` fails closed when the runner and manifest differ.
Formatting-contract fixtures must change with any future runner syntax change.

The v0.5.0 portability claim requires the same `--quick` gate set to pass on
Windows Git Bash and hosted Ubuntu. macOS remains unverified until separately
executed; passing Unix-like hosts must not be generalized into a macOS claim.

## Change Procedure

A dependency or runtime-version update must change every governed mirror,
workflow route, or managed project declaration in one coherent change and pass:

```text
python .ai/scripts/tests/test_dependency_version_consistency.py -v
python .ai/scripts/validate-dependency-versions.py
python .ai/scripts/tests/test_fail_closed_validation.py -v
python .ai/scripts/validate-shell-assets.py
bash .ai/scripts/check-all.sh --quick
```

Online freshness or vulnerability results may inform the selected versions, but
they do not replace these deterministic checks.
