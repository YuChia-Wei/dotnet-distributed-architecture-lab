# Profile-Based Testing Architecture Guide (.NET)

## Applicability

Profile-based testing lets the same behavioral tests exercise multiple infrastructure configurations through fixtures and dependency injection. It is an optional target-repository design, not a claim about repositories that adopt this context framework.

Before using this pattern, discover the target repository's test projects, configuration mechanism, registered providers, and supported profile names. Do not create profiles, settings files, or external services solely because they appear in this guide.

```text
Use-case or integration tests
           |
        fixture
           |
environment/configuration-selected DI
           |
one of the providers confirmed by the target repository
```

## Profile Inventory

Record confirmed profiles before authoring commands or matrices:

| Profile placeholder | Purpose | Provider | Configuration evidence | External dependency |
| --- | --- | --- | --- | --- |
| `<fast-profile>` | Fast behavioral feedback | `<confirmed-provider>` | `<confirmed-settings-or-fixture>` | `<none-or-confirmed-service>` |
| `<integration-profile>` | Infrastructure integration | `<confirmed-provider>` | `<confirmed-settings-or-fixture>` | `<confirmed-service>` |

Profile names, provider names, settings files, and roadmap entries must come from repository evidence or an explicit team decision. A generated `.dev/project-config.yaml`, when present, may summarize that evidence.

## Test Authoring Guide

### 1. Use fixtures for shared profile setup

```csharp
public sealed class CreateProductFeature : IClassFixture<TestProfileFixture>
{
    private readonly TestProfileFixture _fixture;

    public CreateProductFeature(TestProfileFixture fixture)
    {
        _fixture = fixture;
    }
}
```

Rename the fixture and types to match the target repository.

### 2. Resolve ports through dependency injection

```csharp
var useCase = _fixture.Services.GetRequiredService<ICreateProductUseCase>();
var repository = _fixture.Services.GetRequiredService<IAggregateRepository<Product, ProductId>>();
```

Do not instantiate a concrete repository in a behavior test intended to run across providers.

### 3. Use Given-When-Then style

BDDfy is the default test narration library for this AI context. A target team may explicitly opt out of the package and related `.feature` tooling; tests must still use Given-When-Then structure and naming rather than Arrange-Act-Assert. `.feature` files are supported when requested or supplied, but are not mandatory.

```csharp
public sealed class CreateProductFeature : IClassFixture<TestProfileFixture>
{
    [Fact]
    public void Create_product_successfully()
    {
        this.BDDfy();
    }

    void Given_valid_product_creation_input() { }
    void When_I_execute_the_create_product_use_case() { }
    void Then_the_product_is_created_successfully() { }
    void And_a_domain_event_is_emitted() { }
}
```

If BDDfy is not adopted, retain explicit `Given...`, `When...`, and `Then...` sections or helper names using the target test framework.

## Running Profiles

Use the configuration selector already supported by the target repository. For an ASP.NET Core environment-based design, parameterized examples are:

```bash
ASPNETCORE_ENVIRONMENT=<fast-profile> dotnet test <test-project>
ASPNETCORE_ENVIRONMENT=<integration-profile> dotnet test <test-project> --filter <target-filter>
```

For IDE runs, set the same confirmed selector in the IDE's run configuration. Do not set or mutate a process-wide environment selector inside individual test classes.

## Coverage Matrix

Build the matrix from implemented evidence instead of copying a fixed provider roadmap:

| Test suite | `<fast-profile>` | `<integration-profile>` | Evidence |
| --- | --- | --- | --- |
| Use-case behavior | `<supported?>` | `<supported?>` | `<test project or command>` |
| HTTP behavior | `<supported?>` | `<supported?>` | `<test project or command>` |
| Infrastructure integration | `<supported?>` | `<supported?>` | `<test project or command>` |

## Given-When-Then Access Rules

- Given establishes behavior through public application/use-case ports unless the scenario explicitly tests lower-level infrastructure.
- When invokes the behavior under test through the same intended boundary.
- Then observes outcomes through supported queries, read ports, captured messages/events, or other target-repository evidence.
- Direct aggregate or repository access must not bypass the boundary being tested. Read-only repository verification is acceptable only when the test design explicitly permits it.

When clearing captured events from Given, first wait for the fixture's documented capture condition; do not assume a specific `AwaitEvents` or `ClearEvents` API exists.

## Troubleshooting

1. DI container fails: verify the selected profile has an evidenced registration module.
2. Port resolution fails: verify the target provider registers the required abstraction.
3. Events are missing: verify the chosen fixture wires the target repository's capture mechanism.
4. Profile does not switch: verify when and where the target configuration selector is read.

## Related Documents

- `.ai/assets/tech-stacks/dotnet-backend/shared/testing-strategy.md`
- `.ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/sub-agent.yaml`
- `.dev/standards/rationale/profile-based-testing-rationale.MD`
