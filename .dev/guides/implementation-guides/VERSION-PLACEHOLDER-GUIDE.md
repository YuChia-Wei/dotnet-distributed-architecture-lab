# Version Placeholder Guide (Dotnet)

This guide documents all placeholders that should be automatically replaced when generating code from templates.

## Configuration Source
All placeholder values come from `.dev/project-config.yaml`.

## Available Placeholders

### Basic Project Information
- `{rootNamespace}` -> MyScrum
- `{projectName}` -> MyScrum
- `{projectVersion}` -> 0.1.0

### .NET & Runtime Versions
- `{dotnetSdkVersion}` -> 8.0.x
- `{aspnetCoreVersion}` -> 8.0.x

### Dependencies
- `{wolverineVersion}` -> 3.x (set in project-config.yaml)
- `{efCoreVersion}` -> 8.x
- `{npgsqlVersion}` -> 8.x
- `{xunitVersion}` -> 2.x
- `{nsubstituteVersion}` -> 5.x
- `{bddfyVersion}` -> 0.x (set in project-config.yaml)
- `{bddStyle}` -> Gherkin-style-naming

### Backend Configuration
- `{backendPort}` -> 9090
- `{apiPrefix}` -> /v1/api

### Database Configuration (Common)
- `{dbProvider}` -> PostgreSQL
- `{dbSchema}` -> message_store

### Test Environment Database
- `{dbTestHost}` -> localhost
- `{dbTestPort}` -> 5800
- `{dbTestName}` -> board_test
- `{dbTestUsername}` -> postgres
- `{dbTestPassword}` -> root
- `{dbTestConnectionString}` -> Host=localhost;Port=5800;Database=board_test;Username=postgres;Password=root
- `{dbTestSchema}` -> message_store

### Production Environment Database
- `{dbProductionHost}` -> localhost
- `{dbProductionPort}` -> 5500
- `{dbProductionName}` -> board
- `{dbProductionUsername}` -> postgres
- `{dbProductionPassword}` -> root
- `{dbProductionConnectionString}` -> Host=localhost;Port=5500;Database=board;Username=postgres;Password=root
- `{dbProductionSchema}` -> message_store

### AI Environment Database
- `{dbAiHost}` -> localhost
- `{dbAiPort}` -> 6600
- `{dbAiName}` -> board_ai
- `{dbAiUsername}` -> postgres
- `{dbAiPassword}` -> root
- `{dbAiConnectionString}` -> Host=localhost;Port=6600;Database=board_ai;Username=postgres;Password=root
- `{dbAiSchema}` -> message_store

### Frontend Configuration
- `{frontendFramework}` -> React
- `{frontendLanguage}` -> TypeScript
- `{frontendPort}` -> 3000
- `{frontendBuildTool}` -> Vite
- `{reactVersion}` -> 18.3.1
- `{typescriptVersion}` -> 5.5.3
- `{viteVersion}` -> 5.4.1

### Dynamic Placeholders (Context-Dependent)
- `{fileName}` -> extracted from file name (e.g., task-delete-task -> delete-task)
- `{useCaseName}` -> PascalCase (e.g., delete-task -> DeleteTask)
- `{aggregateName}` -> extracted from context (e.g., .dev/tasks/feature/pbi -> pbi)
- `{entityName}` -> extracted from context

## Placeholder Processing Rules

### When to Process Placeholders
1. Always check for placeholders when reading spec files or templates
2. Read `.dev/project-config.yaml` to get latest values
3. Replace all placeholders before generating code

### Processing Steps
1. Identify all placeholders in the template/spec
2. Load configuration from `.dev/project-config.yaml`
3. Replace placeholders with actual values
4. Validate all placeholders have been replaced

### Common Issues
- Missing placeholder values -> check project-config.yaml
- Duplicate placeholders -> check templates and sync
- Context-dependent placeholders -> extract from file path or naming convention

## Usage Notes

1. Automatic replacement: AI replaces placeholders when generating code
2. Single source of truth: `.dev/project-config.yaml`
3. Environment-specific DB config for test/production/ai
4. Schema note: all PostgreSQL connections use `message_store` schema only

## Important Reminders

- Database password is `root` (not password1)
- All PostgreSQL connections use `message_store` schema
- ASP.NET Core ports follow `{backendPort}`
- PostgreSQL container ports:
  - Test: 5800
  - Production: 5500
  - AI: 6600

