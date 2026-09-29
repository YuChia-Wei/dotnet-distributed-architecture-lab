using System;
using System.Threading;
using System.Threading.Tasks;
using Example.Plans.Domain;

namespace Example.Plans.UseCases;

/// <summary>建立方案的應用流程。</summary>
public sealed class CreatePlanUseCase : ICreatePlanUseCase
{
    private readonly IAggregateRepository<Plan, PlanId> _planRepository;

    public CreatePlanUseCase(IAggregateRepository<Plan, PlanId> planRepository)
    {
        Contract.RequireNotNull("PlanRepository", planRepository);
        _planRepository = planRepository;
    }

    public async Task<CqrsOutput> ExecuteAsync(
        CreatePlanInput input,
        CancellationToken cancellationToken)
    {
        try
        {
            var output = CqrsOutput.Create();

            Contract.RequireNotNull("Input", input);
            Contract.RequireNotNull("Plan id", input.Id);
            Contract.RequireNotNull("User id", input.UserId);

            if (input.Name != null && string.IsNullOrWhiteSpace(input.Name))
            {
                output.SetExitCode(ExitCode.Failure)
                      .SetMessage("Plan name cannot be empty");
                return output;
            }

            var planId = PlanId.ValueOf(input.Id!);
            if (await _planRepository.FindByIdAsync(planId, cancellationToken) != null)
            {
                throw new ArgumentException($"Plan with id {input.Id} already exists");
            }

            var plan = new Plan(planId, input.Name ?? string.Empty, input.UserId!);
            await _planRepository.SaveAsync(plan, cancellationToken);

            output.SetId(input.Id)
                  .SetExitCode(ExitCode.Success);
            return output;
        }
        catch (Exception ex)
        {
            throw new UseCaseFailureException(ex);
        }
    }
}
