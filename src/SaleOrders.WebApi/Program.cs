using SaleOrders.Applications;
using SaleOrders.Infrastructure;
using Scalar.AspNetCore;
using Wolverine;
using Wolverine.RabbitMQ;

var builder = WebApplication.CreateBuilder(args);

builder.Host.UseWolverine(opts =>
{
    // 1. 設定訊息總管（RabbitMQ）
    var rabbitMqConnectionString = builder.Configuration.GetConnectionString("MessageBroker");
    opts.UseRabbitMq(new Uri(rabbitMqConnectionString!))
        .AutoProvision();

    // 2. 將所有訊息預設送進 named queue
    opts.PublishAllMessages()
        .ToRabbitQueue("orders") // 直接對 Queue
        .UseDurableOutbox(); // 建議開啟 Outbox，確保至少一次送達

    // 掃描 application 的 DI 擴充，避免在掃描的時候直接倚賴到內部的實作型別
    opts.Discovery.IncludeAssembly(typeof(SaleOrders.Applications.ServiceCollectionExtensions).Assembly);
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