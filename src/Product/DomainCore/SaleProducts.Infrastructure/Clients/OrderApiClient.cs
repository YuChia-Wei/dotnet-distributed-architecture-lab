using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Json;
using Lab.MessageSchemas.Orders.DataTransferObjects;

namespace SaleProducts.Infrastructure.Clients;

/// <summary>
/// 訂單服務 API 用戶端介面。
/// </summary>
public interface IOrderApiClient
{
    /// <summary>
    /// 依訂單識別碼取得訂單明細。
    /// </summary>
    /// <param name="orderId">訂單識別碼。</param>
    /// <returns>訂單明細資料。</returns>
    Task<OrderDetailsResponse> GetOrderDetailsAsync(Guid orderId);
}

/// <summary>
/// 透過 HTTP 呼叫訂單服務的 API 用戶端。
/// </summary>
public class OrderApiClient : IOrderApiClient
{
    private readonly HttpClient _httpClient;

    /// <summary>
    /// 建立 <see cref="OrderApiClient"/> 執行個體。
    /// </summary>
    /// <param name="httpClient">預先設定的 <see cref="HttpClient"/>。</param>
    public OrderApiClient(HttpClient httpClient)
    {
        this._httpClient = httpClient;
    }

    /// <inheritdoc />
    public async Task<OrderDetailsResponse> GetOrderDetailsAsync(Guid orderId)
    {
        var response = await this._httpClient.GetAsync($"api/orders/{orderId}");
        if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
        {
            throw new KeyNotFoundException($"Order {orderId} not found when requesting details.");
        }

        response.EnsureSuccessStatusCode();

        var orderDetails = await response.Content.ReadFromJsonAsync<OrderDetailsResponse>();
        if (orderDetails is null)
        {
            throw new InvalidOperationException($"Order {orderId} details response body is empty.");
        }

        return orderDetails;
    }
}
