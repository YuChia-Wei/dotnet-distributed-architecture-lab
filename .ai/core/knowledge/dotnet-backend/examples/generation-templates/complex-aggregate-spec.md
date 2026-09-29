# Complex Aggregate Specification Template

Use this YAML template to describe complex aggregates for LLM code generation.
It is language-agnostic and works for .NET implementations.

## Template Structure

### 1. Aggregate Overview
```yaml
aggregate:
  name: [AggregateRootName]
  description: [Business purpose and responsibility]
  bounded_context: [Context name]
  invariants:
    - [Business rule 1 that must always be true]
    - [Business rule 2 that must always be true]
```

### 2. Entity Hierarchy
```yaml
entities:
  root:
    name: [AggregateRootName]
    id_type: [IdType]
    properties:
      - name: [propertyName]
        type: [type]
        description: [purpose]
        constraints: [validation rules]

  children:
    - name: [EntityName]
      parent: [ParentEntityName]
      id_type: [IdType or embedded]
      cardinality: [one-to-one | one-to-many]
      properties:
        - name: [propertyName]
          type: [type]
          description: [purpose]
      invariants:
        - [Entity-specific business rules]
```

### 3. Value Objects
```yaml
value_objects:
  - name: [ValueObjectName]
    properties:
      - name: [propertyName]
        type: [type]
        validation: [rules]
    used_by: [List of entities using this VO]
```

### 4. Domain Events
```yaml
domain_events:
  - name: [EventName]
    trigger: [What action causes this event]
    properties:
      - name: [propertyName]
        type: [type]
        source: [Where value comes from]
```

### 5. Commands and Business Operations
```yaml
commands:
  - name: [CommandName]
    description: [What this command does]
    parameters:
      - name: [paramName]
        type: [type]
        required: [true/false]
    validations:
      - [Validation rule]
    side_effects:
      - [What happens as result]
    events: [List of events emitted]
```

### 6. Aggregate Relationships
```yaml
relationships:
  - type: [association | composition | aggregation]
    from: [EntityName]
    to: [EntityName]
    cardinality: [1..1 | 1..* | 0..* | etc]
    navigation: [unidirectional | bidirectional]
    cascade: [operations that cascade]
```

## Usage Tips

- Define boundaries, invariants, and events first.
- Prefer business language over technical terms.
- Include edge cases and constraints that must be enforced.
