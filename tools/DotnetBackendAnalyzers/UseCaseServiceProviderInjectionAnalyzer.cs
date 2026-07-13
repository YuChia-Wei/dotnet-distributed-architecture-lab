using System.Collections.Immutable;
using System.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.Diagnostics;

namespace DotnetBackendAnalyzers;

[DiagnosticAnalyzer(LanguageNames.CSharp)]
public sealed class UseCaseServiceProviderInjectionAnalyzer : DiagnosticAnalyzer
{
    public override ImmutableArray<DiagnosticDescriptor> SupportedDiagnostics =>
        ImmutableArray.Create(
            RuleDescriptors.UseCaseServiceProviderInjection,
            RuleDescriptors.UseCaseDependencyResolution,
            RuleDescriptors.MixedCommandQueryHandler,
            RuleDescriptors.UseCaseDirectRepositoryConstruction,
            RuleDescriptors.UseCaseContractShape,
            RuleDescriptors.UseCaseForbiddenDependency,
            RuleDescriptors.DispatchHandlerBoundary);

    public override void Initialize(AnalysisContext context)
    {
        context.ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None);
        context.EnableConcurrentExecution();
        context.RegisterSymbolAction(AnalyzeNamedType, SymbolKind.NamedType);
        context.RegisterSyntaxNodeAction(AnalyzeObjectCreation, Microsoft.CodeAnalysis.CSharp.SyntaxKind.ObjectCreationExpression);
    }

    private static void AnalyzeNamedType(SymbolAnalysisContext context)
    {
        var type = (INamedTypeSymbol)context.Symbol;
        if (type.TypeKind == TypeKind.Interface && type.Name.EndsWith("UseCase", System.StringComparison.Ordinal))
        {
            AnalyzeUseCaseContract(context, type);
            return;
        }

        if (type.TypeKind != TypeKind.Class || !LooksLikeUseCaseOrHandler(type))
        {
            return;
        }

        if (type.Name.EndsWith("UseCase", System.StringComparison.Ordinal))
        {
            AnalyzeUseCaseImplementation(context, type);
        }

        if (IsDispatchHandler(type))
        {
            AnalyzeDispatchHandler(context, type);
        }

        var handlesCommand = false;
        var handlesQuery = false;

        foreach (var member in type.GetMembers())
        {
            if (member is IFieldSymbol field)
            {
                ReportForbiddenMemberType(context, type, field.Type, field.Locations, field.Name);
                continue;
            }

            if (member is IPropertySymbol property)
            {
                ReportForbiddenMemberType(context, type, property.Type, property.Locations, property.Name);
                ReportInjectionAttributes(context, type, property);
                continue;
            }

            if (member is not IMethodSymbol method)
            {
                continue;
            }

            foreach (var parameter in method.Parameters)
            {
                ReportForbiddenMemberType(context, type, parameter.Type, parameter.Locations, parameter.Name);
            }

            if (method.Name is not "Handle" and not "HandleAsync" || method.Parameters.Length == 0)
            {
                continue;
            }

            handlesCommand |= ImplementsMarker(method.Parameters[0].Type, "ICommand");
            handlesQuery |= ImplementsMarker(method.Parameters[0].Type, "IQuery");
        }

        if (handlesCommand && handlesQuery)
        {
            context.ReportDiagnostic(Diagnostic.Create(
                RuleDescriptors.MixedCommandQueryHandler,
                type.Locations[0],
                type.Name));
        }
    }

    private static void AnalyzeUseCaseContract(SymbolAnalysisContext context, INamedTypeSymbol type)
    {
        var methods = type.GetMembers().OfType<IMethodSymbol>()
            .Where(method => method.MethodKind == MethodKind.Ordinary)
            .ToArray();
        var executeMethods = methods.Where(method => method.Name == "ExecuteAsync").ToArray();

        if (executeMethods.Length != 1)
        {
            ReportUseCaseShape(context, type, "declare exactly one ExecuteAsync operation");
            return;
        }

        if (methods.Any(method => method.Name is "Handle" or "HandleAsync"))
        {
            ReportUseCaseShape(context, type, "must not expose Handle or HandleAsync");
        }

        AnalyzeExecuteAsyncShape(context, type, executeMethods[0]);
    }

    private static void AnalyzeUseCaseImplementation(SymbolAnalysisContext context, INamedTypeSymbol type)
    {
        if (type.IsAbstract)
        {
            return;
        }

        var executeMethods = type.GetMembers("ExecuteAsync").OfType<IMethodSymbol>()
            .Where(method => method.MethodKind == MethodKind.Ordinary)
            .ToArray();
        if (executeMethods.Length != 1)
        {
            ReportUseCaseShape(context, type, "implement exactly one ExecuteAsync operation");
        }
        else
        {
            AnalyzeExecuteAsyncShape(context, type, executeMethods[0]);
        }

        if (type.GetMembers().OfType<IMethodSymbol>()
            .Any(method => method.Name is "Handle" or "HandleAsync"))
        {
            ReportUseCaseShape(context, type, "must not also expose a Handler entry point");
        }

        foreach (var constructor in type.InstanceConstructors)
        {
            foreach (var parameter in constructor.Parameters)
            {
                if (!IsForbiddenUseCaseDependency(parameter.Type))
                {
                    continue;
                }

                context.ReportDiagnostic(Diagnostic.Create(
                    RuleDescriptors.UseCaseForbiddenDependency,
                    parameter.Locations.FirstOrDefault() ?? type.Locations[0],
                    type.Name,
                    parameter.Type.Name));
            }
        }
    }

    private static void AnalyzeExecuteAsyncShape(
        SymbolAnalysisContext context,
        INamedTypeSymbol type,
        IMethodSymbol method)
    {
        if (!IsTask(method.ReturnType))
        {
            ReportUseCaseShape(context, type, "ExecuteAsync must return Task or Task<T>");
        }
        else if (method.ReturnType is INamedTypeSymbol { IsGenericType: true } taskType
            && taskType.TypeArguments.Length == 1
            && IsTransportOutput(taskType.TypeArguments[0]))
        {
            ReportUseCaseShape(context, type, "HTTP, broker acknowledgement, or framework output is forbidden");
        }

        if (method.Parameters.Length == 0
            || !IsCancellationToken(method.Parameters[method.Parameters.Length - 1].Type)
            || method.Parameters[method.Parameters.Length - 1].IsOptional)
        {
            ReportUseCaseShape(context, type, "ExecuteAsync must end with a non-optional CancellationToken");
            return;
        }

        var inputParameters = method.Parameters.Take(method.Parameters.Length - 1).ToArray();
        if (inputParameters.Length > 1)
        {
            ReportUseCaseShape(context, type, "multiple input values require one dedicated Input object");
            return;
        }

        if (inputParameters.Any(parameter => IsTransportContract(parameter.Type)))
        {
            ReportUseCaseShape(context, type, "transport, Command, Query, Request, Message, or Contract input is forbidden");
            return;
        }

        if (inputParameters.Length == 1
            && !IsStandardScalar(inputParameters[0].Type)
            && !inputParameters[0].Type.Name.EndsWith("Input", System.StringComparison.Ordinal))
        {
            ReportUseCaseShape(context, type, "a non-scalar input type must use the Input suffix");
        }
    }

    private static void AnalyzeDispatchHandler(SymbolAnalysisContext context, INamedTypeSymbol type)
    {
        var dependencies = type.InstanceConstructors
            .SelectMany(constructor => constructor.Parameters)
            .Concat(type.GetMembers().OfType<IMethodSymbol>().SelectMany(method => method.Parameters))
            .Select(parameter => parameter.Type)
            .ToArray();
        var useCaseDependencies = dependencies
            .Where(IsUseCaseType)
            .Select(dependency => dependency.ToDisplayString())
            .Distinct()
            .Count();

        if (useCaseDependencies != 1)
        {
            context.ReportDiagnostic(Diagnostic.Create(
                RuleDescriptors.DispatchHandlerBoundary,
                type.Locations[0],
                type.Name,
                "depend on exactly one Use Case"));
        }

        if (dependencies.Any(IsForbiddenHandlerDependency))
        {
            context.ReportDiagnostic(Diagnostic.Create(
                RuleDescriptors.DispatchHandlerBoundary,
                type.Locations[0],
                type.Name,
                "must not depend on repositories or Domain services"));
        }
    }

    private static void ReportUseCaseShape(
        SymbolAnalysisContext context,
        INamedTypeSymbol type,
        string detail)
    {
        context.ReportDiagnostic(Diagnostic.Create(
            RuleDescriptors.UseCaseContractShape,
            type.Locations[0],
            type.Name,
            detail));
    }

    private static void AnalyzeObjectCreation(SyntaxNodeAnalysisContext context)
    {
        var creation = (Microsoft.CodeAnalysis.CSharp.Syntax.ObjectCreationExpressionSyntax)context.Node;
        var containingType = context.ContainingSymbol?.ContainingType;
        if (containingType is null || !LooksLikeUseCaseOrHandler(containingType))
        {
            return;
        }

        var createdType = context.SemanticModel.GetTypeInfo(creation, context.CancellationToken).Type;
        if (createdType is null || !createdType.Name.EndsWith("Repository", System.StringComparison.Ordinal))
        {
            return;
        }

        context.ReportDiagnostic(Diagnostic.Create(
            RuleDescriptors.UseCaseDirectRepositoryConstruction,
            creation.Type.GetLocation(),
            containingType.Name,
            createdType.Name));
    }

    private static void ReportForbiddenMemberType(
        SymbolAnalysisContext context,
        INamedTypeSymbol containingType,
        ITypeSymbol memberType,
        ImmutableArray<Location> locations,
        string memberName)
    {
        var location = locations.Length > 0 ? locations[0] : containingType.Locations[0];
        if (memberType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat) == "global::System.IServiceProvider")
        {
            context.ReportDiagnostic(Diagnostic.Create(
                RuleDescriptors.UseCaseServiceProviderInjection,
                location,
                containingType.Name));
        }
        else if (memberType.Name.EndsWith("ServiceLocator", System.StringComparison.Ordinal))
        {
            context.ReportDiagnostic(Diagnostic.Create(
                RuleDescriptors.UseCaseDependencyResolution,
                location,
                containingType.Name,
                memberName));
        }
    }

    private static void ReportInjectionAttributes(
        SymbolAnalysisContext context,
        INamedTypeSymbol containingType,
        IPropertySymbol property)
    {
        foreach (var attribute in property.GetAttributes())
        {
            var attributeName = attribute.AttributeClass?.Name;
            if (attributeName is not "Inject" and not "InjectAttribute"
                and not "FromServices" and not "FromServicesAttribute")
            {
                continue;
            }

            context.ReportDiagnostic(Diagnostic.Create(
                RuleDescriptors.UseCaseDependencyResolution,
                property.Locations[0],
                containingType.Name,
                attributeName));
        }
    }

    private static bool ImplementsMarker(ITypeSymbol type, string markerPrefix)
    {
        if (type.TypeKind == TypeKind.Interface && type.Name == markerPrefix)
        {
            return true;
        }

        foreach (var contract in type.AllInterfaces)
        {
            if (contract.Name == markerPrefix)
            {
                return true;
            }
        }

        return false;
    }

    private static bool IsTask(ITypeSymbol type)
    {
        return type.Name == "Task"
            && type.ContainingNamespace?.ToDisplayString() == "System.Threading.Tasks";
    }

    private static bool IsCancellationToken(ITypeSymbol type)
    {
        return type.Name == "CancellationToken"
            && type.ContainingNamespace?.ToDisplayString() == "System.Threading";
    }

    private static bool IsStandardScalar(ITypeSymbol type)
    {
        return type.SpecialType is SpecialType.System_Boolean
            or SpecialType.System_Byte
            or SpecialType.System_SByte
            or SpecialType.System_Int16
            or SpecialType.System_UInt16
            or SpecialType.System_Int32
            or SpecialType.System_UInt32
            or SpecialType.System_Int64
            or SpecialType.System_UInt64
            or SpecialType.System_Single
            or SpecialType.System_Double
            or SpecialType.System_Decimal
            or SpecialType.System_Char
            or SpecialType.System_String
            || type.Name is "Guid" or "DateTime" or "DateTimeOffset" or "DateOnly" or "TimeOnly";
    }

    private static bool IsTransportContract(ITypeSymbol type)
    {
        var name = type.Name;
        return name.EndsWith("Request", System.StringComparison.Ordinal)
            || name.EndsWith("Command", System.StringComparison.Ordinal)
            || name.EndsWith("Query", System.StringComparison.Ordinal)
            || name.EndsWith("Message", System.StringComparison.Ordinal)
            || name.EndsWith("Contract", System.StringComparison.Ordinal)
            || type.AllInterfaces.Any(contract => contract.Name is "ICommand" or "IQuery");
    }

    private static bool IsForbiddenUseCaseDependency(ITypeSymbol type)
    {
        var name = type.Name;
        var namespaceName = type.ContainingNamespace?.ToDisplayString() ?? string.Empty;
        return name is "IMessageBus" or "IMediator" or "IDispatcher"
            || name.EndsWith("Dispatcher", System.StringComparison.Ordinal)
            || IsUseCaseType(type)
            || namespaceName.StartsWith("Wolverine", System.StringComparison.Ordinal)
            || namespaceName.StartsWith("MediatR", System.StringComparison.Ordinal)
            || namespaceName.StartsWith("Microsoft.AspNetCore", System.StringComparison.Ordinal);
    }

    private static bool IsTransportOutput(ITypeSymbol type)
    {
        var name = type.Name;
        var namespaceName = type.ContainingNamespace?.ToDisplayString() ?? string.Empty;
        return name is "IActionResult" or "IResult"
            || name.EndsWith("Acknowledgement", System.StringComparison.Ordinal)
            || name.EndsWith("Envelope", System.StringComparison.Ordinal)
            || namespaceName.StartsWith("Microsoft.AspNetCore", System.StringComparison.Ordinal)
            || namespaceName.StartsWith("Wolverine", System.StringComparison.Ordinal);
    }

    private static bool IsUseCaseType(ITypeSymbol type)
    {
        return type.Name.EndsWith("UseCase", System.StringComparison.Ordinal);
    }

    private static bool IsDispatchHandler(INamedTypeSymbol type)
    {
        return type.Name.EndsWith("CommandHandler", System.StringComparison.Ordinal)
            || type.Name.EndsWith("QueryHandler", System.StringComparison.Ordinal);
    }

    private static bool IsForbiddenHandlerDependency(ITypeSymbol type)
    {
        return type.Name.EndsWith("Repository", System.StringComparison.Ordinal)
            || type.Name.EndsWith("DomainService", System.StringComparison.Ordinal);
    }

    private static bool LooksLikeUseCaseOrHandler(INamedTypeSymbol type)
    {
        var name = type.Name;
        if (name.EndsWith("UseCase", System.StringComparison.Ordinal) || name.EndsWith("Handler", System.StringComparison.Ordinal))
        {
            return true;
        }
        return false;
    }
}
