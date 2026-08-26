using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Example.Plans.Outbox;

[Table("task")]
public sealed class TaskData
{
    [Key]
    [Column("id")]
    public string TaskId { get; set; } = string.Empty;

    [Column("name")]
    public string Name { get; set; } = string.Empty;

    [Column("project_name")]
    public string ProjectName { get; set; } = string.Empty;

    [ForeignKey(nameof(ProjectData))]
    [Column("project_id")]
    public string ProjectId { get; set; } = string.Empty;

    public ProjectData? ProjectData { get; set; }

    [Column("is_done")]
    public bool IsDone { get; set; }

    [Column("deadline")]
    public DateOnly? Deadline { get; set; }

    public List<TaskTagData> TagIds { get; set; } = new();
}

[Table("task_tag")]
public sealed class TaskTagData
{
    [Column("task_id")]
    public string TaskId { get; set; } = string.Empty;

    [Column("tag_id")]
    public string TagId { get; set; } = string.Empty;
}
