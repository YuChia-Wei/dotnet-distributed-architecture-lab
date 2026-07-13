using System;
using System.Collections.Immutable;
using System.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.Diagnostics;

namespace DotnetBackendAnalyzers;

[DiagnosticAnalyzer(LanguageNames.CSharp)]
public sealed class RepositoryQueryMethodAnalyzer : DiagnosticAnalyzer
{
    private static readonly ImmutableHashSet<string> AllowedAggregateMethods =
        ImmutableHashSet.Create(StringComparer.Ordinal, "FindByIdAsync", "SaveAsync");

    private static readonly ImmutableHashSet<string> ForbiddenGenericWriteRepositories =
        ImmutableHashSet.Create(
            StringComparer.Ordinal,
            "IRepository",
            "IGenericRepository",
            "IWritableRepository",
            "ICrudRepository");

    private static readonly string[] WriteMethodPrefixes =
    {
        "Save",
        "Add",
        "Create",
        "Insert",
        "Update",
        "Delete",
        "Remove",
        "Upsert",
        "Persist",
        "Purge"
    };

    public override ImmutableArray<DiagnosticDescriptor> SupportedDiagnostics =>
        ImmutableArray.Create(RuleDescriptors.RepositoryQueryMethod);

    public override void Initialize(AnalysisContext context)
    {
        context.ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None);
        context.EnableConcurrentExecution();
        context.RegisterSymbolAction(AnalyzeNamedType, SymbolKind.NamedType);
    }

    private static void AnalyzeNamedType(SymbolAnalysisContext context)
    {
        var type = (INamedTypeSymbol)context.Symbol;
        if (type.TypeKind != TypeKind.Interface)
        {
            return;
        }

        if (IsForbiddenGenericWriteRepository(type))
        {
            Report(context, type, $"public generic writable repository '{type.Name}' is prohibited");
            return;
        }

        var aggregateContracts = GetAggregateContracts(type);
        if (!aggregateContracts.IsEmpty)
        {
            AnalyzeAggregateRepository(context, type, aggregateContracts);
        }

        if (IsOrImplements(type, "IQueryRepository", 0))
        {
            AnalyzeQueryRepository(context, type);
        }
    }

    private static void AnalyzeAggregateRepository(
        SymbolAnalysisContext context,
        INamedTypeSymbol type,
        ImmutableArray<INamedTypeSymbol> aggregateContracts)
    {
        if (IsContract(type, "IDomainRepository", 2)
            && !type.AllInterfaces.Any(candidate => IsContract(candidate, "IAggregateRepository", 2)))
        {
            Report(
                context,
                type,
                "IDomainRepository is a compatibility contract and must inherit IAggregateRepository");
        }

        var invalidAggregate = aggregateContracts
            .Select(contract => contract.TypeArguments[0])
            .FirstOrDefault(candidate => !IsAggregateRoot(candidate));

        if (invalidAggregate is not null)
        {
            Report(
                context,
                type,
                $"aggregate repository type '{invalidAggregate.ToDisplayString()}' is not an Aggregate Root");
        }

        foreach (var method in type.GetMembers().OfType<IMethodSymbol>())
        {
            if (method.MethodKind != MethodKind.Ordinary)
            {
                continue;
            }

            if (!AllowedAggregateMethods.Contains(method.Name))
            {
                Report(
                    context,
                    method,
                    $"aggregate repository member '{method.Name}' is outside the FindByIdAsync/SaveAsync contract");
                continue;
            }

            var contract = aggregateContracts.First();
            if (!HasApprovedAggregateMethodSignature(
                    method,
                    contract.TypeArguments[0],
                    contract.TypeArguments[1]))
            {
                Report(
                    context,
                    method,
                    $"aggregate repository member '{method.Name}' does not match the approved asynchronous signature");
            }
        }
    }

    private static void AnalyzeQueryRepository(
        SymbolAnalysisContext context,
        INamedTypeSymbol type)
    {
        foreach (var method in type.GetMembers().OfType<IMethodSymbol>())
        {
            if (method.MethodKind != MethodKind.Ordinary)
            {
                continue;
            }

            if (LooksLikeWriteMethod(method.Name))
            {
                Report(
                    context,
                    method,
                    $"query repository member '{method.Name}' exposes a persistence write");
                continue;
            }

            if (ContainsMutableDomainType(method.ReturnType))
            {
                Report(
                    context,
                    method,
                    $"query repository member '{method.Name}' returns an Aggregate Root or Domain Entity");
            }
        }
    }

    private static ImmutableArray<INamedTypeSymbol> GetAggregateContracts(INamedTypeSymbol type)
    {
        var builder = ImmutableArray.CreateBuilder<INamedTypeSymbol>();

        if (IsAggregateContract(type))
        {
            builder.Add(type);
        }

        foreach (var candidate in type.AllInterfaces)
        {
            if (IsAggregateContract(candidate))
            {
                builder.Add(candidate);
            }
        }

        return builder.ToImmutable();
    }

    private static bool IsAggregateContract(INamedTypeSymbol type) =>
        IsContract(type, "IAggregateRepository", 2)
        || IsContract(type, "IDomainRepository", 2);

    private static bool IsOrImplements(INamedTypeSymbol type, string name, int arity) =>
        IsContract(type, name, arity)
        || type.AllInterfaces.Any(candidate => IsContract(candidate, name, arity));

    private static bool IsContract(INamedTypeSymbol type, string name, int arity) =>
        type.OriginalDefinition.Name == name
        && type.OriginalDefinition.Arity == arity;

    private static bool IsForbiddenGenericWriteRepository(INamedTypeSymbol type) =>
        type.Arity > 0
        && ForbiddenGenericWriteRepositories.Contains(type.OriginalDefinition.Name);

    private static bool HasApprovedAggregateMethodSignature(
        IMethodSymbol method,
        ITypeSymbol aggregateType,
        ITypeSymbol idType)
    {
        if (method.Parameters.Length < 1 || method.Parameters.Length > 2)
        {
            return false;
        }

        if (method.Parameters.Length == 2
            && !IsCancellationToken(method.Parameters[1].Type))
        {
            return false;
        }

        if (method.Name == "FindByIdAsync")
        {
            return SymbolEqualityComparer.Default.Equals(method.Parameters[0].Type, idType)
                && IsTaskOf(method.ReturnType, aggregateType);
        }

        return method.Name == "SaveAsync"
            && SymbolEqualityComparer.Default.Equals(method.Parameters[0].Type, aggregateType)
            && IsTask(method.ReturnType);
    }

    private static bool IsTaskOf(ITypeSymbol type, ITypeSymbol resultType) =>
        type is INamedTypeSymbol namedType
        && namedType.Name == "Task"
        && namedType.ContainingNamespace.ToDisplayString() == "System.Threading.Tasks"
        && namedType.TypeArguments.Length == 1
        && SymbolEqualityComparer.Default.Equals(namedType.TypeArguments[0], resultType);

    private static bool IsTask(ITypeSymbol type) =>
        type is INamedTypeSymbol namedType
        && namedType.Name == "Task"
        && namedType.ContainingNamespace.ToDisplayString() == "System.Threading.Tasks"
        && namedType.TypeArguments.Length == 0;

    private static bool IsCancellationToken(ITypeSymbol type) =>
        type.Name == "CancellationToken"
        && type.ContainingNamespace.ToDisplayString() == "System.Threading";

    private static bool IsAggregateRoot(ITypeSymbol type)
    {
        if (type is ITypeParameterSymbol typeParameter)
        {
            return typeParameter.ConstraintTypes.Any(IsAggregateRoot);
        }

        if (type is not INamedTypeSymbol namedType)
        {
            return false;
        }

        for (var current = namedType; current is not null; current = current.BaseType)
        {
            if (current.Name == "AggregateRoot" || current.Name == "EsAggregateRoot")
            {
                return true;
            }
        }

        return namedType.Name == "IAggregateRoot"
            || namedType.AllInterfaces.Any(candidate => candidate.Name == "IAggregateRoot");
    }

    private static bool ContainsMutableDomainType(ITypeSymbol type)
    {
        if (IsAggregateRoot(type) || IsDomainEntity(type))
        {
            return true;
        }

        return type is INamedTypeSymbol namedType
            && namedType.TypeArguments.Any(ContainsMutableDomainType);
    }

    private static bool IsDomainEntity(ITypeSymbol type)
    {
        if (type is ITypeParameterSymbol typeParameter)
        {
            return typeParameter.ConstraintTypes.Any(IsDomainEntity);
        }

        if (type is not INamedTypeSymbol namedType)
        {
            return false;
        }

        for (var current = namedType; current is not null; current = current.BaseType)
        {
            if (current.Name == "DomainEntity")
            {
                return true;
            }
        }

        return namedType.Name == "IDomainEntity"
            || namedType.AllInterfaces.Any(candidate => candidate.Name == "IDomainEntity");
    }

    private static bool LooksLikeWriteMethod(string methodName) =>
        WriteMethodPrefixes.Any(prefix =>
            methodName.StartsWith(prefix, StringComparison.Ordinal));

    private static void Report(
        SymbolAnalysisContext context,
        ISymbol symbol,
        string reason)
    {
        var location = symbol.Locations.FirstOrDefault(candidate => candidate.IsInSource);
        if (location is null)
        {
            return;
        }

        context.ReportDiagnostic(Diagnostic.Create(
            RuleDescriptors.RepositoryQueryMethod,
            location,
            reason));
    }
}
