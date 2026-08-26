using System;
using System.Threading;
using System.Threading.Tasks;
using Example.Plans.Domain;

namespace Example.Plans.UseCases;

/// <summary>建立任務的應用流程。</summary>
public sealed class CreateTaskUseCase : ICreateTaskUseCase
{
    private readonly IAggregateRepository<Plan, PlanId> _planRepository;

    public CreateTaskUseCase(IAggregateRepository<Plan, PlanId> planRepository)
    {
        Contract.RequireNotNull("PlanRepository", planRepository);
        _planRepository = planRepository;
    }

    public async Task<CqrsOutput> ExecuteAsync(
        CreateTaskInput input,
        CancellationToken cancellationToken)
    {
        try
        {
            var output = CqrsOutput.Create();

            Contract.RequireNotNull("Input", input);
            Contract.RequireNotNull("Plan id", input.PlanId);
            Contract.RequireNotNull("Project name", input.ProjectName);
            Contract.RequireNotNull("Task name", input.TaskName);

            var plan = await _planRepository.FindByIdAsync(
                input.PlanId!,
                cancellationToken);
            if (plan == null)
            {
                output.SetId(input.PlanId!.Value)
                      .SetExitCode(ExitCode.Failure)
                      .SetMessage($"Create task failed: plan not found, plan id = {input.PlanId!.Value}");
                return output;
            }

            var taskId = plan.CreateTask(input.ProjectName!, TaskId.Create(), input.TaskName!);
            await _planRepository.SaveAsync(plan, cancellationToken);

            output.SetId(taskId.Value)
                  .SetExitCode(ExitCode.Success);
            return output;
        }
        catch (Exception ex)
        {
            throw new UseCaseFailureException(ex);
        }
    }
}
