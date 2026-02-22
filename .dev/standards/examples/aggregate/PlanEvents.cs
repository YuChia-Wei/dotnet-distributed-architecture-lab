using System;
using System.Collections.Generic;
using Example.Tags.Domain;

namespace Example.Plans.Domain;

public static class PlanEvents
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

    public interface IPlanEvent : IInternalDomainEvent
    {
        PlanId PlanId { get; }
    }

    public abstract record PlanEvent(
        PlanId PlanId,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : IPlanEvent
    {
        public string Source => PlanId.Value;
    }

    public sealed record PlanCreated(
        PlanId PlanId,
        string Name,
        string UserId,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn), IConstructionEvent
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record PlanRenamed(
        PlanId PlanId,
        string NewName,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record PlanDeleted(
        PlanId PlanId,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn), IDestructionEvent
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record ProjectCreated(
        PlanId PlanId,
        ProjectId ProjectId,
        ProjectName ProjectName,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record ProjectDeleted(
        PlanId PlanId,
        ProjectId ProjectId,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record TaskCreated(
        PlanId PlanId,
        ProjectId ProjectId,
        ProjectName ProjectName,
        TaskId TaskId,
        string TaskName,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record TaskChecked(
        PlanId PlanId,
        ProjectId ProjectId,
        TaskId TaskId,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record TaskUnchecked(
        PlanId PlanId,
        ProjectId ProjectId,
        TaskId TaskId,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record TaskDeleted(
        PlanId PlanId,
        ProjectId ProjectId,
        TaskId TaskId,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record TaskDeadlineSet(
        PlanId PlanId,
        ProjectId ProjectId,
        TaskId TaskId,
        string? Deadline,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record TaskRenamed(
        PlanId PlanId,
        ProjectId ProjectId,
        TaskId TaskId,
        string NewName,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record TagAssigned(
        PlanId PlanId,
        ProjectId ProjectId,
        TaskId TaskId,
        TagId TagId,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public sealed record TagUnassigned(
        PlanId PlanId,
        ProjectId ProjectId,
        TaskId TaskId,
        TagId TagId,
        IReadOnlyDictionary<string, string> Metadata,
        Guid Id,
        DateTimeOffset OccurredOn
    ) : PlanEvent(PlanId, Metadata, Id, OccurredOn)
    {
        // TODO: add guard clauses or Contract checks in your EzDdd port.
    }

    public static class TypeMapper
    {
        public const string MappingTypePrefix = "PlanEvents.";
        public const string PlanCreatedType = MappingTypePrefix + "PlanCreated";
        public const string PlanRenamedType = MappingTypePrefix + "PlanRenamed";
        public const string PlanDeletedType = MappingTypePrefix + "PlanDeleted";
        public const string ProjectCreatedType = MappingTypePrefix + "ProjectCreated";
        public const string ProjectDeletedType = MappingTypePrefix + "ProjectDeleted";
        public const string TaskCreatedType = MappingTypePrefix + "TaskCreated";
        public const string TaskCheckedType = MappingTypePrefix + "TaskChecked";
        public const string TaskUncheckedType = MappingTypePrefix + "TaskUnchecked";
        public const string TaskDeletedType = MappingTypePrefix + "TaskDeleted";
        public const string TaskDeadlineSetType = MappingTypePrefix + "TaskDeadlineSet";
        public const string TaskRenamedType = MappingTypePrefix + "TaskRenamed";
        public const string TagAssignedType = MappingTypePrefix + "TagAssigned";
        public const string TagUnassignedType = MappingTypePrefix + "TagUnassigned";

        public static readonly IReadOnlyDictionary<string, Type> Map =
            new Dictionary<string, Type>
            {
                [PlanCreatedType] = typeof(PlanCreated),
                [PlanRenamedType] = typeof(PlanRenamed),
                [PlanDeletedType] = typeof(PlanDeleted),
                [ProjectCreatedType] = typeof(ProjectCreated),
                [ProjectDeletedType] = typeof(ProjectDeleted),
                [TaskCreatedType] = typeof(TaskCreated),
                [TaskCheckedType] = typeof(TaskChecked),
                [TaskUncheckedType] = typeof(TaskUnchecked),
                [TaskDeletedType] = typeof(TaskDeleted),
                [TaskDeadlineSetType] = typeof(TaskDeadlineSet),
                [TaskRenamedType] = typeof(TaskRenamed),
                [TagAssignedType] = typeof(TagAssigned),
                [TagUnassignedType] = typeof(TagUnassigned)
            };
    }
}
