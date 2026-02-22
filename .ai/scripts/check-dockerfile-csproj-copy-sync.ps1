param(
    [string]$SrcRoot = "src",
    [switch]$FailOnMismatch
)

$ErrorActionPreference = "Stop"

function Normalize-PathStyle {
    param([string]$PathText)
    return $PathText.Replace("\", "/").TrimStart("/")
}

function Resolve-ToFullPath {
    param(
        [string]$BasePath,
        [string]$RelativePath
    )
    $normalized = $RelativePath.Replace("/", "\")
    return [System.IO.Path]::GetFullPath((Join-Path $BasePath $normalized))
}

function Get-ProjectReferencesRecursive {
    param(
        [string]$ProjectPath,
        [hashtable]$Visited
    )

    $fullProjectPath = [System.IO.Path]::GetFullPath($ProjectPath)
    if ($Visited.ContainsKey($fullProjectPath)) {
        return @()
    }
    $Visited[$fullProjectPath] = $true

    [xml]$xml = Get-Content -Path $fullProjectPath
    $references = @()
    foreach ($node in @($xml.Project.ItemGroup.ProjectReference)) {
        if (-not $node) { continue }
        $include = $node.Include
        if ([string]::IsNullOrWhiteSpace($include)) { continue }

        $childProjectPath = [System.IO.Path]::GetFullPath((Join-Path (Split-Path $fullProjectPath -Parent) $include))
        if (Test-Path $childProjectPath) {
            $references += $childProjectPath
            $references += Get-ProjectReferencesRecursive -ProjectPath $childProjectPath -Visited $Visited
        }
    }

    return $references
}

function Get-PathRelativeToSrcRoot {
    param(
        [string]$FullPath,
        [string]$FullSrcRoot
    )
    $resolved = [System.IO.Path]::GetFullPath($FullPath)
    if ($resolved.StartsWith($FullSrcRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        $relative = $resolved.Substring($FullSrcRoot.Length).TrimStart([char]92, [char]47)
        return $relative
    }
    return $resolved
}

$fullSrcRoot = (Resolve-Path $SrcRoot).Path
$dockerfiles = Get-ChildItem -Path $SrcRoot -Recurse -Filter Dockerfile | Sort-Object FullName

if (-not $dockerfiles) {
    Write-Host "No Dockerfile found under '$SrcRoot'."
    exit 0
}

$hasMismatch = $false

foreach ($dockerfile in $dockerfiles) {
    $lines = Get-Content -Path $dockerfile.FullName

    $restoreLine = $lines | Where-Object { $_ -match '^RUN\s+dotnet restore\s+"([^"]+\.csproj)"' } | Select-Object -First 1
    if (-not $restoreLine) {
        Write-Host ""
        Write-Host "[SKIP] $($dockerfile.FullName) (no dotnet restore line)"
        continue
    }

    $restoreProject = [regex]::Match($restoreLine, '^RUN\s+dotnet restore\s+"([^"]+\.csproj)"').Groups[1].Value
    $entryProjectFull = Resolve-ToFullPath -BasePath $fullSrcRoot -RelativePath $restoreProject
    if (-not (Test-Path $entryProjectFull)) {
        Write-Host ""
        Write-Host "[ERROR] $($dockerfile.FullName)"
        Write-Host "  Restore project not found: $restoreProject"
        $hasMismatch = $true
        continue
    }

    $copyProjectLines = $lines | Where-Object { $_ -match '^COPY\s+\["([^"]+\.csproj)",' }
    $copiedProjectFullSet = @()
    foreach ($copyLine in $copyProjectLines) {
        $copySource = [regex]::Match($copyLine, '^COPY\s+\["([^"]+\.csproj)",').Groups[1].Value
        if ($copySource.StartsWith("src/")) {
            $copySource = $copySource.Substring(4)
        }
        $copiedProjectFullSet += Resolve-ToFullPath -BasePath $fullSrcRoot -RelativePath $copySource
    }
    $copiedProjectFullSet = $copiedProjectFullSet | Sort-Object -Unique

    $visited = @{}
    $requiredProjects = @($entryProjectFull) + (Get-ProjectReferencesRecursive -ProjectPath $entryProjectFull -Visited $visited)
    $requiredProjects = $requiredProjects | Sort-Object -Unique

    $missingProjects = @($requiredProjects | Where-Object { $copiedProjectFullSet -notcontains $_ })
    $extraProjects = @($copiedProjectFullSet | Where-Object { $requiredProjects -notcontains $_ })

    Write-Host ""
    Write-Host "[CHECK] $($dockerfile.FullName)"

    if ($missingProjects.Count -eq 0 -and $extraProjects.Count -eq 0) {
        Write-Host "  MATCH"
        continue
    }

    $hasMismatch = $true
    if ($missingProjects.Count -gt 0) {
        Write-Host "  Missing csproj COPY:"
        foreach ($missing in $missingProjects) {
            $relativeMissing = Get-PathRelativeToSrcRoot -FullPath $missing -FullSrcRoot $fullSrcRoot
            Write-Host "  - $relativeMissing"
        }

        Write-Host "  Suggested COPY lines:"
        foreach ($missing in $missingProjects) {
            $relativeMissing = Normalize-PathStyle (Get-PathRelativeToSrcRoot -FullPath $missing -FullSrcRoot $fullSrcRoot)
            $targetDir = [System.IO.Path]::GetDirectoryName($relativeMissing).Replace("\", "/")
            if (-not [string]::IsNullOrWhiteSpace($targetDir)) {
                $targetDir = $targetDir + "/"
            }
            Write-Host "  COPY [""src/$relativeMissing"", ""$targetDir""]"
        }
    }

    if ($extraProjects.Count -gt 0) {
        Write-Host "  Extra csproj COPY (not required by ProjectReference graph):"
        foreach ($extra in $extraProjects) {
            $relativeExtra = Get-PathRelativeToSrcRoot -FullPath $extra -FullSrcRoot $fullSrcRoot
            Write-Host "  - $relativeExtra"
        }
    }
}

Write-Host ""
if ($hasMismatch) {
    Write-Host "Result: MISMATCH"
    if ($FailOnMismatch) {
        exit 2
    }
    exit 0
}

Write-Host "Result: MATCH"
exit 0
