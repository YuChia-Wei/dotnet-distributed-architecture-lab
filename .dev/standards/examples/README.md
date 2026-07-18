# Examples (.NET)

This directory contains .NET examples and historical/reference material used by
the AI coding assistant for the Clean Architecture + DDD + CQRS stack.

## Evidence Contract

[`evidence-manifest.yaml`](evidence-manifest.yaml) is the machine-readable
classification source. Its allowed tiers and evidence requirements are defined
by [`evidence-schema.yaml`](evidence-schema.yaml).
Placeholder-family outcomes and canonical replacements are recorded in
[`placeholder-disposition.yaml`](placeholder-disposition.yaml).

The tiers are:

- `executable-tested`: implementation with declared build and test commands;
- `structure-validated`: structure/configuration with named validators;
- `illustrative`: explanatory snippets that are not copy-ready;
- `reference-only`: conceptual material selected on demand;
- `historical`: retained provenance and migration evidence.

Unclassified legacy material defaults to `historical`. Nothing is promoted to a
stronger tier by inference.

There is currently no directory-wide verified-template or single-source-of-truth
claim. Target package versions, technology selections, namespaces, and physical
layouts must come from target repository evidence.

Use [`INDEX.md`](INDEX.md) for the folder catalog. `README.md` owns purpose,
boundaries, and evidence interpretation; `INDEX.md` owns navigation.

Placeholder-heavy families are routed as `reference-only` or `historical` until
their APIs are rewritten against current canonical standards. Their presence is
not permission to copy unresolved EzDDD, uContract, persistence, or test-host
shapes into a target.
