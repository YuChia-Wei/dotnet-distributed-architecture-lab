using System.Collections.Immutable;
using System.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Diagnostics;

namespace DotnetBackendAnalyzers;

[DiagnosticAnalyzer(LanguageNames.CSharp)]
public sealed class AggregateInfrastructureDependencyAnalyzer : DiagnosticAnalyzer
{
    private static readonly string[] ForbiddenTypeSuffixes = { ".DbContext", "DbContext" };

    public override ImmutableArray<DiagnosticDescriptor> SupportedDiagnostics =>
        ImmutableArray.Create(RuleDescriptors.AggregateInfrastructureDependency);

    public override void Initialize(AnalysisContext context)
    {
        context.ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None);
        context.EnableConcurrentExecution();
        context.RegisterSyntaxNodeAction(AnalyzeClass, SyntaxKind.ClassDeclaration);
    }

    private static void AnalyzeClass(SyntaxNodeAnalysisContext context)
    {
        var classDeclaration = (ClassDeclarationSyntax)context.Node;
        var classSymbol = context.SemanticModel.GetDeclaredSymbol(classDeclaration, context.CancellationToken);

        if (classSymbol is null || !LooksLikeAggregateOrEntity(classSymbol))
        {
            return;
        }

        foreach (var typeSyntax in classDeclaration.DescendantNodes().OfType<TypeSyntax>())
        {
            var type = context.SemanticModel.GetTypeInfo(typeSyntax, context.CancellationToken).Type;
            if (type is null || !IsForbiddenInfrastructureType(type))
            {
                continue;
            }

            context.ReportDiagnostic(Diagnostic.Create(
                RuleDescriptors.AggregateInfrastructureDependency,
                typeSyntax.GetLocation(),
                classSymbol.Name,
                type.Name));
        }
    }

    private static bool LooksLikeAggregateOrEntity(INamedTypeSymbol symbol)
    {
        if (symbol.Name.EndsWith("Aggregate", System.StringComparison.Ordinal)
            || symbol.Name.EndsWith("AggregateRoot", System.StringComparison.Ordinal)
            || symbol.Name.EndsWith("Entity", System.StringComparison.Ordinal))
        {
            return true;
        }

        for (var current = symbol.BaseType; current is not null; current = current.BaseType)
        {
            var name = current.Name;
            if (name == "AggregateRoot" || name == "Entity" || name.EndsWith("AggregateRoot", System.StringComparison.Ordinal))
            {
                return true;
            }
        }

        return false;
    }

    private static bool IsForbiddenInfrastructureType(ITypeSymbol type)
    {
        var fullName = type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat);
        foreach (var suffix in ForbiddenTypeSuffixes)
        {
            if (fullName.EndsWith(suffix, System.StringComparison.Ordinal))
            {
                return true;
            }
        }

        return false;
    }
}
