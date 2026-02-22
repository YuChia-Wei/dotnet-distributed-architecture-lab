using System;
using Example.Plans.Domain;

namespace Example.Plans.UseCases;

public sealed class CreatePlanService : ICreatePlanUseCase
{
    private readonly IRepository<Plan, PlanId> _planRepository;

    public CreatePlanService(IRepository<Plan, PlanId> planRepository)
    {
        Contract.RequireNotNull("PlanRepository", planRepository);
        _planRepository = planRepository;
    }

    public CqrsOutput Execute(CreatePlanInput input)
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
            if (_planRepository.FindById(planId) != null)
            {
                throw new ArgumentException($"Plan with id {input.Id} already exists");
            }

            var plan = new Plan(planId, input.Name ?? string.Empty, input.UserId!);
            _planRepository.Save(plan);

            output.SetId(input.Id)
                  .SetExitCode(ExitCode.Success);
            return output;
        }
        catch (Exception ex)
        {
            throw new UseCaseFailureException(ex);
        }
    }

    // Wolverine handler entry point
    public CqrsOutput Handle(CreatePlanInput input) => Execute(input);
}
