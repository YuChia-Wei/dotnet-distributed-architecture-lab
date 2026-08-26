using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Example.Plans.Outbox;

[Table("project")]
public sealed class ProjectData
{
    [Key]
    [Column("id")]
    public string ProjectId { get; set; } = string.Empty;

    [Column("name")]
    public string Name { get; set; } = string.Empty;

    [ForeignKey(nameof(PlanData))]
    [Column("plan_id")]
    public string PlanId { get; set; } = string.Empty;

    public PlanData? PlanData { get; set; }

    public List<TaskData> TaskDatas { get; set; } = new();

    public void AddTaskData(TaskData taskData)
    {
        taskData.ProjectData = this;
        TaskDatas.Add(taskData);
    }
}
