using Lab.BuildingBlocks.Domains;
using Lab.BuildingBlocks.Integrations;
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

    // 2. 將 Integration Events 送進 RabbitMQ
    // 要依據介面區分發送的目標的話，傳遞給第三方服務的寫法要這樣比較安全
    opts.Publish(rule =>
    {
        rule.MessagesImplementing<IIntegrationEvent>();
        rule.ToRabbitQueue("orders")
            .UseDurableOutbox();
    });

    // 2. 將 Integration Events 送進 RabbitMQ
    // 這是錯誤寫法， wolverine 無法依據介面建立 rabbit 所需要的路由資源
    // by ai: PublishMessage<T>() 僅適合「具體型別」或「共用抽象基底類別」。
    // opts.PublishMessage<IIntegrationEvent>()
    //     .ToRabbitQueue("orders") // 直接對 Queue
    //     .UseDurableOutbox(); // 建議開啟 Outbox，確保至少一次送達

    // 3. 將 Domain Events 送進 in-memory bus
    // in-memory bus 沒有介面解析的限制
    opts.PublishMessage<IDomainEvent>()
        .Locally();

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