using System.Text.Json.Serialization;
using System.Globalization;
using Lab.BoundedContextContracts.Procurement.IntegrationEvents;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Npgsql;
using Procurement.Applications;
using Procurement.Domains;
using Procurement.Infrastructure;
using Wolverine;
using Wolverine.Kafka;
using Wolverine.Postgresql;

var builder = WebApplication.CreateBuilder(args);
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? throw new InvalidOperationException("ConnectionStrings:DefaultConnection is required.");

builder.Services.AddSingleton(NpgsqlDataSource.Create(connectionString));
builder.Services.AddScoped<PostgresPurchaseStore>();
builder.Services.AddScoped<IPurchaseOrderRepository>(sp => sp.GetRequiredService<PostgresPurchaseStore>());
builder.Services.AddScoped<IPurchaseOrderQueries>(sp => sp.GetRequiredService<PostgresPurchaseStore>());
builder.Services.AddScoped<IPurchaseCreationCommitter>(sp => sp.GetRequiredService<PostgresPurchaseStore>());
builder.Services.AddScoped<IPurchaseSubmissionCommitter>(sp => sp.GetRequiredService<PostgresPurchaseStore>());
builder.Services.AddScoped<IGoodsReceiptCommitter>(sp => sp.GetRequiredService<PostgresPurchaseStore>());
builder.Services.AddScoped<IOperationUseCase<QuoteSupplierInput, SupplierQuoteResponse>, QuoteSupplierUseCase>();
builder.Services.AddScoped<IOperationUseCase<GetPurchaseInput, PurchaseOrderResponse>, GetPurchaseUseCase>();
builder.Services.AddScoped<IOperationUseCase<ListPurchasesInput, IReadOnlyList<PurchaseOrderResponse>>, ListPurchasesUseCase>();
builder.Services.AddScoped<IOperationUseCase<CreatePurchaseInput, CreatePurchaseOutput>, CreatePurchaseUseCase>();
builder.Services.AddScoped<IOperationUseCase<ReconcilePurchaseInput, PurchaseOrderResponse>, ReconcilePurchaseUseCase>();
builder.Services.AddScoped<IOperationUseCase<ReceiveGoodsInput, ReceiveGoodsOutput>, ReceiveGoodsUseCase>();
builder.Services.AddSingleton<ISupplierGateway, HttpSupplierGateway>();
builder.Services.AddHostedService<ProcurementOutboxRelay>();

var timeoutSetting = builder.Configuration["SupplierHttp:TimeoutSeconds"] ?? "2";
if (!int.TryParse(timeoutSetting, NumberStyles.None, CultureInfo.InvariantCulture, out var timeoutSeconds)
    || timeoutSeconds is < 1 or > 30)
    throw new InvalidOperationException("SupplierHttp:TimeoutSeconds must be an integer from 1 through 30.");

foreach (var profile in new[] { "direct", "wiremock", "microcks" })
{
    var configured = builder.Configuration[$"SupplierProfiles:{profile}"]
        ?? throw new InvalidOperationException($"SupplierProfiles:{profile} is required.");
    if (!Uri.TryCreate(configured, UriKind.Absolute, out var uri) || uri.Scheme is not ("http" or "https"))
        throw new InvalidOperationException($"SupplierProfiles:{profile} must be an absolute HTTP URI.");
    if (!uri.AbsoluteUri.EndsWith('/')) uri = new Uri(uri.AbsoluteUri + "/");
    builder.Services.AddHttpClient($"supplier-{profile}", client =>
    {
        client.BaseAddress = uri;
        client.Timeout = TimeSpan.FromSeconds(timeoutSeconds);
    });
}

builder.Host.UseWolverine(options =>
{
    var profile = builder.Configuration["Messaging:Profile"] ?? "Kafka";
    if (profile.Equals("InMemory", StringComparison.OrdinalIgnoreCase))
    {
        options.StubAllExternalTransports();
        options.PublishMessage<GoodsReceived>().Locally();
    }
    else if (profile.Equals("Kafka", StringComparison.OrdinalIgnoreCase))
    {
        var brokers = builder.Configuration["Messaging:Kafka:ConnectionString"]
            ?? throw new InvalidOperationException("Messaging:Kafka:ConnectionString is required.");
        options.PersistMessagesWithPostgresql(connectionString, "procurement_wolverine");
        options.UseKafka(brokers).AutoProvision();
        options.PublishMessage<GoodsReceived>().ToKafkaTopic("procurement.integration.events").UseDurableOutbox();
    }
    else throw new InvalidOperationException("Messaging:Profile must be Kafka or InMemory.");
});

builder.Services.AddControllers().AddJsonOptions(options =>
    options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter()));
builder.Services.Configure<Microsoft.AspNetCore.Mvc.ApiBehaviorOptions>(options =>
{
    options.InvalidModelStateResponseFactory = context =>
    {
        var detail = string.Join("; ", context.ModelState.Values.SelectMany(x => x.Errors)
            .Select(x => x.ErrorMessage).Where(x => !string.IsNullOrWhiteSpace(x)).Take(5));
        var problem = new ProblemDetails
        {
            Status = StatusCodes.Status400BadRequest,
            Title = "Invalid request",
            Detail = "The request body is invalid."
        };
        problem.Extensions["code"] = "invalid_request";
        problem.Extensions["message"] = detail.Length > 0 ? detail : "The request body is invalid.";
        return new BadRequestObjectResult(problem);
    };
});
builder.Services.AddHealthChecks().AddCheck<ProcurementDatabaseHealthCheck>("postgresql");

var app = builder.Build();
app.UseExceptionHandler(errorApp => errorApp.Run(async context =>
{
    var exception = context.Features.Get<IExceptionHandlerFeature>()?.Error;
    var (status, code, message) = exception switch
    {
        ProcurementRuleException rule when rule.Code.EndsWith("not_found", StringComparison.Ordinal) =>
            (404, rule.Code, rule.Message),
        ProcurementRuleException rule when rule.Code.StartsWith("invalid", StringComparison.Ordinal) =>
            (400, rule.Code, rule.Message),
        ProcurementRuleException rule => (409, rule.Code, rule.Message),
        SupplierGatewayException supplier when supplier.Code == "supplier_not_found" =>
            (404, supplier.Code, supplier.Message),
        SupplierGatewayException supplier when supplier.Code == "supplier_identity_conflict" =>
            (409, supplier.Code, supplier.Message),
        SupplierGatewayException supplier when supplier.Code == "supplier_business_rejection" =>
            (400, supplier.Code, supplier.Message),
        SupplierGatewayException supplier when supplier.Code == "supplier_timeout" =>
            (504, supplier.Code, supplier.Message),
        SupplierGatewayException supplier => (502, supplier.Code, supplier.Message),
        TaskCanceledException => (504, "supplier_timeout", "Supplier request timed out."),
        HttpRequestException => (502, "supplier_unavailable", "Supplier is unavailable."),
        _ => (500, "internal_error", "An unexpected error occurred.")
    };
    context.Response.StatusCode = status;
    var problem = new ProblemDetails { Status = status, Title = code, Detail = message };
    problem.Extensions["code"] = code;
    problem.Extensions["message"] = message;
    await context.Response.WriteAsJsonAsync(problem);
}));
app.MapControllers();
app.MapHealthChecks("/health");
app.Run();

/// <summary>採購 API 的主機入口。</summary>
public partial class Program;

/// <summary>確認採購資料庫可供本機 API 使用。</summary>
public sealed class ProcurementDatabaseHealthCheck(NpgsqlDataSource dataSource) : IHealthCheck
{
    /// <inheritdoc />
    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        try
        {
            await using var connection = await dataSource.OpenConnectionAsync(cancellationToken);
            await using var command = new NpgsqlCommand("SELECT 1", connection);
            await command.ExecuteScalarAsync(cancellationToken);
            return HealthCheckResult.Healthy();
        }
        catch (Exception ex) { return HealthCheckResult.Unhealthy("PostgreSQL is unavailable.", ex); }
    }
}
