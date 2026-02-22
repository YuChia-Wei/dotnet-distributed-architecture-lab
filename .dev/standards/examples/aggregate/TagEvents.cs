using System;
using System.Collections.Generic;
using Example.Plans.Domain;

namespace Example.Tags.Domain;

public static class TagEvents
{
    public interface IInternalDomainEvent
    {
        Guid Id { get; }
        DateTimeOffset OccurredOn { get; }
        IReadOnlyDictionary<string, string> Metadata { get; }
        string Source { get; }
    }

    public interface IConstructionEvent { }
    public interface IDestructionEvent { }

    public interface ITagEvent : IInternalDomainEvent
    {
        TagId TagId { get; }
    }

    public abstract record TagEvent(
        TagId TagId,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : ITagEvent
    {
        public string Source => TagId.Value;
    }

    public sealed record TagCreated(
        TagId TagId,
        PlanId PlanId,
        string Name,
        string Color,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : TagEvent(TagId, Metadata, Id, OccurredOn), IConstructionEvent
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record TagRenamed(
        TagId TagId,
        string NewName,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : TagEvent(TagId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record TagColorChanged(
        TagId TagId,
        string NewColor,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : TagEvent(TagId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record TagDeleted(
        TagId TagId,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : TagEvent(TagId, Metadata, Id, OccurredOn), IDestructionEvent
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public static class TypeMapper
    {
        public const string MappingTypePrefix = "TagEvents.";
        public const string TagCreatedType = MappingTypePrefix + "TagCreated";
        public const string TagRenamedType = MappingTypePrefix + "TagRenamed";
        public const string TagColorChangedType = MappingTypePrefix + "TagColorChanged";
        public const string TagDeletedType = MappingTypePrefix + "TagDeleted";

        public static readonly IReadOnlyDictionary<string, Type> Map =
            new Dictionary<string, Type>
            {
                [TagCreatedType] = typeof(TagCreated),
                [TagRenamedType] = typeof(TagRenamed),
                [TagColorChangedType] = typeof(TagColorChanged),
                [TagDeletedType] = typeof(TagDeleted)
            };
    }
}
