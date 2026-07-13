# Version And Configuration Placeholder Guide (.NET)

This guide defines how template placeholders are resolved. It intentionally does not prescribe a product name, dependency version, port, provider, schema, environment, or credential.

## Evidence Sources

Resolve values from target-repository evidence in this order:

1. authoritative project and configuration files;
2. repository-owned standards or decisions;
3. a generated `.dev/project-config.yaml` that cites the discovered evidence;
4. an explicit user or team decision for a value that does not yet exist.

Do not invent a value to make replacement succeed. Keep the placeholder unresolved and report the missing decision instead.

## Placeholder Catalog

### Project Identity

- `{rootNamespace}`: namespace confirmed from project files or repository convention.
- `{projectName}`: target project or solution name.
- `{projectVersion}`: version from the target repository's version source.

### .NET And Dependencies

- `{dotnetSdkVersion}`: SDK version from `global.json`, project configuration, or CI evidence.
- `{targetFramework}`: target framework from the relevant project file.
- `{wolverineVersion}`, `{efCoreVersion}`, `{npgsqlVersion}`: versions from applicable package references or central package management.
- `{xunitVersion}`, `{nsubstituteVersion}`, `{bddfyVersion}`: versions from the target test project when those packages are adopted.
- `{bddStyle}`: `Given-When-Then`; BDDfy is the default narration library, but a team may opt out of the package while retaining GWT style.

Do not copy version examples into generated output as defaults.

### HTTP Host

- `{backendPort}`: port from target launch, container, orchestration, or deployment configuration.
- `{apiPrefix}`: route prefix confirmed by target endpoint or routing configuration.
- `{allowedOrigins}`: reviewed CORS origins from environment-specific configuration.

### Persistence

- `{dbProvider}`: provider confirmed from package and registration evidence.
- `{dbHost}`, `{dbPort}`, `{dbName}`, `{dbUsername}`: environment-specific values from the target configuration source.
- `{dbPasswordSecretRef}`: reference to an environment variable, secret manager key, or local developer-secret entry; never a literal password.
- `{dbConnectionStringSecretRef}`: reference to a protected connection-string source.
- `{dbSchema}`: schema confirmed from mappings, migrations, or an explicit decision.

Create separate environment placeholders only for environments the target repository actually defines, for example `{db_<environment>_Host}`. Do not assume `test`, `production`, or AI-specific databases exist or share one schema.

### Context-Dependent Names

- `{fileName}`: derived from the target artifact name.
- `{useCaseName}`: derived from the confirmed use-case term and naming standard.
- `{aggregateName}`: derived from domain language or an approved model.
- `{entityName}`: derived from the target domain context.

Do not infer domain names from historical examples in this framework.

## Processing Rules

1. Inventory placeholders in the template or specification.
2. Map every placeholder to a cited target-repository evidence source.
3. Separate non-secret configuration from secret references.
4. Replace only placeholders with confirmed values.
5. Report unresolved placeholders and the decision or evidence needed.
6. Verify generated output contains no unresolved placeholder and no copied credential.

## Credential Safety

- Never document or generate a reusable literal password, token, or connection string.
- Use environment variables, local developer-secret stores, CI/CD secret stores, or the target platform's secret manager.
- Examples may show variable names such as `${DB_PASSWORD}`, but must not assign a value.
- Treat a generated `.dev/project-config.yaml` as non-secret metadata; it may record a secret reference, not secret material.

## Optional Frontend Values

Frontend placeholders belong in a frontend/full-stack profile, not this .NET backend guide. Resolve them only when the target repository has confirmed frontend evidence and the applicable context profile defines their ownership.

## Failure Handling

- Missing value: leave it unresolved, identify the evidence gap, and consider `repo-structure-sync`.
- Conflicting values: report the conflicting sources and request a decision from the owning team.
- Stale generated summary: refresh it from authoritative repository evidence.
- Secret found in a template or summary: remove it from reusable context and rotate it through the target repository's security process if it was real.
