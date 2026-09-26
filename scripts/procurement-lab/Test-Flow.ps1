param(
    [Parameter(Mandatory)][Guid]$ProductId,
    [switch]$SeedInventory,
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'
$procurementBase = 'http://127.0.0.1:8180/api/procurement'
$inventoryBase = 'http://127.0.0.1:8185/api/inventory'

function Send-Json([string]$Uri, $Body) {
    $response = Invoke-WebRequest -Method Post -Uri $Uri -ContentType 'application/json' `
        -Body ($Body | ConvertTo-Json -Depth 5) -TimeoutSec 30 -SkipHttpErrorCheck
    $content = if ($response.Content) { $response.Content | ConvertFrom-Json } else { $null }
    return [pscustomobject]@{ Status = [int]$response.StatusCode; Body = $content }
}

function Assert-Equal($Actual, $Expected, [string]$Label) {
    if ($Actual -ne $Expected) { throw "$Label expected=$Expected actual=$Actual" }
}

function Get-Stock {
    $result = Invoke-RestMethod -Uri "$inventoryBase/product/$ProductId" -TimeoutSec 10
    return [int]$result.availableQuantity
}

function Wait-Stock([int]$Expected) {
    $deadline = [DateTimeOffset]::UtcNow.AddSeconds(60)
    do {
        try {
            $actual = Get-Stock
            if ($actual -eq $Expected) { return }
        } catch { }
        Start-Sleep -Seconds 2
    } while ([DateTimeOffset]::UtcNow -lt $deadline)
    throw "Inventory did not reach stock $Expected within 60 seconds; last observed=$actual"
}

if ($SeedInventory) {
    $seed = Send-Json "$inventoryBase/product/$ProductId" @{ stock = 20 }
    Assert-Equal $seed.Status 200 'Inventory initialization HTTP status'
}
Assert-Equal (Get-Stock) 20 'Initial stock'

$quote = Invoke-RestMethod -Uri "$procurementBase/suppliers/direct/catalog/REAL-001" -TimeoutSec 10
Assert-Equal $quote.sku 'REAL-001' 'Quote SKU'
Assert-Equal $quote.currency 'TWD' 'Quote currency'
Assert-Equal $quote.origin 'sandbox' 'Direct quote origin'

$clientRequestId = [Guid]::NewGuid()
$purchase = Send-Json "$procurementBase/purchase-orders" @{
    clientRequestId = $clientRequestId
    productId = $ProductId
    supplierSku = 'REAL-001'
    quantity = 10
    unitPrice = $quote.unitPrice
    currency = 'TWD'
    provider = 'direct'
}
Assert-Equal $purchase.Status 201 'Purchase creation HTTP status'
Assert-Equal $purchase.Body.state 'Accepted' 'Supplier acceptance'
$purchaseOrderId = [Guid]$purchase.Body.id
if ($purchaseOrderId -eq [Guid]::Empty) { throw 'Purchase creation returned no id.' }
Assert-Equal (Get-Stock) 20 'Supplier acceptance leaves stock unchanged'

$firstReceiptId = [Guid]::NewGuid()
$first = Send-Json "$procurementBase/purchase-orders/$purchaseOrderId/receipts" `
    @{ receiptId = $firstReceiptId; quantity = 6 }
Assert-Equal $first.Status 201 'First receipt HTTP status'
Assert-Equal $first.Body.created $true 'First receipt created'
Wait-Stock 26

$replay = Send-Json "$procurementBase/purchase-orders/$purchaseOrderId/receipts" `
    @{ receiptId = $firstReceiptId; quantity = 6 }
Assert-Equal $replay.Status 200 'Receipt replay HTTP status'
Assert-Equal $replay.Body.created $false 'Receipt replay outcome'
Start-Sleep -Seconds 2
Assert-Equal (Get-Stock) 26 'Receipt replay leaves stock unchanged'

$secondReceiptId = [Guid]::NewGuid()
$second = Send-Json "$procurementBase/purchase-orders/$purchaseOrderId/receipts" `
    @{ receiptId = $secondReceiptId; quantity = 4 }
Assert-Equal $second.Status 201 'Second receipt HTTP status'
Wait-Stock 30
$order = Invoke-RestMethod -Uri "$procurementBase/purchase-orders/$purchaseOrderId" -TimeoutSec 10
Assert-Equal $order.receivedQuantity 10 'Total received quantity'
Assert-Equal $order.state 'Received' 'Final purchase state'

$evidence = [ordered]@{
    observedAt = [DateTimeOffset]::UtcNow.ToString('o')
    outcome = 'passed'
    productId = $ProductId.ToString('D')
    clientRequestId = $clientRequestId.ToString('D')
    purchaseOrderId = $purchaseOrderId.ToString('D')
    firstReceiptId = $firstReceiptId.ToString('D')
    secondReceiptId = $secondReceiptId.ToString('D')
    firstReceiptReplayStatus = $replay.Status
    initialStock = 20
    finalStock = 30
}
if ($OutputPath) {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
    $resolved = if ([System.IO.Path]::IsPathRooted($OutputPath)) { $OutputPath } else { Join-Path $repoRoot $OutputPath }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $resolved) | Out-Null
    $evidence | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $resolved -Encoding utf8
}
$evidence | ConvertTo-Json -Depth 5
