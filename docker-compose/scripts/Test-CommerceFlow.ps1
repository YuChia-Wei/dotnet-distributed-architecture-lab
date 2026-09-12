param(
    [string]$BaseUri = 'http://localhost:8888',
    [string]$OutputPath = 'artifacts/nuget-consumer/compose-commerce-e2e.json'
)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
function Send-Json([string]$Method, [string]$Path, $Body) {
    Invoke-RestMethod -Method $Method -Uri "$BaseUri$Path" -ContentType 'application/json' -Body ($Body | ConvertTo-Json) -TimeoutSec 30
}
function Assert-Value($Actual, $Expected, [string]$Description) {
    if ($Actual -ne $Expected) { throw "$Description expected=$Expected actual=$Actual" }
}
$name = "compose-regression-$([Guid]::NewGuid())"
$product = Send-Json Post '/api/products' @{ name=$name; description='Compose regression'; price=20 }
$productId = $product.id
if (!$productId) { throw 'Product creation did not return an id.' }
$readProduct = Invoke-RestMethod "$BaseUri/api/products/$productId"
Assert-Value $readProduct.name $name 'Product readback'
$inventory = Send-Json Post "/api/inventory/product/$productId" @{ stock=10 }
Assert-Value $inventory.availableQuantity 10 'Initial stock'
$operationId = [Guid]::NewGuid().ToString()
$request = @{ operationId=$operationId; orderDate=[DateTimeOffset]::UtcNow.ToString('o'); totalAmount=40; productId=$productId; productName=$name; quantity=2 }
$order = Send-Json Post '/api/orders' $request
Assert-Value $order.isSuccess $true 'Order placement'
$orderId = $order.value.orderId
if (!$orderId) { throw 'Order creation did not return an id.' }
$remaining = Invoke-RestMethod "$BaseUri/api/inventory/product/$productId"
Assert-Value $remaining.availableQuantity 8 'Kafka reservation result'
$readOrder = Invoke-RestMethod "$BaseUri/api/orders/$orderId"
Assert-Value $readOrder.orderId $orderId 'Order readback'
Send-Json Patch "/api/orders/$orderId/ship" @{ reason='Compose regression shipment' } | Out-Null
Send-Json Patch "/api/orders/$orderId/deliver" @{ reason='Compose regression delivery' } | Out-Null
$cancelRequest = @{ operationId=[Guid]::NewGuid().ToString(); orderDate=[DateTimeOffset]::UtcNow.ToString('o'); totalAmount=20; productId=$productId; productName=$name; quantity=1 }
$cancelOrder = Send-Json Post '/api/orders' $cancelRequest
Assert-Value $cancelOrder.isSuccess $true 'Cancellable order placement'
Send-Json Patch "/api/orders/$($cancelOrder.value.orderId)/cancel" @{ reason='Compose regression cancellation' } | Out-Null
$beforeRejected = Invoke-RestMethod "$BaseUri/api/inventory/product/$productId"
$rejectedOperationId = [Guid]::NewGuid().ToString()
$rejectedRequest = @{ operationId=$rejectedOperationId; orderDate=[DateTimeOffset]::UtcNow.ToString('o'); totalAmount=2000; productId=$productId; productName=$name; quantity=100 }
$rejected = Invoke-WebRequest -Method Post -Uri "$BaseUri/api/orders" -ContentType 'application/json' -Body ($rejectedRequest | ConvertTo-Json) -TimeoutSec 30 -SkipHttpErrorCheck
Assert-Value ([int]$rejected.StatusCode) 400 'Insufficient stock rejection'
if ($rejected.Content -notmatch 'Inventory is not enough') { throw "Unexpected rejection: $($rejected.Content)" }
$afterRejected = Invoke-RestMethod "$BaseUri/api/inventory/product/$productId"
Assert-Value $afterRejected.availableQuantity $beforeRejected.availableQuantity 'Rejected order preserves stock'
$resolvedOutput = Join-Path $repoRoot $OutputPath
New-Item -ItemType Directory -Force (Split-Path $resolvedOutput) | Out-Null
[ordered]@{ observedAt=[DateTimeOffset]::UtcNow.ToString('o'); outcome='passed'; productId=$productId; operationId=$operationId; deliveredOrderId=$orderId; cancelledOrderId=$cancelOrder.value.orderId; rejectedOperationId=$rejectedOperationId; stockAfterReservation=8; stockAfterRejection=$afterRejected.availableQuantity; checks=@('Product create/read','Inventory seed/read','Kafka stock reservation','Order read','Ship and deliver','Cancel','Insufficient stock rejection') } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $resolvedOutput -Encoding utf8
Write-Output "Compose commerce E2E passed: $resolvedOutput"
