using System;
using System.Collections.Immutable;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Diagnostics;

namespace DotnetBackendAnalyzers;

[DiagnosticAnalyzer(LanguageNames.CSharp)]
public sealed class EventSourcedAggregateMutationAnalyzer : DiagnosticAnalyzer
{
    private static readonly ImmutableArray<SyntaxKind> AssignmentKinds =
        ImmutableArray.Create(
            SyntaxKind.SimpleAssignmentExpression,
            SyntaxKind.AddAssignmentExpression,
            SyntaxKind.SubtractAssignmentExpression,
            SyntaxKind.MultiplyAssignmentExpression,
            SyntaxKind.DivideAssignmentExpression,
            SyntaxKind.ModuloAssignmentExpression,
            SyntaxKind.AndAssignmentExpression,
            SyntaxKind.ExclusiveOrAssignmentExpression,
            SyntaxKind.OrAssignmentExpression,
            SyntaxKind.LeftShiftAssignmentExpression,
            SyntaxKind.RightShiftAssignmentExpression,
            SyntaxKind.CoalesceAssignmentExpression);

    public override ImmutableArray<DiagnosticDescriptor> SupportedDiagnostics =>
        ImmutableArray.Create(RuleDescriptors.EventSourcedAggregateDirectMutation);

    public override void Initialize(AnalysisContext context)
    {
        context.ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None);
        context.EnableConcurrentExecution();
        context.RegisterSyntaxNodeAction(AnalyzeAssignment, AssignmentKinds);
        context.RegisterSyntaxNodeAction(
            AnalyzeIncrementOrDecrement,
            SyntaxKind.PreIncrementExpression,
            SyntaxKind.PreDecrementExpression,
            SyntaxKind.PostIncrementExpression,
            SyntaxKind.PostDecrementExpression);
    }

    private static void AnalyzeAssignment(SyntaxNodeAnalysisContext context)
    {
        var assignment = (AssignmentExpressionSyntax)context.Node;
        AnalyzeMutation(context, assignment.Left);
    }

    private static void AnalyzeIncrementOrDecrement(SyntaxNodeAnalysisContext context)
    {
        var expression = (ExpressionSyntax)context.Node;
        var operand = expression switch
        {
            PrefixUnaryExpressionSyntax prefix => prefix.Operand,
            PostfixUnaryExpressionSyntax postfix => postfix.Operand,
            _ => null
        };

        if (operand is not null)
        {
            AnalyzeMutation(context, operand);
        }
    }

    private static void AnalyzeMutation(SyntaxNodeAnalysisContext context, ExpressionSyntax target)
    {
        var method = target.FirstAncestorOrSelf<MethodDeclarationSyntax>();
        if (method is null || method.Identifier.ValueText == "When")
        {
            return;
        }

        var classDeclaration = target.FirstAncestorOrSelf<ClassDeclarationSyntax>();
        var aggregateSymbol = classDeclaration is null
            ? null
            : context.SemanticModel.GetDeclaredSymbol(classDeclaration, context.CancellationToken);
        if (aggregateSymbol is null || !InheritsFromEsAggregateRoot(aggregateSymbol))
        {
            return;
        }

        var member = context.SemanticModel.GetSymbolInfo(target, context.CancellationToken).Symbol;
        if (member is not IFieldSymbol and not IPropertySymbol
            || member.ContainingType is null
            || !IsAggregateMember(aggregateSymbol, member.ContainingType))
        {
            return;
        }

        context.ReportDiagnostic(Diagnostic.Create(
            RuleDescriptors.EventSourcedAggregateDirectMutation,
            target.GetLocation(),
            aggregateSymbol.Name,
            member.Name));
    }

    private static bool InheritsFromEsAggregateRoot(INamedTypeSymbol symbol)
    {
        for (var current = symbol.BaseType; current is not null; current = current.BaseType)
        {
            if (current.Name == "EsAggregateRoot")
            {
                return true;
            }
        }

        return false;
    }

    private static bool IsAggregateMember(INamedTypeSymbol aggregate, INamedTypeSymbol declaringType)
    {
        for (var current = aggregate; current is not null; current = current.BaseType)
        {
            if (SymbolEqualityComparer.Default.Equals(current, declaringType))
            {
                return true;
            }
        }

        return false;
    }
}
