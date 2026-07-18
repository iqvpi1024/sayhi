[CmdletBinding()]
param(
    [string]$InstallRoot = (Join-Path $PSScriptRoot "..\.noetide-demo"),
    [switch]$Recreate
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

try {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    $python = Get-Command python -ErrorAction Stop
    $version = & $python.Source -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ([version]$version -lt [version]"3.12") {
        throw "Python 3.12 or newer is required; found $version."
    }

    $installPath = [IO.Path]::GetFullPath($InstallRoot)
    $venvPath = Join-Path $installPath ".venv"
    $dataPath = Join-Path $installPath "synthetic-data"
    if ($Recreate -and (Test-Path -LiteralPath $installPath)) {
        Remove-Item -LiteralPath $installPath -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $installPath | Out-Null
    if (-not (Test-Path -LiteralPath $venvPath)) {
        & $python.Source -m venv $venvPath
    }
    $venvPython = Join-Path $venvPath "Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $venvPython)) {
        throw "virtual environment creation failed"
    }
    $sourcePath = Join-Path $repoRoot "src"
    if (-not (Test-Path -LiteralPath (Join-Path $sourcePath "noetide_micro"))) {
        throw "source package is missing"
    }
    $launcherPath = Join-Path $installPath "noetide.cmd"
    Set-Content -LiteralPath $launcherPath -Value "@echo off`r`n`"$venvPython`" -m noetide_micro %*" -Encoding ascii
    $previousPythonPath = $env:PYTHONPATH
    try {
        $env:PYTHONPATH = $sourcePath
        & $venvPython -m noetide_micro --data-dir $dataPath init
        if ($LASTEXITCODE -ne 0) { throw "module smoke check failed" }
        & $launcherPath --data-dir $dataPath status
        if ($LASTEXITCODE -ne 0) { throw "launcher smoke check failed" }
    }
    finally {
        $env:PYTHONPATH = $previousPythonPath
    }
    Write-Output "Synthetic local demo is ready: $dataPath"
    exit 0
}
catch {
    Write-Error "Noetide synthetic demo setup failed: $($_.Exception.Message)"
    exit 1
}
