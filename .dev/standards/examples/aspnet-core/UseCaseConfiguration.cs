using Example.Plans.UseCases;
using Example.Plans.UseCases.Port;
using Microsoft.Extensions.DependencyInjection;

namespace Example.Plans.Hosting;

public static class UseCaseConfiguration
{
    public static IServiceCollection AddUseCases(this IServiceCollection services)
    {
        // Message bus / producer wiring (ezapp 2.0.0 equivalent)
        // TODO: configure Wolverine message bus + producers.

        // Use case services
        services.AddScoped<ICreatePlanUseCase, CreatePlanService>();
        services.AddScoped<ICreateTaskUseCase, CreateTaskService>();
        services.AddScoped<IDeleteTaskUseCase, DeleteTaskService>();
        services.AddScoped<IRenameTaskUseCase, RenameTaskService>();
        services.AddScoped<IAssignTagUseCase, AssignTagService>();
        services.AddScoped<IGetPlanUseCase, GetPlanService>();
        services.AddScoped<IGetPlansUseCase, GetPlansService>();
        services.AddScoped<IGetTasksByDateUseCase, GetTasksByDateService>();

        // Projection implementations (read side)
        // TODO: register EF Core projections for outbox profile only.

        // Reactors (event handlers)
        // TODO: register reactors with Wolverine.

        return services;
    }
}
