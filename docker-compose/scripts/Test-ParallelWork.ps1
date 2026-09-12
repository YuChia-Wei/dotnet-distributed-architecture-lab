param(
    [string]$ProjectName = 'mqarchlab-pr5-integration',
    [string]$BaseUri = 'http://localhost:8888',
    [string]$OutputPath = 'artifacts/nuget-consumer/compose-parallel-e2e.json'
)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$composeFiles = @('-p', $ProjectName, '-f', "$repoRoot/docker-compose/docker-compose.yml", '-f', "$repoRoot/docker-compose/docker-compose.override.yml", '-f', "$repoRoot/docker-compose/docker-compose.verification.yml")
$results = @()
foreach ($mode in @('WhenAll', 'IndependentHandlers')) {
    $startedAt = [DateTimeOffset]::UtcNow.ToString('o')
    $response = Invoke-RestMethod -Method Post -Uri "$BaseUri/api/products/diagnostics/parallel-work/$mode" -TimeoutSec 20
    $probeId = $response.probeId
    if (!$probeId) { throw 'Publication did not return a probe identifier.' }
    $deadline = [DateTimeOffset]::UtcNow.AddSeconds(30)
    do {
        $logs = @(& docker compose @composeFiles logs --no-color --since $startedAt orders-consumer 2>&1 | ForEach-Object { "$_" } | Where-Object { $_.Contains($probeId) })
        if ($LASTEXITCODE -ne 0) { throw 'Could not read consumer logs.' }
        $completed = @($logs | Where-Object { $_ -match 'completed.*applied=True' })
        if ($completed.Count -ge 2) { break }
        Start-Sleep -Milliseconds 300
    } while ([DateTimeOffset]::UtcNow -lt $deadline)
    if ($completed.Count -ne 2) { throw "$mode did not complete both work items." }
    $starts = @($logs | Where-Object { $_ -match 'started in scope' })
    if ($starts.Count -ne 2) { throw "$mode did not start exactly two work items." }
    $scopeIds = @($starts | ForEach-Object { [regex]::Match($_, 'scope ([0-9a-f-]+)').Groups[1].Value } | Select-Object -Unique)
    if ($scopeIds.Count -ne 2) { throw "$mode shared its branch scope." }
    $firstCompletion = [Array]::IndexOf($logs, $completed[0])
    if ([Array]::IndexOf($logs, $starts[0]) -ge $firstCompletion -or [Array]::IndexOf($logs, $starts[1]) -ge $firstCompletion) { throw "$mode did not overlap." }
    $replayStart = [DateTimeOffset]::UtcNow.ToString('o')
    $null = Invoke-RestMethod -Method Post -Uri "$BaseUri/api/products/diagnostics/parallel-work/$mode`?probeId=$probeId" -TimeoutSec 20
    $deadline = [DateTimeOffset]::UtcNow.AddSeconds(30)
    do {
        $replay = @(& docker compose @composeFiles logs --no-color --since $replayStart orders-consumer 2>&1 | ForEach-Object { "$_" } | Where-Object { $_.Contains($probeId) -and $_ -match 'completed.*applied=False' })
        if ($LASTEXITCODE -ne 0) { throw 'Could not read replay logs.' }
        if ($replay.Count -ge 2) { break }
        Start-Sleep -Milliseconds 300
    } while ([DateTimeOffset]::UtcNow -lt $deadline)
    if ($replay.Count -ne 2) { throw "$mode replay did not deduplicate both effects." }
    $results += [ordered]@{ mode = $mode; probeId = $probeId; topic = $response.topic; consumer = $response.consumer; scopeIds = $scopeIds; overlap = $true; replayDeduplicated = $true; execution = $logs; replay = $replay }
}
$resolvedOutput = Join-Path $repoRoot $OutputPath
$null = New-Item -ItemType Directory -Force (Split-Path $resolvedOutput)
[ordered]@{ project = $ProjectName; observedAt = [DateTimeOffset]::UtcNow.ToString('o'); outcome = 'passed'; results = $results } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resolvedOutput -Encoding utf8
Write-Output "Compose parallel E2E passed: $resolvedOutput"
