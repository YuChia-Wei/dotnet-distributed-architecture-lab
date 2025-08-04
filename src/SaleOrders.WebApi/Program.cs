using SaleOrders.Applications;
using SaleOrders.Infrastructure;
using Scalar.AspNetCore;
using Wolverine;
using Wolverine.RabbitMQ;

var builder = WebApplication.CreateBuilder(args);

builder.Host.UseWolverine(opts =>
{
    var rabbitMqConnectionString = builder.Configuration.GetConnectionString("MessageBroker");
    opts.UseRabbitMq(new Uri(rabbitMqConnectionString!)).AutoProvision();
});

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();

// domain core DI
builder.Services.AddApplicationServices();
builder.Services.AddInfrastructureServices(builder.Configuration);

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi()
       .CacheOutput();

    app.MapScalarApiReference();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();