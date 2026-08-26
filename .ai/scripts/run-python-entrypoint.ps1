[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)][string]$Entrypoint,
    [ValidateSet('human', 'json')][string]$DiagnosticFormat = 'human',
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
)
$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $PSCommandPath
if ($Arguments -and $Arguments[0] -eq '--diagnostic-format=json') {
    $DiagnosticFormat = 'json'
    $Arguments = @($Arguments | Select-Object -Skip 1)
}
$candidate = $null
$activePython = if ($env:VIRTUAL_ENV) { Join-Path $env:VIRTUAL_ENV 'Scripts/python.exe' } else { $null }
foreach ($possible in @($env:AI_CONTEXT_PYTHON, $activePython, 'python', 'python3')) {
    if (-not $possible -or $candidate) { continue }
    $command = Get-Command $possible -ErrorAction SilentlyContinue
    $resolved = if ($command) { $command.Source } else { $possible }
    try {
        & $resolved -B -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>$null
        if ($LASTEXITCODE -eq 0) { $candidate = $resolved }
    } catch { }
}
if (-not $candidate) {
    foreach ($directory in (($env:PATH -split [IO.Path]::PathSeparator) | Where-Object { $_ })) {
        Get-ChildItem -LiteralPath $directory -File -Filter 'python*' -ErrorAction SilentlyContinue |
            Sort-Object Name | ForEach-Object {
                if ($candidate -or $_.Name -notmatch '^python(?:3\.\d+|3\d+|\d{2,3})(?:\.exe)?$') { return }
                try {
                    & $_.FullName -B -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>$null
                    if ($LASTEXITCODE -eq 0) { $candidate = $_.FullName }
                } catch { }
            }
        if ($candidate) { break }
    }
}
if (-not $candidate) {
    $uv = Get-Command uv -ErrorAction SilentlyContinue
    if ($uv) {
        try {
            $candidate = (& $uv.Source python find --managed-python --no-python-downloads --offline --no-config --no-project '>=3.11' 2>$null | Select-Object -First 1).Trim()
        } catch { $candidate = $null }
    }
}
if (-not $candidate) {
    if ($DiagnosticFormat -eq 'json') {
        @{ schema_version = '1.0'; outcome = 'blocked-by-environment'; reason_code = 'no-ready-python'; entrypoint = $Entrypoint; required_python = '>=3.11'; candidates = @(); missing_requirements = @(); requirements_path = (Join-Path (Split-Path -Parent (Split-Path -Parent $scriptDir)) 'requirements.txt'); selected_executable = $null; selected_version = $null; recovery_command = $null; mutation_started = $false } | ConvertTo-Json -Compress
    } else {
        [Console]::Error.WriteLine("Python prerequisite blocked for ${Entrypoint}: no-ready-python. Python >=3.11 is required; see requirements.txt.")
    }
    if ($Entrypoint -eq '.ai/scripts/plan-ai-context-package-apply.py') { exit 2 }
    exit 1
}
$env:AI_CONTEXT_PYTHON = $candidate
& $candidate (Join-Path $scriptDir 'python_prerequisites.py') --entrypoint $Entrypoint --diagnostic-format $DiagnosticFormat --delegate -- @Arguments
exit $LASTEXITCODE
