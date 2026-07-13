using Microsoft.CodeAnalysis;

namespace DotnetBackendAnalyzers;

internal static class RuleDescriptors
{
    public static readonly DiagnosticDescriptor RepositoryQueryMethod = new(
        id: "DBA1001",
        title: "Repository contract violation",
        messageFormat: "{0}",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Error,
        isEnabledByDefault: true,
        description: "Aggregate repositories, query repositories, and compatibility contracts must preserve their distinct semantic boundaries.");

    public static readonly DiagnosticDescriptor UseCaseServiceProviderInjection = new(
        id: "DBA1002",
        title: "Use case or handler should not inject IServiceProvider",
        messageFormat: "Use case or handler '{0}' injects IServiceProvider; inject explicit dependencies instead",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Error,
        isEnabledByDefault: true,
        description: "Use cases should declare explicit dependencies and avoid service locator style access.");

    public static readonly DiagnosticDescriptor AggregateInfrastructureDependency = new(
        id: "DBA1003",
        title: "Aggregate should not depend on infrastructure types",
        messageFormat: "Aggregate/entity '{0}' references infrastructure type '{1}'",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Warning,
        isEnabledByDefault: true,
        description: "Domain aggregates and entities must remain independent from infrastructure concerns such as EF Core DbContext.");

    public static readonly DiagnosticDescriptor ControllerApiAttribute = new(
        id: "DBA1004",
        title: "Controller should declare ApiControllerAttribute",
        messageFormat: "Controller '{0}' does not declare ApiControllerAttribute",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Warning,
        isEnabledByDefault: true,
        description: "ASP.NET Core API controllers should use ApiControllerAttribute for consistent API behavior and validation.");

    public static readonly DiagnosticDescriptor ControllerPersistenceAccess = new(
        id: "DBA1005",
        title: "Controller should not access persistence directly",
        messageFormat: "Controller '{0}' directly references persistence member or type '{1}'",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Error,
        isEnabledByDefault: true,
        description: "Controllers should delegate application behavior and must not use DbContext or SaveChanges directly.");

    public static readonly DiagnosticDescriptor ControllerDirectConstruction = new(
        id: "DBA1006",
        title: "Controller should not construct handlers or use cases",
        messageFormat: "Controller '{0}' directly constructs '{1}'; inject a Use Case interface instead",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Error,
        isEnabledByDefault: true,
        description: "Controllers should receive explicit Use Case interfaces through dependency injection.");

    public static readonly DiagnosticDescriptor MapperMustBeStatic = new(
        id: "DBA1007",
        title: "Mapper should be static",
        messageFormat: "Mapper '{0}' must be a static class",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Warning,
        isEnabledByDefault: true,
        description: "Object mappers are deterministic pure transformations and must not have instance state or an injection graph.");

    public static readonly DiagnosticDescriptor MapperForbiddenDependency = new(
        id: "DBA1008",
        title: "Mapper should not depend on application or persistence services",
        messageFormat: "Mapper '{0}' references forbidden dependency type '{1}'",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Warning,
        isEnabledByDefault: true,
        description: "Object mappers must not depend on repositories, use cases, or handlers.");

    public static readonly DiagnosticDescriptor EventSourcedAggregateDirectMutation = new(
        id: "DBA1009",
        title: "Event-sourced aggregate state should change through event transitions",
        messageFormat: "Event-sourced aggregate '{0}' mutates member '{1}' outside a When transition",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Warning,
        isEnabledByDefault: true,
        description: "EsAggregateRoot state changes must be applied by event transition methods so replay produces the same state.");

    public static readonly DiagnosticDescriptor UseCaseDependencyResolution = new(
        id: "DBA1010",
        title: "Use case should not use service locator or attribute injection",
        messageFormat: "Use case or handler '{0}' uses forbidden dependency resolution '{1}'",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Error,
        isEnabledByDefault: true,
        description: "Use cases must declare explicit constructor dependencies and must not use service locator or attribute-based injection.");

    public static readonly DiagnosticDescriptor MixedCommandQueryHandler = new(
        id: "DBA1011",
        title: "Handler should not mix command and query responsibilities",
        messageFormat: "Handler '{0}' handles both command and query marker types",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Error,
        isEnabledByDefault: true,
        description: "CQRS handlers must keep command and query responsibilities separate.");

    public static readonly DiagnosticDescriptor UseCaseDirectRepositoryConstruction = new(
        id: "DBA1012",
        title: "Use case should not construct repositories",
        messageFormat: "Use case or handler '{0}' directly constructs repository type '{1}'",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Error,
        isEnabledByDefault: true,
        description: "Repository ports must be injected into use cases; concrete repository construction belongs in the composition root.");

    public static readonly DiagnosticDescriptor ControllerForbiddenDependency = new(
        id: "DBA1014",
        title: "Controller must depend on a Use Case boundary",
        messageFormat: "Controller '{0}' injects forbidden dependency '{1}'; inject a Use Case interface instead",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Error,
        isEnabledByDefault: true,
        description: "Controllers must not inject handlers, buses, dispatchers, write repositories, or Domain services. Query repositories and query services are reserved for explicitly selected pure-query endpoints.");

    public static readonly DiagnosticDescriptor UseCaseContractShape = new(
        id: "DBA1015",
        title: "Use Case contract shape is invalid",
        messageFormat: "Use Case '{0}' violates the canonical contract: {1}",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Error,
        isEnabledByDefault: true,
        description: "Use Cases use ExecuteAsync, a non-optional CancellationToken, and transport-neutral input/output contracts, and must not expose Handler entry points.");

    public static readonly DiagnosticDescriptor UseCaseForbiddenDependency = new(
        id: "DBA1016",
        title: "Use Case dependency is forbidden",
        messageFormat: "Use Case '{0}' depends on forbidden type '{1}'",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Error,
        isEnabledByDefault: true,
        description: "Use Cases must not depend directly on IMessageBus, mediators/dispatchers, transport contracts, or another Use Case.");

    public static readonly DiagnosticDescriptor DispatchHandlerBoundary = new(
        id: "DBA1017",
        title: "Dispatch Handler must adapt to one Use Case",
        messageFormat: "Dispatch Handler '{0}' violates the Handler boundary: {1}",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Error,
        isEnabledByDefault: true,
        description: "Command and Query dispatch handlers map delivery input and invoke exactly one Use Case without depending on repositories or Domain services.");

    public static readonly DiagnosticDescriptor ProjectionWriteOperation = new(
        id: "DBA1013",
        title: "Projection should not perform persistence writes",
        messageFormat: "Projection '{0}' calls persistence write operation '{1}'",
        category: DiagnosticCategories.Architecture,
        defaultSeverity: DiagnosticSeverity.Warning,
        isEnabledByDefault: true,
        description: "Projection services are read-side ports and must not call DbContext or DbSet write operations.");
}
