param(
    [switch]$NoBuild,
    [Guid]$InventoryProductId,
    [ValidateRange(10, 300)][int]$TimeoutSeconds = 90
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$composeDir = Join-Path $repoRoot 'docker-compose'
$composeArgs = @(
    '-p', 'mqarchlab-pr5-integration',
    '--profile', 'procurement-lab',
    '--profile', 'verification',
    '-f', (Join-Path $composeDir 'docker-compose.yml'),
    '-f', (Join-Path $composeDir 'docker-compose.override.yml'),
    '-f', (Join-Path $composeDir 'docker-compose.verification.yml'),
    '-f', (Join-Path $composeDir 'docker-compose.procurement.yml')
)

function Invoke-Compose([string[]]$ComposeParameters) {
    & docker compose @composeArgs @ComposeParameters
    if ($LASTEXITCODE -ne 0) { throw "docker compose failed: $($ComposeParameters -join ' ')" }
}

function Wait-Database([string]$Service, [string]$Database) {
    $deadline = [DateTimeOffset]::UtcNow.AddSeconds($TimeoutSeconds)
    do {
        & docker compose @composeArgs exec -T $Service pg_isready -U user -d $Database *> $null
        if ($LASTEXITCODE -eq 0) { return }
        Start-Sleep -Seconds 2
    } while ([DateTimeOffset]::UtcNow -lt $deadline)
    throw "$Service did not become ready within $TimeoutSeconds seconds."
}

function Invoke-Migration([string]$Service, [string]$Database, [string]$RelativePath) {
    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Migration file missing: $path" }
    Get-Content -LiteralPath $path -Raw | & docker compose @composeArgs exec -T $Service `
        psql -U user -d $Database -v ON_ERROR_STOP=1
    if ($LASTEXITCODE -ne 0) { throw "Migration failed: $RelativePath" }
}

function Wait-Http([string]$Uri) {
    $deadline = [DateTimeOffset]::UtcNow.AddSeconds($TimeoutSeconds)
    do {
        try {
            $response = Invoke-WebRequest -Uri $Uri -TimeoutSec 3 -SkipHttpErrorCheck
            if ([int]$response.StatusCode -eq 200) { return }
        } catch { }
        Start-Sleep -Seconds 2
    } while ([DateTimeOffset]::UtcNow -lt $deadline)
    throw "$Uri did not return HTTP 200 within $TimeoutSeconds seconds."
}

Invoke-Compose -ComposeParameters @('config', '--quiet')
Invoke-Compose -ComposeParameters @('up', '-d', '--no-deps', 'kafka', 'postgres-inventory', 'postgres-procurement', 'postgres-supplier')
Wait-Database 'postgres-inventory' 'inventory_db'
Wait-Database 'postgres-procurement' 'procurement_db'
Wait-Database 'postgres-supplier' 'supplier_db'

# Existing PostgreSQL volumes skip docker-entrypoint-initdb.d; both SQL files are repeatable.
Invoke-Migration 'postgres-inventory' 'inventory_db' `
    'docker-compose/sql-script/migrations/inventory/20260926_0003_add_inventory_goods_receipts.sql'
Invoke-Migration 'postgres-procurement' 'procurement_db' `
    'docker-compose/sql-script/procurement/001-procurement.sql'

$applicationArgs = @('up', '-d', '--no-deps')
if ($NoBuild) { $applicationArgs += '--no-build' } else { $applicationArgs += '--build' }
$applicationArgs += @('supplier-sandbox', 'supplier-mock', 'microcks', 'inventory-api', 'inventory-consumer', 'procurement-api')
Invoke-Compose -ComposeParameters $applicationArgs

Wait-Http 'http://127.0.0.1:8181/health'
Wait-Http 'http://127.0.0.1:8182/health'
Wait-Http 'http://127.0.0.1:8180/health'
Wait-Http 'http://127.0.0.1:8184/api/services?page=0&size=1'
if ($PSBoundParameters.ContainsKey('InventoryProductId') -and $InventoryProductId -ne [Guid]::Empty) {
    Wait-Http "http://127.0.0.1:8185/api/inventory/product/$InventoryProductId"
}

Write-Output 'Lab endpoints: Procurement http://127.0.0.1:8180/ ; Sandbox http://127.0.0.1:8181/ ; WireMock control http://127.0.0.1:8182/ ; Microcks http://127.0.0.1:8184/ ; Inventory http://127.0.0.1:8185/'
Write-Output 'Import a selected supplier YAML with Set-MicrocksMode.ps1 or the Microcks Quick Import UI before using the microcks provider.'
