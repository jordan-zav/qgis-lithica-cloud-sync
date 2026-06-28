$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Split-Path -Parent $scriptRoot
$source = Join-Path $scriptRoot "lithica_drive_sync"
$artifacts = Join-Path $workspaceRoot "artifacts"
$stagingRoot = Join-Path $artifacts "_qgis_plugin_staging"
$stagingPlugin = Join-Path $stagingRoot "lithica_drive_sync"
$target = Join-Path $artifacts "Lithica Cloud Sync-1.0.0.zip"
$temporaryTarget = Join-Path $artifacts ("Lithica Cloud Sync-" + [guid]::NewGuid().ToString("N") + ".tmp.zip")

$resolvedWorkspace = [System.IO.Path]::GetFullPath($workspaceRoot)
$resolvedStaging = [System.IO.Path]::GetFullPath($stagingRoot)
if (-not $resolvedStaging.StartsWith($resolvedWorkspace, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Staging path is outside the workspace."
}

if (Test-Path -LiteralPath $stagingRoot) {
    Remove-Item -LiteralPath $stagingRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $stagingPlugin -Force | Out-Null

$excludedNames = @("__pycache__", ".pytest_cache")
Get-ChildItem -LiteralPath $source -Recurse -File |
    Where-Object {
        $relative = $_.FullName.Substring($source.Length).TrimStart("\")
        $parts = $relative -split "[\\/]"
        -not ($parts | Where-Object { $excludedNames -contains $_ })
    } |
    ForEach-Object {
        $relative = $_.FullName.Substring($source.Length).TrimStart("\")
        $destination = Join-Path $stagingPlugin $relative
        $parent = Split-Path -Parent $destination
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
        Copy-Item -LiteralPath $_.FullName -Destination $destination
    }

$licenseSource = Join-Path $scriptRoot "LICENSE"
if (Test-Path -LiteralPath $licenseSource) {
    Copy-Item -LiteralPath $licenseSource -Destination (Join-Path $stagingPlugin "LICENSE")
}

$dangerPatterns = @(
    "-----BEGIN PRIVATE KEY-----",
    '"type"\s*:\s*"service_account"',
    "ya29\.[A-Za-z0-9_-]{20,}",
    "1//[A-Za-z0-9_-]{20,}"
)
$findings = Get-ChildItem -LiteralPath $stagingPlugin -Recurse -File |
    Select-String -Pattern $dangerPatterns
if ($findings) {
    throw "Packaging stopped because credential material was detected."
}

$baseTarget = $temporaryTarget.Substring(0, $temporaryTarget.Length - 4)
python -c "import shutil; shutil.make_archive(r'$baseTarget', 'zip', r'$stagingRoot')"

$replaced = $false
for ($attempt = 1; $attempt -le 5 -and -not $replaced; $attempt++) {
    try {
        if (Test-Path -LiteralPath $target) {
            Remove-Item -LiteralPath $target -Force
        }
        Move-Item -LiteralPath $temporaryTarget -Destination $target -Force
        $replaced = $true
    } catch {
        if ($attempt -eq 5) {
            throw
        }
        Start-Sleep -Milliseconds 500
    }
}
Remove-Item -LiteralPath $stagingRoot -Recurse -Force

Write-Output $target
