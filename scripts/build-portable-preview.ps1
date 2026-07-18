[CmdletBinding()]
param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot "..\dist"),
    [string]$Version = "0.1.2",
    [string]$Ref = "HEAD",
    [string]$RuntimeCache = (Join-Path $env:TEMP "noetide-python-3.12.10-embed-amd64.zip")
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$runtimeUrl = "https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip"
$runtimeSha256 = "4acbed6dd1c744b0376e3b1cf57ce906f9dc9e95e68824584c8099a63025a3c3"

try {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    $git = Get-Command git -ErrorAction Stop
    $outputPath = [IO.Path]::GetFullPath($OutputDirectory)
    New-Item -ItemType Directory -Force -Path $outputPath | Out-Null
    if (-not (Test-Path -LiteralPath $RuntimeCache)) {
        Invoke-WebRequest -Uri $runtimeUrl -OutFile $RuntimeCache
    }
    $actualRuntimeHash = (Get-FileHash -LiteralPath $RuntimeCache -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualRuntimeHash -ne $runtimeSha256) { throw "embedded Python runtime SHA-256 mismatch" }

    $stageRoot = Join-Path $env:TEMP ("noetide-portable-" + [Guid]::NewGuid().ToString("N"))
    $bundleName = "Noetide-synthetic-preview-v$Version-win64"
    $bundleRoot = Join-Path $stageRoot $bundleName
    try {
        New-Item -ItemType Directory -Force -Path $stageRoot | Out-Null
        $sourceArchive = Join-Path $stageRoot "source.zip"
        $sourceRoot = Join-Path $stageRoot "source"
        & $git.Source -C $repoRoot archive --format=zip --output=$sourceArchive $Ref -- src/noetide_micro LICENSE README.md SUPPORT.md scripts/portable
        if ($LASTEXITCODE -ne 0) { throw "git archive source snapshot failed" }
        Expand-Archive -LiteralPath $sourceArchive -DestinationPath $sourceRoot -Force
        New-Item -ItemType Directory -Force -Path $bundleRoot | Out-Null
        Expand-Archive -LiteralPath $RuntimeCache -DestinationPath (Join-Path $bundleRoot "runtime") -Force
        Set-Content -LiteralPath (Join-Path $bundleRoot "runtime\python312._pth") -Value "python312.zip`r`n.`r`n..\app\src`r`n" -Encoding ascii
        New-Item -ItemType Directory -Force -Path (Join-Path $bundleRoot "app\src"), (Join-Path $bundleRoot "scripts") | Out-Null
        Copy-Item -Recurse -Force (Join-Path $sourceRoot "src\noetide_micro") (Join-Path $bundleRoot "app\src\noetide_micro")
        Copy-Item -Force (Join-Path $sourceRoot "LICENSE"), (Join-Path $sourceRoot "README.md"), (Join-Path $sourceRoot "SUPPORT.md") $bundleRoot
        Copy-Item -Force (Join-Path $sourceRoot "scripts\portable\setup-synthetic-preview.ps1") (Join-Path $bundleRoot "scripts")
        Copy-Item -Force (Join-Path $sourceRoot "scripts\portable\Noetide Console.cmd") (Join-Path $bundleRoot "scripts")
        Copy-Item -Force (Join-Path $sourceRoot "scripts\portable\Noetide Start.cmd") (Join-Path $bundleRoot "scripts")
        $manifest = @{ schema_version = "noetide.portable-preview.v1"; version = $Version; source_ref = $Ref; runtime = @{ version = "3.12.10"; source_url = $runtimeUrl; sha256 = $runtimeSha256 }; synthetic_only = $true; real_personal_data_supported = $false }
        $manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $bundleRoot "RUNTIME_MANIFEST.json") -Encoding utf8
        $archivePath = Join-Path $outputPath "$bundleName.zip"
        Remove-Item -LiteralPath $archivePath -Force -ErrorAction SilentlyContinue
        Compress-Archive -LiteralPath $bundleRoot -DestinationPath $archivePath -Force
        $archiveHash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
        Set-Content -LiteralPath (Join-Path $outputPath "SHA256SUMS-$Version-win64.txt") -Value "$archiveHash  $bundleName.zip" -Encoding ascii -NoNewline
        Write-Output "Built self-contained portable preview: $archivePath"
    }
    finally {
        Remove-Item -LiteralPath $stageRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    exit 0
}
catch {
    Write-Error "Noetide portable preview build failed: $($_.Exception.Message)"
    exit 1
}
