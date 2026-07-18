[CmdletBinding()]
param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot "..\dist"),
    [string]$Version = "0.1.0",
    [string]$Ref = "HEAD"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

try {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    $git = Get-Command git -ErrorAction Stop
    $outputPath = [IO.Path]::GetFullPath($OutputDirectory)
    New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

    $archiveName = "Noetide-synthetic-preview-v$Version.zip"
    $archivePath = Join-Path $outputPath $archiveName
    Remove-Item -LiteralPath $archivePath -Force -ErrorAction SilentlyContinue
    & $git.Source -C $repoRoot archive --format=zip --prefix="Noetide-synthetic-preview-v$Version/" --output=$archivePath $Ref
    if ($LASTEXITCODE -ne 0) { throw "git archive failed" }

    $hash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
    Set-Content -LiteralPath (Join-Path $outputPath "SHA256SUMS.txt") -Value "$hash  $archiveName" -Encoding ascii -NoNewline
    Write-Output "Built synthetic preview archive: $archivePath"
    exit 0
}
catch {
    Write-Error "Noetide public preview build failed: $($_.Exception.Message)"
    exit 1
}
