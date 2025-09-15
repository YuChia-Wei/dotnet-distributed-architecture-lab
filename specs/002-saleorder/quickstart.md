# Quickstart

1.  Run the `SaleOrders.WebApi` project.
2.  Create a new order by sending a `POST` request to `/api/orders`.
3.  Take note of the `orderId` from the response.
4.  Send a `PATCH` request to `/api/orders/{orderId}/cancel` to cancel the order.
5.  Verify that the response has a status code of 200 OK.
6.  Check the message queue for an `OrderCancelled` event.