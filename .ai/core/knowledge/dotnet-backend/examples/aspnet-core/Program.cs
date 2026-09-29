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
if (env.IsEnvironment("Outbox") || env.IsEnvironment("TestOutbox"))
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

// Initialize the target-owned domain event type mapper registry.
BootstrapConfig.Initialize();

app.MapGet("/", () => "ExampleAppApp (.NET) is running.");
app.Run();
