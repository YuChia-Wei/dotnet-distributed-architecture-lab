# ASP.NET Core Configuration Checklist 🔥

## ⚠️ Common Errors That Must Be Avoided

This checklist records configuration mistakes commonly encountered in .NET projects so they are not repeated.

## 1. Database Connection Configuration

### ❌ Error: Using the Wrong Port
```json
// Incorrect
"MainDb": "Host=${DB_HOST};Port=${DB_PORT};Database=${DB_NAME};Username=${DB_USER};Password=${DB_PASSWORD}"

// Correct
"MainDb": "Host=${DB_HOST};Port=${DB_PORT};Database=${DB_NAME};Username=${DB_USER};Password=${DB_PASSWORD}"
```

### ❌ Error: Incorrect Schema Configuration
```json
// Incorrect: schema is omitted or an incorrect key is used
"MainDb": "Host=${DB_HOST};Port=${DB_PORT};Database=${DB_NAME};Username=${DB_USER};Password=${DB_PASSWORD}"

// Correct: specify the schema in the connection string
"MainDb": "Host=${DB_HOST};Port=${DB_PORT};Database=${DB_NAME};Username=${DB_USER};Password=${DB_PASSWORD};Search Path=${DB_SCHEMA}"
```

## 2. Package Dependency Configuration

### ❌ Error: Missing Provider Package
- `Microsoft.EntityFrameworkCore.Npgsql` or `Microsoft.EntityFrameworkCore.SqlServer` is missing.

### ✅ Correct Approach
```bash
dotnet add package Microsoft.EntityFrameworkCore
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
```

## 3. Profile / Environment Configuration

### ❌ Error: Missing appsettings.{Environment}.json
Create `appsettings.InMemory.json` / `appsettings.Outbox.json` or the corresponding environment-specific files.

### ✅ Correct Approach
- Set `ASPNETCORE_ENVIRONMENT=InMemory` / `Outbox`.
- Use `IConfiguration` to read the profile.
- Do not create a second custom profile mechanism.
- Keep environment names consistent, for example `TestInMemory` / `TestOutbox`.

### ✅ Authoritative Standard
- Follow `coding-standards/profile-configuration-standards.md` for detailed mandatory rules.

## 4. WolverineFx Configuration

### ❌ Error: Handlers / Messaging Are Not Registered
**Resolution**: Verify WolverineFx service registration and assembly scanning.

## 5. EF Core Migration

### ❌ Error: Migrations Are Outdated or Not Applied
```bash
dotnet ef migrations add Init
dotnet ef database update
```
