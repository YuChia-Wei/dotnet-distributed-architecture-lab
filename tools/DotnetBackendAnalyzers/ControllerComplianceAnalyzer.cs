using System;
using System.Collections.Immutable;
using System.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Diagnostics;

namespace DotnetBackendAnalyzers;

[DiagnosticAnalyzer(LanguageNames.CSharp)]
public sealed class ControllerComplianceAnalyzer : DiagnosticAnalyzer
{
    private static readonly ImmutableHashSet<string> PersistenceMethods =
        ImmutableHashSet.Create(StringComparer.Ordinal, "SaveChanges", "SaveChangesAsync");

    public override ImmutableArray<DiagnosticDescriptor> SupportedDiagnostics =>
        ImmutableArray.Create(
            RuleDescriptors.ControllerApiAttribute,
            RuleDescriptors.ControllerPersistenceAccess,
            RuleDescriptors.ControllerDirectConstruction,
            RuleDescriptors.ControllerForbiddenDependency);

    public override void Initialize(AnalysisContext context)
    {
        context.ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None);
        context.EnableConcurrentExecution();
        context.RegisterSyntaxNodeAction(AnalyzeController, SyntaxKind.ClassDeclaration);
    }

    private static void AnalyzeController(SyntaxNodeAnalysisContext context)
    {
        var declaration = (ClassDeclarationSyntax)context.Node;
        if (!declaration.Identifier.ValueText.EndsWith("Controller", StringComparison.Ordinal))
        {
            return;
        }

        var controllerSymbol = context.SemanticModel.GetDeclaredSymbol(declaration, context.CancellationToken);
        if (controllerSymbol is null || controllerSymbol.IsAbstract)
        {
            return;
        }

        AnalyzeApiControllerAttribute(context, declaration, controllerSymbol);
        AnalyzePersistenceAccess(context, declaration);
        AnalyzeDirectConstruction(context, declaration);
        AnalyzeInjectedDependencies(context, controllerSymbol);
    }

    private static void AnalyzeInjectedDependencies(
        SyntaxNodeAnalysisContext context,
        INamedTypeSymbol controllerSymbol)
    {
        foreach (var constructor in controllerSymbol.InstanceConstructors)
        {
            foreach (var parameter in constructor.Parameters)
            {
                if (!IsForbiddenControllerDependency(parameter.Type))
                {
                    continue;
                }

                var location = parameter.Locations.FirstOrDefault() ?? controllerSymbol.Locations[0];
                context.ReportDiagnostic(Diagnostic.Create(
                    RuleDescriptors.ControllerForbiddenDependency,
                    location,
                    controllerSymbol.Name,
                    parameter.Type.Name));
            }
        }
    }

    private static bool IsForbiddenControllerDependency(ITypeSymbol type)
    {
        var name = type.Name;
        if (name.EndsWith("Handler", StringComparison.Ordinal)
            || name is "IMessageBus" or "IMediator" or "IDispatcher"
            || name.EndsWith("Dispatcher", StringComparison.Ordinal)
            || name.EndsWith("DomainService", StringComparison.Ordinal))
        {
            return true;
        }

        if (!name.EndsWith("Repository", StringComparison.Ordinal))
        {
            return false;
        }

        return !name.EndsWith("QueryRepository", StringComparison.Ordinal)
            && !type.AllInterfaces.Any(contract => contract.Name == "IQueryRepository");
    }

    private static void AnalyzeApiControllerAttribute(
        SyntaxNodeAnalysisContext context,
        ClassDeclarationSyntax declaration,
        INamedTypeSymbol controllerSymbol)
    {
        var hasApiControllerAttribute = controllerSymbol
            .GetAttributes()
            .Any(attribute =>
                attribute.AttributeClass?.Name is "ApiControllerAttribute" or "ApiController");

        if (hasApiControllerAttribute)
        {
            return;
        }

        context.ReportDiagnostic(Diagnostic.Create(
            RuleDescriptors.ControllerApiAttribute,
            declaration.Identifier.GetLocation(),
            controllerSymbol.Name));
    }

    private static void AnalyzePersistenceAccess(
        SyntaxNodeAnalysisContext context,
        ClassDeclarationSyntax declaration)
    {
        foreach (var typeSyntax in declaration.DescendantNodes().OfType<TypeSyntax>())
        {
            var type = context.SemanticModel.GetTypeInfo(typeSyntax, context.CancellationToken).Type;
            if (!IsDbContext(type))
            {
                continue;
            }

            context.ReportDiagnostic(Diagnostic.Create(
                RuleDescriptors.ControllerPersistenceAccess,
                typeSyntax.GetLocation(),
                declaration.Identifier.ValueText,
                type?.Name ?? typeSyntax.ToString()));
        }

        foreach (var invocation in declaration.DescendantNodes().OfType<InvocationExpressionSyntax>())
        {
            var method = context.SemanticModel.GetSymbolInfo(invocation, context.CancellationToken).Symbol as IMethodSymbol;
            var methodName = method?.Name ?? GetInvokedMethodName(invocation);
            if (methodName is null || !PersistenceMethods.Contains(methodName))
            {
                continue;
            }

            context.ReportDiagnostic(Diagnostic.Create(
                RuleDescriptors.ControllerPersistenceAccess,
                invocation.GetLocation(),
                declaration.Identifier.ValueText,
                methodName));
        }
    }

    private static void AnalyzeDirectConstruction(
        SyntaxNodeAnalysisContext context,
        ClassDeclarationSyntax declaration)
    {
        foreach (var creation in declaration.DescendantNodes().OfType<ObjectCreationExpressionSyntax>())
        {
            var type = context.SemanticModel.GetTypeInfo(creation, context.CancellationToken).Type;
            var typeName = type?.Name ?? creation.Type.ToString();
            if (!typeName.EndsWith("Handler", StringComparison.Ordinal)
                && !typeName.EndsWith("UseCase", StringComparison.Ordinal))
            {
                continue;
            }

            context.ReportDiagnostic(Diagnostic.Create(
                RuleDescriptors.ControllerDirectConstruction,
                creation.Type.GetLocation(),
                declaration.Identifier.ValueText,
                typeName));
        }
    }

    private static bool IsDbContext(ITypeSymbol? type)
    {
        for (var current = type as INamedTypeSymbol; current is not null; current = current.BaseType)
        {
            if (current.Name == "DbContext")
            {
                return true;
            }
        }

        return false;
    }

    private static string? GetInvokedMethodName(InvocationExpressionSyntax invocation)
    {
        return invocation.Expression switch
        {
            IdentifierNameSyntax identifier => identifier.Identifier.ValueText,
            MemberAccessExpressionSyntax memberAccess => memberAccess.Name.Identifier.ValueText,
            _ => null
        };
    }
}
