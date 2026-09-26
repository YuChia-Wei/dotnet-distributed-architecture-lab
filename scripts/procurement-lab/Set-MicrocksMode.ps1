param(
    [Parameter(Mandatory)]
    [ValidateSet('mock', 'proxy', 'hybrid')]
    [string]$Mode,
    [string]$BearerToken
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$artifact = Join-Path $repoRoot "samples/SupplierMock/microcks/supplier-$Mode.yaml"
if (-not (Test-Path -LiteralPath $artifact -PathType Leaf)) {
    throw "Microcks artifact is missing: $artifact"
}

$headers = @{}
if ($BearerToken) { $headers.Authorization = "Bearer $BearerToken" }
$baseUri = 'http://127.0.0.1:8184'

try {
    Invoke-RestMethod -Method Post -Uri "$baseUri/api/artifact/upload?mainArtifact=true" `
        -Form @{ file = (Get-Item -LiteralPath $artifact) } -Headers $headers `
        -TimeoutSec 30 -ErrorAction Stop | Out-Null
} catch {
    throw "Microcks $Mode artifact upload failed: $($_.Exception.Message)"
}

$service = $null
$deadline = [DateTimeOffset]::UtcNow.AddSeconds(20)
do {
    try {
        $services = @(Invoke-RestMethod -Uri "$baseUri/api/services?page=0&size=100" `
            -Headers $headers -TimeoutSec 10 -ErrorAction Stop)
        $service = $services | Where-Object { $_.name -eq 'Supplier API' -and $_.version -eq '1.0.0' } |
            Select-Object -First 1
        if ($service) { break }
    } catch {
        throw "Microcks service read-back failed after upload: $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 1
} while ([DateTimeOffset]::UtcNow -lt $deadline)

if (-not $service) {
    throw 'Microcks upload returned, but Supplier API version 1.0.0 was not found in /api/services.'
}

[ordered]@{
    selectedMode = $Mode
    artifact = $artifact
    serviceName = $service.name
    serviceVersion = $service.version
    serviceId = $service.id
    operations = if ($null -eq $service.operations) { 0 } else { @($service.operations).Count }
    mockBaseUrl = "$baseUri/rest/Supplier+API/1.0.0/"
    note = 'Service identity was read back; mock/proxy behavior still requires HTTP and origin checks.'
} | ConvertTo-Json -Depth 4
