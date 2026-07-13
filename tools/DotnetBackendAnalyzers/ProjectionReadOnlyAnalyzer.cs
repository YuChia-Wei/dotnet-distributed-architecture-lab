using System;
using System.Collections.Immutable;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Diagnostics;

namespace DotnetBackendAnalyzers;

[DiagnosticAnalyzer(LanguageNames.CSharp)]
public sealed class ProjectionReadOnlyAnalyzer : DiagnosticAnalyzer
{
    private static readonly ImmutableHashSet<string> WriteMethods =
        ImmutableHashSet.Create(StringComparer.Ordinal, "Add", "AddAsync", "Update", "Remove");

    public override ImmutableArray<DiagnosticDescriptor> SupportedDiagnostics =>
        ImmutableArray.Create(RuleDescriptors.ProjectionWriteOperation);

    public override void Initialize(AnalysisContext context)
    {
        context.ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None);
        context.EnableConcurrentExecution();
        context.RegisterSyntaxNodeAction(AnalyzeInvocation, SyntaxKind.InvocationExpression);
    }

    private static void AnalyzeInvocation(SyntaxNodeAnalysisContext context)
    {
        var invocation = (InvocationExpressionSyntax)context.Node;
        var projectionType = context.ContainingSymbol?.ContainingType;
        if (projectionType is null || !ImplementsProjectionMarker(projectionType))
        {
            return;
        }

        var method = context.SemanticModel.GetSymbolInfo(invocation, context.CancellationToken).Symbol as IMethodSymbol;
        if (method is null || !IsPersistenceWrite(method))
        {
            return;
        }

        context.ReportDiagnostic(Diagnostic.Create(
            RuleDescriptors.ProjectionWriteOperation,
            invocation.GetLocation(),
            projectionType.Name,
            method.Name));
    }

    private static bool ImplementsProjectionMarker(INamedTypeSymbol type)
    {
        foreach (var contract in type.AllInterfaces)
        {
            if (contract.Name == "IProjection")
            {
                return true;
            }
        }

        return false;
    }

    private static bool IsPersistenceWrite(IMethodSymbol method)
    {
        if (method.Name is "SaveChanges" or "SaveChangesAsync")
        {
            return InheritsFrom(method.ContainingType, "DbContext");
        }

        return WriteMethods.Contains(method.Name)
            && (InheritsFrom(method.ContainingType, "DbContext")
                || InheritsFrom(method.ContainingType, "DbSet"));
    }

    private static bool InheritsFrom(INamedTypeSymbol? type, string typeName)
    {
        for (var current = type; current is not null; current = current.BaseType)
        {
            if (current.Name == typeName)
            {
                return true;
            }
        }

        return false;
    }
}
