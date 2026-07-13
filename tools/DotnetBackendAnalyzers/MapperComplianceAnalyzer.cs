using System;
using System.Collections.Immutable;
using System.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Diagnostics;

namespace DotnetBackendAnalyzers;

[DiagnosticAnalyzer(LanguageNames.CSharp)]
public sealed class MapperComplianceAnalyzer : DiagnosticAnalyzer
{
    private static readonly string[] ForbiddenTypeSuffixes =
    {
        "Repository",
        "UseCase",
        "Handler"
    };

    public override ImmutableArray<DiagnosticDescriptor> SupportedDiagnostics =>
        ImmutableArray.Create(
            RuleDescriptors.MapperMustBeStatic,
            RuleDescriptors.MapperForbiddenDependency);

    public override void Initialize(AnalysisContext context)
    {
        context.ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None);
        context.EnableConcurrentExecution();
        context.RegisterSyntaxNodeAction(AnalyzeMapper, SyntaxKind.ClassDeclaration);
    }

    private static void AnalyzeMapper(SyntaxNodeAnalysisContext context)
    {
        var declaration = (ClassDeclarationSyntax)context.Node;
        var mapperSymbol = context.SemanticModel.GetDeclaredSymbol(declaration, context.CancellationToken);
        if (mapperSymbol is null || !mapperSymbol.Name.EndsWith("Mapper", StringComparison.Ordinal))
        {
            return;
        }

        if (!mapperSymbol.IsStatic)
        {
            context.ReportDiagnostic(Diagnostic.Create(
                RuleDescriptors.MapperMustBeStatic,
                declaration.Identifier.GetLocation(),
                mapperSymbol.Name));
        }

        foreach (var typeSyntax in declaration.DescendantNodes().OfType<TypeSyntax>())
        {
            var type = context.SemanticModel.GetTypeInfo(typeSyntax, context.CancellationToken).Type;
            if (type is null || !IsForbiddenDependency(type))
            {
                continue;
            }

            context.ReportDiagnostic(Diagnostic.Create(
                RuleDescriptors.MapperForbiddenDependency,
                typeSyntax.GetLocation(),
                mapperSymbol.Name,
                type.Name));
        }
    }

    private static bool IsForbiddenDependency(ITypeSymbol type)
    {
        var candidate = type is INamedTypeSymbol { IsGenericType: true } namedType
            ? namedType.ConstructedFrom.Name
            : type.Name;

        foreach (var suffix in ForbiddenTypeSuffixes)
        {
            if (candidate.EndsWith(suffix, StringComparison.Ordinal))
            {
                return true;
            }
        }

        return false;
    }
}
