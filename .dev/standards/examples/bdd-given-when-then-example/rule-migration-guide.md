# Rule Migration Guide (ezSpec -> BDDfy)

This guide migrates ezSpec Rule usage into BDDfy tests with Gherkin-style naming.

## Migration Steps

### 1. Analyze Existing Scenarios
Group scenarios by business intent.

### 2. Define Rules as BDDfy Groupings
Use a consistent naming convention to keep Rule intent visible:
```
Rule_<RuleName>__<ScenarioName>()
```

### 3. Group Scenarios Under Each Rule
```csharp
[Fact]
public void Rule_Input_validation_reject_empty_name()
{
    this.Given(_ => Given_input_with_empty_name())
        .When(_ => When_i_execute())
        .Then(_ => Then_rejected_for_validation())
        .BDDfy();
}
```

### 4. Use Shared Step Methods for Setup
Create reusable `Given_*` methods and call them in multiple scenarios.
TODO: If BDDfy Story/Scenario attributes are adopted, map Rule to Story metadata.

## Example

Before:
```
Create_order_successfully()
Reject_duplicate_order_number()
Reject_empty_customer_id()
Reject_negative_amount()
```

After:
```
Rule_Successful_creation_create_order_successfully()
Rule_Input_validation_reject_empty_customer_id()
Rule_Input_validation_reject_negative_amount()
Rule_Duplicate_validation_reject_duplicate_order_number()
```

## Checklist

- [ ] Group scenarios by business intent
- [ ] Use Rule-prefixed test method names
- [ ] Share Given/When/Then methods across scenarios
- [ ] Verify Rule grouping via naming or TODO: Story metadata
