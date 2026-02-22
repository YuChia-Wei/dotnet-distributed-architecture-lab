using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Example.Shared.Outbox;

namespace Example.Plans.Outbox;

[Table("plan")]
public sealed class PlanData : IOutboxData<string>
{
    [NotMapped]
    public List<DomainEventData> DomainEventDatas { get; set; } = new();

    [NotMapped]
    public string StreamName { get; set; } = string.Empty;

    [Key]
    [Column("id")]
    public string PlanId { get; set; } = string.Empty;

    [Column("name")]
    public string Name { get; set; } = string.Empty;

    [Column("user_id")]
    public string UserId { get; set; } = string.Empty;

    [Column("next_task_id")]
    public int NextTaskId { get; set; }

    [Column("is_deleted")]
    public bool IsDeleted { get; set; }

    public List<ProjectData> ProjectDatas { get; set; } = new();

    [Column("created_at")]
    public DateTimeOffset CreatedAt { get; set; }

    [Column("last_updated")]
    public DateTimeOffset LastUpdated { get; set; }

    [ConcurrencyCheck]
    public long Version { get; set; }

    [NotMapped]
    public string Id
    {
        get => PlanId;
        set => PlanId = value;
    }

    public void AddProjectData(ProjectData projectData)
    {
        projectData.PlanData = this;
        ProjectDatas.Add(projectData);
    }
}
