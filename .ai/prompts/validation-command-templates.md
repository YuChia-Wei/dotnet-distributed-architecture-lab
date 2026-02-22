# Validation Commands & Report Template (Dotnet)

## Purpose
Standardize how to run validation checks and how to report results for review and compliance sign-off.

## Validation Command Set
> Commands are templates; adapt paths to the active aggregate/use case.

### 1) Spec Compliance Gate (Mandatory)
```
# read specs + generate compliance checklist + validate tests
./.ai/scripts/check-spec-compliance.sh <spec-file> <task-name>
```

### 2) Repository Compliance (Optional but recommended)
```
./.ai/scripts/check-repository-compliance.sh <path>
```

### 3) Targeted Test Runs (xUnit)
```
# run all tests
 dotnet test

# run specific project
 dotnet test src/tests/Application/<Aggregate>/<Aggregate>.Tests.csproj

# run specific test via filter
 dotnet test --filter FullyQualifiedName~<TestClassOrMethod>
```

## Output Format (Compliance Report)
```
╔════════════════════════════════════════════════════════════════╗
║               SPEC COMPLIANCE REPORT (.NET)                   ║
╠════════════════════════════════════════════════════════════════╣
║ Problem Frame: <domain>/<frame-type>/<use-case>               ║
║ Aggregate: <Aggregate>                                        ║
║ Environment: <inmemory|outbox|eventsourcing>                  ║
╠════════════════════════════════════════════════════════════════╣
║ CATEGORY                    │ COVERED │ TOTAL │ RATE │ STATUS ║
╠════════════════════════════════════════════════════════════════╣
║ Use Case Input Fields       │   0     │   0   │  0%  │  ❌    ║
║ Service Preconditions       │   0     │   0   │  0%  │  ❌    ║
║ Aggregate Behavior          │   0     │   0   │  0%  │  ❌    ║
║ Domain Event Attributes     │   0     │   0   │  0%  │  ❌    ║
║ Constraints (C1–Cn)         │   0     │   0   │  0%  │  ❌    ║
║ Error Handling              │   0     │   0   │  0%  │  ❌    ║
║ Scenario / AC Coverage      │   0     │   0   │  0%  │  ❌    ║
║ Then Condition Coverage     │   0     │   0   │  0%  │  ❌    ║
║ Contract Semantics (L3)     │   0     │   0   │  0%  │  ❌    ║
║ GWT Semantics (L4)          │   0     │   0   │  0%  │  ❌    ║
╠════════════════════════════════════════════════════════════════╣
║ OVERALL COMPLIANCE          │   0     │   0   │  0%  │  ❌    ║
╚════════════════════════════════════════════════════════════════╝

Missing Items:
- <SpecRef>: <description> → <target file + method>
- <SpecRef>: <description> → <target file + method>

Remediation Actions:
1) [TEST] <file> :: <method>
   - Action: add assertion for <then condition>
2) [PRODUCTION] <file> :: <method>
   - Action: add ensure() for <postcondition>

VERDICT: NOT COMPLIANT (must reach 100% gate)
```

## Notes
- Gate is **100%**. Any deficit requires remediation and re-run.
- Keep reports in task results and link to spec references (scenario id, AC id, PRE/POST id).
