using System;
using System.Collections.Generic;

namespace Example.Plans.UseCases.Port;

// Complex DTO template: mixed types, optional fields, enums, and collections.
public sealed class TaskDto
{
    public enum TaskStatus
    {
        Todo,
        InProgress,
        Done,
        Cancelled
    }

    public enum TaskPriority
    {
        Low = 1,
        Medium = 2,
        High = 3,
        Urgent = 4
    }

    public string Id { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
    public string? Description { get; private set; }

    public string ProjectId { get; private set; } = string.Empty;
    public string PlanId { get; private set; } = string.Empty;

    public bool IsDone { get; private set; }
    public TaskStatus Status { get; private set; }
    public TaskPriority Priority { get; private set; }

    public DateOnly? Deadline { get; private set; }
    public DateOnly CreatedDate { get; private set; }
    public DateOnly? CompletedDate { get; private set; }

    public HashSet<string> TagIds { get; private set; } = new();
    public HashSet<string> AssigneeIds { get; private set; } = new();
    public Dictionary<string, string> Metadata { get; private set; } = new();

    public int CommentCount { get; private set; }
    public int AttachmentCount { get; private set; }

    public TaskDto()
    {
        IsDone = false;
        Status = TaskStatus.Todo;
        Priority = TaskPriority.Medium;
        CreatedDate = DateOnly.FromDateTime(DateTime.UtcNow);
    }

    public TaskDto SetId(string id)
    {
        Id = id;
        return this;
    }

    public TaskDto SetName(string name)
    {
        Name = name;
        return this;
    }

    public TaskDto SetDescription(string? description)
    {
        Description = description;
        return this;
    }

    public TaskDto SetProjectId(string projectId)
    {
        ProjectId = projectId;
        return this;
    }

    public TaskDto SetPlanId(string planId)
    {
        PlanId = planId;
        return this;
    }

    public TaskDto SetDone(bool done)
    {
        IsDone = done;
        if (done && CompletedDate == null)
        {
            CompletedDate = DateOnly.FromDateTime(DateTime.UtcNow);
        }
        return this;
    }

    public TaskDto SetStatus(TaskStatus status)
    {
        Status = status;
        return this;
    }

    public TaskDto SetPriority(TaskPriority priority)
    {
        Priority = priority;
        return this;
    }

    public TaskDto SetDeadline(DateOnly? deadline)
    {
        Deadline = deadline;
        return this;
    }

    public TaskDto SetCreatedDate(DateOnly createdDate)
    {
        CreatedDate = createdDate;
        return this;
    }

    public TaskDto SetCompletedDate(DateOnly? completedDate)
    {
        CompletedDate = completedDate;
        return this;
    }

    public TaskDto SetTagIds(IEnumerable<string> tagIds)
    {
        TagIds = new HashSet<string>(tagIds);
        return this;
    }

    public TaskDto SetAssigneeIds(IEnumerable<string> assigneeIds)
    {
        AssigneeIds = new HashSet<string>(assigneeIds);
        return this;
    }

    public TaskDto SetMetadata(Dictionary<string, string> metadata)
    {
        Metadata = metadata;
        return this;
    }

    public TaskDto SetCommentCount(int commentCount)
    {
        CommentCount = commentCount;
        return this;
    }

    public TaskDto SetAttachmentCount(int attachmentCount)
    {
        AttachmentCount = attachmentCount;
        return this;
    }

    public TaskDto AddTag(string tagId)
    {
        TagIds.Add(tagId);
        return this;
    }

    public TaskDto RemoveTag(string tagId)
    {
        TagIds.Remove(tagId);
        return this;
    }

    public TaskDto AddAssignee(string assigneeId)
    {
        AssigneeIds.Add(assigneeId);
        return this;
    }

    public TaskDto PutMetadata(string key, string value)
    {
        Metadata[key] = value;
        return this;
    }

    public bool IsOverdue()
    {
        return Deadline.HasValue && DateOnly.FromDateTime(DateTime.UtcNow) > Deadline.Value && !IsDone;
    }

    public bool HasDescription() => !string.IsNullOrWhiteSpace(Description);
    public bool HasDeadline() => Deadline.HasValue;
    public bool HasTags() => TagIds.Count > 0;
}
