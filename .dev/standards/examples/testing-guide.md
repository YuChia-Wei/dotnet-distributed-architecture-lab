# Testing Guide Overview (.NET)

## Document Layers

### 1) Use Case Tests (Production-Ready)
**File**: `examples/use-case-test-example.md`
- Profile-based testing (InMemory / Outbox)
- BDDfy + xUnit (Gherkin-style naming)
- Real DI wiring

### 2) Contract Tests (DbC Preconditions)
**Reference**: `examples/contract/`
- Pure xUnit (no host/DI unless required)
- Validate preconditions
- One command method per test group

### 3) Conceptual Examples
**File**: `examples/test-example.md`
- Learning material
- Manual setups and patterns

## Keep Both Guides?

Yes:
- `use-case-test-example.md` = production patterns
- `test-example.md` = learning/reference

## Recommended Structure

```
examples/
├── use-case-test-example.md    # primary reference
├── test-example.md             # concepts
├── outbox/                      # outbox tests
└── inquiry-archive/             # query patterns
```

## Key Rules

- No base test classes
- Rule-prefixed test names for scenario grouping
- Event verification is mandatory for command use cases
