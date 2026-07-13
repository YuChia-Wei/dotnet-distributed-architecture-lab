# ASP.NET Core appsettings Template Set 🔧

## 🎯 Purpose
Provides complete `appsettings.json` and `appsettings.{Environment}.json` templates to prevent profile and connection configuration errors.

## 📋 Configuration File Structure

```
src/Api/
├── appsettings.json                # Primary configuration
├── appsettings.InMemory.json       # InMemory Profile
├── appsettings.Outbox.json         # Outbox Profile
├── appsettings.Test.json           # Primary test configuration
├── appsettings.Test-InMemory.json  # InMemory tests
└── appsettings.Test-Outbox.json    # Outbox tests
```

## 1️⃣ appsettings.json (Primary Configuration)

```json
{
  "App": {
    "Name": "ai-scrum"
  },
  "Profiles": {
    "Mode": "InMemory"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning",
      "Microsoft.AspNetCore": "Warning"
    }
  }
}
```

## 2️⃣ appsettings.InMemory.json (InMemory Profile)

```json
{
  "Profiles": {
    "Mode": "InMemory"
  },
  "Persistence": {
    "Provider": "InMemory"
  }
}
```

## 3️⃣ appsettings.Outbox.json (Outbox Profile)

```json
{
  "Profiles": {
    "Mode": "Outbox"
  },
  "Persistence": {
    "Provider": "PostgreSQL"
  },
  "ConnectionStrings": {
    "MainDb": "Host=${DB_HOST};Port=${DB_PORT};Database=${DB_NAME};Username=${DB_USER};Password=${DB_PASSWORD}"
  },
  "Outbox": {
    "PollingIntervalMs": 5000,
    "BatchSize": 100
  }
}
```

## 4️⃣ appsettings.Test.json (Primary Test Configuration)

```json
{
  "Profiles": {
    "Mode": "Test-InMemory"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Warning"
    }
  }
}
```

## 5️⃣ appsettings.Test-InMemory.json (InMemory Tests)

```json
{
  "Profiles": {
    "Mode": "Test-InMemory"
  },
  "Persistence": {
    "Provider": "InMemory"
  }
}
```

## 6️⃣ appsettings.Test-Outbox.json (Outbox Tests)

```json
{
  "Profiles": {
    "Mode": "Test-Outbox"
  },
  "Persistence": {
    "Provider": "PostgreSQL"
  },
  "ConnectionStrings": {
    "MainDb": "Host=${DB_HOST};Port=${DB_PORT};Database=${DB_NAME};Username=${DB_USER};Password=${DB_PASSWORD}"
  }
}
```

## 🚨 Key Configuration Details

### 1. Why Is Profiles/Mode Required?
The profile switches between InMemory and Outbox behavior, preventing conflicts between configuration sets.

### 2. Profile Naming Rules
- `InMemory`
- `Outbox`
- `Test-InMemory`
- `Test-Outbox`

### 3. Database Port Separation
- Development environment: 5432
- Test environment: 5800

## 🔍 Diagnostic Commands

```bash
# Check the environment variable
echo $ASPNETCORE_ENVIRONMENT

# Start with the specified environment
ASPNETCORE_ENVIRONMENT=Outbox dotnet run --project src/Api
```

## ⚠️ Common Errors and Solutions

### Error 1: The Correct appsettings.{Environment}.json Is Not Loaded
**Solution**: Verify that `ASPNETCORE_ENVIRONMENT` is configured correctly.

### Error 2: The Repository Cannot Be Resolved
**Solution**: Verify that the DI registrations for the corresponding profile exist.

## 📝 Best Practices

1. Start development with the InMemory profile.
2. Ensure the Outbox profile has a corresponding database.
3. Specify the profile explicitly during testing.
4. Override sensitive settings with environment variables in production.
