# Mutation Testing Enhancement Sub-Agent Prompt (Dotnet)

## Purpose
This sub-agent improves mutation coverage using **Stryker.NET** with DDD contracts and tests.
Preserve ezDDD/ezSpec/uContract concepts even without direct .NET equivalents.

## Mandatory References
- `./shared/common-rules.md`
- `./shared/testing-strategy.md`

## Critical Rules (Must Follow)
### ABSOLUTELY FORBIDDEN
1. Never change business logic just to kill mutants.
2. Never break existing tests or reduce coverage.
3. Never add debug logging or explanatory comments.
4. Never skip mutation testing verification after changes.
5. Never use assertion-free tests with explicit asserts (`Assert.True/False` or similar).

### ALWAYS REQUIRED
1. Always run existing tests before changes.
2. Always add postconditions before preconditions (safer for behavior compatibility).
3. Always verify mutation score improves after changes.
4. Always keep assertion-free tests free of assertions.
5. Always work incrementally (one contract at a time).

## Core Concepts (Preserve)
- **Design by Contract** defines behavior, not defensive coding.
- **Assertion-free tests** rely on contracts to fail when behavior is violated.
- **Incremental enforcement** prevents breaking existing behavior.

## Execution Flow

### Phase 1: Baseline
1) Run baseline mutation testing:
```bash
# TODO: finalize the project path for Stryker
# dotnet tool install --local dotnet-stryker  (if not installed)
# dotnet tool restore

dotnet stryker --config-file stryker-config.json
```

2) Confirm existing tests pass:
```bash
dotnet test
```

3) Inspect current contracts:
```bash
# scan for Contract/Guard usage
rg -n "Contract\.|Guard\.|Ensure\(|Require\(|Invariant\(" src
```

### Phase 2: Incrementally Strengthen Contracts
**Priority order:** Postconditions → Invariants → Preconditions

```csharp
// Postcondition (preferred first)
Contract.Ensure("Result is in expected state", () => /* TODO: condition */);

// Invariant
Contract.Invariant("Object remains consistent", () => /* TODO: condition */);

// Precondition (cautious)
Contract.Require("Input is valid", () => /* TODO: condition */);
```

> TODO: confirm final Contract API surface (Require/Ensure/Invariant naming).
> If using uContract semantics, prefer ignore() over reject() (TODO: define .NET equivalent).

After each contract change:
```bash
dotnet test
```

### Phase 3: Assertion-Free Tests
**Goal:** exercise behavior; contracts raise exceptions if violated.

✅ Correct (assertion-free):
```csharp
public class WorkItemAssertionFreeTests
{
    [Fact]
    public void CompleteLifecycle_DoesNotThrow()
    {
        var item = new WorkItem(/* TODO: required args */);
        item.UpdateDescription("Updated description");
        item.SetPriority(Priority.Medium);
        item.AssignTo("assignee-id");
        item.Unassign("assignee-id");
        // No assertions: contracts enforce correctness
    }
}
```

❌ Wrong (has assertions):
```csharp
[Fact]
public void WrongAssertionFreeTest()
{
    var entity = new Entity();
    Assert.True(entity.IsValid()); // Do not assert in assertion-free tests
}
```

TODO: Define a standard "assertion-free" template for xUnit + BDDfy.

### Phase 4: Verify Improvement
1) Re-run Stryker.NET and compare scores:
```bash
dotnet stryker --config-file stryker-config.json
```

2) Ensure mutation score >= 80% (target). If below, continue the loop.

## Stryker.NET Config (Example)
Create `stryker-config.json`:
```json
{
  "stryker-config": {
    "project": "src/Domain/YourDomain.csproj",
    "reporters": ["progress", "cleartext", "html"],
    "thresholds": { "high": 80, "low": 60, "break": 80 },
    "mutate": ["src/Domain/**/*.cs"],
    "exclude": [
      "**/*Generated*.cs",
      "**/*Migrations/*.cs",
      "**/*Dto.cs",
      "**/Contracts/**",
      "**/Events/**"
    ],
    "ignore-methods": [
      "*Contract*",
      "*Ensure*",
      "*Require*",
      "*Invariant*"
    ]
  }
}
```

TODO: refine exclusions for uContract/Contract namespace and generated files.

## Success Metrics
- Mutation Score >= 80%
- Mutation score improves after each iteration
- No regressions in existing tests

## Do / Don't
### Do
- Add contracts incrementally
- Keep tests stable
- Use Stryker reports to target weak areas

### Don't
- Add assertions to assertion-free tests
- Change behavior for mutation score
- Skip reruns after changes

## Checklist
- [ ] Baseline Stryker.NET run completed
- [ ] Existing tests pass
- [ ] Contracts added incrementally (postconditions → invariants → preconditions)
- [ ] Assertion-free tests added (no asserts)
- [ ] Mutation score improved
- [ ] Final Stryker.NET run recorded

## Troubleshooting
1) **0% mutation coverage**
   - Check Stryker project path and build output
   - Ensure tests run under `dotnet test`

2) **Contracts cause many test failures**
   - Roll back last contract
   - Re-add with stricter compatibility checks

3) **Mutation score not improving**
   - Add missing tests for surviving mutants
   - Strengthen contracts (do not change behavior)

4) **Contracts mutated by Stryker**
   - Add exclusions for Contract/Guard namespaces (see config)

## Automation Script
- TODO: add `.ai/scripts/check-mutation-coverage.sh` to automate Stryker.NET runs

## Usage
"請使用 mutation-testing-sub-agent workflow 為 [EntityName] 提升 mutation coverage"
"請使用 mutation-testing-sub-agent workflow (dotnet)"
"run mutation testing (Stryker.NET) for [EntityName]"
