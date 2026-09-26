param(
    [switch]$NoBuild,
    [ValidateRange(15, 300)][int]$TimeoutSeconds = 120
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$composeDir = Join-Path $repoRoot 'docker-compose'
$composeArgs = @(
    '-p', 'mqarchlab-pr5-integration',
    '--profile', 'procurement-lab', '--profile', 'verification', '--profile', 'frontend-lab',
    '-f', (Join-Path $composeDir 'docker-compose.yml'),
    '-f', (Join-Path $composeDir 'docker-compose.override.yml'),
    '-f', (Join-Path $composeDir 'docker-compose.verification.yml'),
    '-f', (Join-Path $composeDir 'docker-compose.procurement.yml'),
    '-f', (Join-Path $composeDir 'docker-compose.frontend.yml')
)

function Invoke-Compose([string[]]$Parameters) {
    & docker compose @composeArgs @Parameters
    if ($LASTEXITCODE -ne 0) { throw "docker compose failed: $($Parameters -join ' ')" }
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

# Reuse the procurement bootstrap; it preserves volumes and starts only selected commerce services.
$procurementArgs = @{ TimeoutSeconds = $TimeoutSeconds }
if ($NoBuild) { $procurementArgs.NoBuild = $true }
& (Join-Path $repoRoot 'scripts/procurement-lab/Start-Lab.ps1') @procurementArgs
if (-not $?) { throw 'Procurement bootstrap failed.' }

Invoke-Compose -Parameters @('config', '--quiet')
Invoke-Compose -Parameters @('up', '-d', '--no-deps', 'postgres-order', 'postgres-product')
Wait-Database 'postgres-order' 'orders_db'
Wait-Database 'postgres-product' 'products_db'

$appArgs = @('up', '-d', '--no-deps')
if ($NoBuild) { $appArgs += '--no-build' } else { $appArgs += '--build' }
$appArgs += @('orders-api', 'product-api', 'orders-consumer', 'product-consumer',
    'web-frontend', 'admin-frontend', 'yarp-gateway')
Invoke-Compose -Parameters $appArgs

Wait-Http 'http://127.0.0.1:8888/web/'
Wait-Http 'http://127.0.0.1:8888/admin/'
Write-Output 'Frontend lab: http://127.0.0.1:8888/web/ and http://127.0.0.1:8888/admin/'
Write-Output 'Check the Admin integrations page for the current Microcks state; select a Supplier API preset only if needed.'
