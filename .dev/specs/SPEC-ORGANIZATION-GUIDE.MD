# Spec File Organization Guide

This document explains how to organize specs by bounded context, aggregate, and test target. This framework repository does not retain an active production/domain spec subtree; production specs are target-repository outputs, usually created by `repo-structure-sync` or a later workflow when source requirements exist. This repository retains rules, templates, and `.dev/specs/tests/`.

## Directory Structure

```text
Framework repo (.dev/specs/):
  README.MD
  SPEC-GUIDE.MD
  SPEC-ORGANIZATION-GUIDE.MD
  tests/
    <bounded-context>/
      aggregate/
      use-cases/
      integration/
    cross-domain/
    e2e/

Target repo (.dev/specs/ when production specs exist):
  domains/
    <bounded-context>/
      <aggregate>/
        entity/
          <aggregate>-spec.md
        usecase/
          <action>-<aggregate>.json
```

## Placement Rules

1. Identify the aggregate primarily operated on by the use case.
2. Confirm the bounded context that owns the aggregate.
3. Use the same bounded-context/aggregate perspective for production and test specs.
4. A relationship does not imply ownership. Do not place B's spec in A's aggregate directory merely because A references B.
5. If bounded-context or aggregate ownership is unclear, use `ddd-ca-hex-architect` first; do not guess the path.
6. This framework repository retains only guides, templates, and test-spec materials; it does not host an active `domains/` subtree.

## Naming Rules

- Use case spec: `<action>-<aggregate>.json`
- Entity/aggregate spec: `<aggregate>-spec.md`
- Test spec: `<target>.test-spec.md`
- Use kebab-case for directories and filenames.

## Neutral Example

```text
Target repo:
.dev/specs/
  domains/
    <context-a>/
      <aggregate-a>/
        entity/
          <aggregate-a>-spec.md
        usecase/
          create-<aggregate-a>.json
          update-<aggregate-a>.json
    <context-b>/
      <aggregate-b>/
        usecase/
          process-<aggregate-b>.json
  tests/
    <context-a>/
      aggregate/
        <aggregate-a>.test-spec.md
      use-cases/
        create-<aggregate-a>.test-spec.md
      integration/
        <aggregate-a>-persistence.test-spec.md
```

## Common Mistakes

### Placing by Relationship Instead of Ownership

```text
Wrong:
domains/<context-a>/<aggregate-a>/usecase/create-<aggregate-b>.json

Correct:
domains/<context-b>/<aggregate-b>/usecase/create-<aggregate-b>.json
```

### Placing All Use Cases at One Level

```text
Wrong:
specs/usecases/<use-case>.json

Correct:
specs/domains/<bounded-context>/<aggregate>/usecase/<use-case>.json
```

## Migration Steps

1. Confirm bounded-context and aggregate ownership.
2. Create the correct directories.
3. Move the spec and corresponding test specs.
4. Update requirements, problem frames, workflow tasks, and code references.
5. Search for old paths and validate JSON/Markdown.

## Review Checklist

- [ ] Spec paths reflect bounded-context and aggregate ownership.
- [ ] Production and test specs use consistent naming.
- [ ] Cross-domain and E2E specs are not misplaced under a single aggregate.
- [ ] Documents use the target repository's ubiquitous language.
- [ ] Template placeholders are not mistaken for product truth.
