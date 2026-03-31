# Prevent DI Startup Failures Guide (Dotnet)

## Problem Description
When initializing a new project, two fatal errors appear frequently:

### Error 1: DI registration missing
```
No service for type 'IRepository<Product, ProductId>' has been registered.
```

### Error 2: DbContext configuration missing
```
Unable to resolve service for type 'AppDbContext' while attempting to activate ...
```

## Root Cause Analysis

### 1. Repository registration gap
- Outbox profile requires the full outbox registration chain.
- Missing any dependency breaks DI registration for repositories.

### 2. DbContext auto-registration
- EF Core will attempt to connect when registered.
- InMemory profile must not register EF Core or a real database.

### 3. Dependency chain (Outbox)
```
CreateProductUseCase
  -> IRepository<Product, ProductId>
     -> OutboxRepository
        -> OutboxStore / OutboxClient
           -> DbContext + Wolverine Outbox
```

## Problem 3: Profile configuration complexity

### Common challenges
1. Conditional DI registration
2. EF Core setup conflicts in InMemory
3. Multi-layer outbox dependency registration

### Solution reference
- `.dev/guides/PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md`

## Protection Mechanisms

### Step 1: Pre-checks

#### 1.1 Profile selection
```bash
echo "Planned profile: [inmemory/outbox]"
```

#### 1.2 If Outbox profile is selected, ensure these exist
- [ ] Data class implementing OutboxData
- [ ] Mapper with nested OutboxMapper
- [ ] EF Core DbContext configured
- [ ] Wolverine durable outbox enabled
- [ ] Repository registration wired

### Step 2: Progressive implementation strategy

#### Option A: InMemory first, Outbox later (recommended)
```csharp
if (env.IsEnvironment("inmemory") || env.IsEnvironment("test-inmemory"))
{
    services.AddInMemoryProfile();
}
```

#### Option B: Direct Outbox (requires full chain)
Ensure all outbox components are registered in one pass.

### Step 3: Required configuration templates

#### 3.1 appsettings.json (default)
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  }
}
```

Note: set the environment via `ASPNETCORE_ENVIRONMENT` or launchSettings; do not hardcode it inside appsettings.

#### 3.2 appsettings.inmemory.json
```json
{
  "Data": { "DisableEfCore": true }
}
```

#### 3.3 appsettings.outbox.json
```json
{
  "ConnectionStrings": {
    "Outbox": "Host=localhost;Port=5432;Database=aiscrum;Username=postgres;Password=root"
  }
}
```

### Step 4: Verification commands
```bash
dotnet build
ASPNETCORE_ENVIRONMENT=inmemory dotnet run
ASPNETCORE_ENVIRONMENT=inmemory dotnet test
```

### Step 5: Diagnosis flow

If repository DI fails:
1. Check environment:
   ```bash
   echo $ASPNETCORE_ENVIRONMENT
   ```
2. Check profile registrations in code
3. Ensure outbox registrations exist for outbox profile
4. Ensure EF Core is not registered for InMemory

## DO / DON'T

DO
1. Start with InMemory to confirm app bootstraps
2. Add Outbox in a second phase
3. Keep registrations profile-specific
4. Validate DI before running tests

DON'T
1. Skip InMemory phase unless outbox chain is complete
2. Register EF Core in InMemory
3. Mix profile registrations in the same module
4. Ignore DI exceptions

## Implementation Order Suggestion
1. Create DateProvider
2. Bootstrap the host + DI
3. Implement domain models
4. Wire InMemory profile
5. Add Outbox profile (optional)

## References
- `.dev/guides/PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md`
- `.dev/guides/FRAMEWORK-API-INTEGRATION-GUIDE.md`
- `.ai/COMMON-PITFALLS.md`


