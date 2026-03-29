# DDD + CA + CQRS Learning Path (Dotnet)

## Core Concept Levels

### Level 1: Fundamentals
1. Clean Architecture principles
   - Dependencies point inward
   - Business logic independent of frameworks
   - Test-first mindset

2. DDD tactical patterns
   - Aggregate: transaction boundary
   - Value Object: immutable value
   - Domain Event: state change record

3. CQRS basics
   - Command: changes state
   - Query: reads state
   - Read/write separation

### Level 2: Implementation Patterns
1. Aggregate implementation
   - Pattern: event sourcing with Apply/When method
   - Rule: use C# pattern matching for event dispatch
   - Example layout:
     - `src/Domain/<Aggregate>/Aggregates/<Aggregate>.cs`
     - `src/Domain/<Aggregate>/Events/<Aggregate>Events.cs`

2. Use case pattern
   - Command use cases return `CqrsOutput`
   - Query use cases return custom Output DTOs
   - Handlers coordinate Domain and Infrastructure (WolverineFx)

3. Testing strategy
   - Use Case tests: must follow ezSpec intent using xUnit + BDDfy (Gherkin-style naming)
   - Domain tests: xUnit is allowed
   - Rule: do not directly call Aggregate methods in tests

### Level 3: Advanced Practices
1. Cross-aggregate collaboration
   - Reactor pattern: handle Domain Events with Wolverine handlers
   - Avoid direct references to other Aggregates

2. Query strategy
   - ID query: Repository
   - List query: Projection
   - Cross-aggregate query in reactors: Inquiry
   - Soft delete and history: Archive

## Required Reading Order

### Phase 1: Understand the architecture
1. `CLAUDE.md` - project memory (TODO: replace with .NET memory doc when available)
2. `.ai/assets/shared/architecture-config.md` - architecture rules
3. `.ai/assets/shared/common-rules.md` - non-negotiable rules
4. `.ai/assets/shared/testing-strategy.md` - test rules
5. `.ai/assets/skills/spec-compliance-validator/references/spec-compliance-rules.md` - spec compliance rules

### Phase 2: Learn by examples
1. `.dev/standards/examples/outbox/README.md` - outbox flow
2. `.dev/standards/examples/reference/ezspec-test-template.md` - BDD test style
3. `.dev/standards/coding-standards/test-standards.md` - mocking pattern
4. `.dev/standards/examples/dto/README.md` - DTO layout

### Phase 3: Avoid common mistakes
1. `.ai/COMMON-PITFALLS.md` - cross-cutting pitfalls
2. `.ai/FAILURE-CASES.md` - failure patterns

## Key Principles Quick Reference

### DDD
- Aggregate is the transaction boundary (one Aggregate per command)
- Value Objects are immutable
- Domain Events capture every change (event sourcing)

### Clean Architecture
- Depend on abstractions, not implementations
- Domain layer has no framework dependencies
- Tests lead implementation

### CQRS
- Commands change state and return `CqrsOutput`
- Queries return DTO-focused outputs
- Keep write and read models separate

## Coding Style Examples (C#)

### Pattern matching for events
```csharp
public void When(IDomainEvent @event)
{
    switch (@event)
    {
        case ProductCreated e:
            Id = e.ProductId;
            Name = e.Name;
            break;
        case ProductRenamed e:
            Name = e.NewName;
            break;
    }
}
```

### Value Object with record
```csharp
public readonly record struct ProductId(string Value);
```

### Use case handler shape (Wolverine)
```csharp
public static class CreateProduct
{
    public record Command(string Name);

    public static CqrsOutput Handle(Command command, IProductRepository repo)
    {
        // validate with Contract.require/ensure
        // create aggregate and save
        return CqrsOutput.Ok();
    }
}
```

## Testing Style (xUnit + BDDfy)

```csharp
public sealed class CreateProductUseCaseTests
{
    [Fact]
    public void Create_product_successfully()
    {
        this.BDDfy();
    }

    void Given_valid_product_input() { }
    void When_I_execute_create_product() { }
    void Then_the_product_is_created() { }
    void And_a_domain_event_is_emitted() { }
}
```

## Quick Start Template for LLM Tasks

When you need to implement a new feature:
1. Find the closest example in `.dev/standards/examples/`
2. Follow naming rules:
   - Use case: `<Operation><Aggregate>UseCase`
   - Handler: `<Operation><Aggregate>Handler` or Wolverine handler class
   - Input/Output: `<Operation><Aggregate>Request`, `<Aggregate>Response`
3. Apply correct patterns:
   - Command: handler returns `CqrsOutput`
   - Query: handler returns custom output DTOs
   - Test: xUnit + BDDfy (Gherkin-style naming), no BaseTestClass

## Common Pitfalls
1. Do not auto-generate ezDDD framework classes
2. Do not use EF Core lazy-loading proxies
3. Do not inject Wolverine `IMessageBus` into use cases
4. Do not directly operate on other Aggregates
5. Do not call Aggregate methods directly in tests

## Prompting the LLM

Initial conversation template:
```markdown
I am using DDD + Clean Architecture + CQRS + Event Sourcing in .NET.
Please follow these references to learn the coding style:

1. Project memory: CLAUDE.md (TODO: replace with .NET memory doc)
2. Learning path: .dev/guides/LEARNING-PATH.md
3. Code templates: .ai/CODE-TEMPLATES.md
4. Prompts: .ai/assets/

Important rules:
- Preserve ezDDD/ezSpec concepts even if .NET tooling differs
- Aggregate state changes only via Apply/When
- Use case tests must be xUnit + BDDfy (no BaseTestClass)
- No EF Core lazy loading
```

Specific task prompt patterns:

Create new Aggregate:
```markdown
Please implement [Aggregate] root:
- Operations: [list]
- Fields: [list]
- Business rules: [list]

Please produce:
1. [Aggregate].cs (Aggregate root)
2. [Aggregate]Events.cs (Domain Events)
3. [Aggregate]Id.cs (Value Object)
4. Create[Aggregate]UseCase + handler
5. Create[Aggregate] tests (BDDfy with Gherkin-style naming)
```

Add new feature:
```markdown
Add [feature] to [Aggregate]:
- Requirements: [list]
- Inputs: [list]
- Rules: [list]

Please produce:
1. Aggregate method and new event
2. Update Apply/When for the new event
3. [Operation][Aggregate] handler
4. Tests (xUnit + BDDfy)
```

Code review:
```markdown
Please review this code for DDD + CA compliance:

[code]

Check:
1. Dependency direction (inner layers only)
2. Aggregate Apply/When pattern
3. Domain Events + Value Objects
4. Command/Query separation
5. Tests follow xUnit + BDDfy (no BaseTestClass)
```

## Prompting Best Practices

Do:
1. Provide specific reference file paths
2. Use consistent terms (Aggregate, Use Case, Domain Event)
3. Ask for complete code sets (not fragments)
4. Explicitly specify required patterns (CQRS, event sourcing)

Do not:
1. Assume the LLM remembers prior context
2. Omit business rules and requirements
3. Accept outputs that violate the rules
4. Skip test requests

## Correction Loop
When the output violates rules:
1. Point to the exact rule (cite the relevant .md file)
2. Provide a correct reference example
3. Explain the principle behind the rule
4. Ask for a regenerated solution





