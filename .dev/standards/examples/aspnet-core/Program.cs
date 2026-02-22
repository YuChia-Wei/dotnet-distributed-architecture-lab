using Example.Plans.Hosting;
using Example.Plans.Outbox;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);

// Load configuration + environment
var env = builder.Environment;
var config = builder.Configuration;

// Profile-based registration
if (env.IsEnvironment("Outbox") || env.IsEnvironment("Test-Outbox"))
{
    builder.Services.AddPlanDataSource(config);
    builder.Services.AddOutboxRepositories(config);
    // TODO: configure Wolverine durable outbox + message relay
}
else
{
    builder.Services.AddInMemoryRepositories();
}

builder.Services.AddUseCases();

var app = builder.Build();

// Initialize domain event type mapper registry (ezDDD port)
BootstrapConfig.Initialize();

app.MapGet("/", () => "AiScrumApp (.NET) is running.");
app.Run();
