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
    $wheelPath = Join-Path $installPath "wheel"
    New-Item -ItemType Directory -Force -Path $wheelPath | Out-Null
    & $python.Source -m pip wheel --no-deps --no-build-isolation --wheel-dir $wheelPath $repoRoot
    if ($LASTEXITCODE -ne 0) { throw "local wheel build failed" }
    $wheel = Get-ChildItem -LiteralPath $wheelPath -Filter "noetide-*.whl" | Select-Object -First 1
    if ($null -eq $wheel) { throw "local wheel build produced no Noetide wheel" }
    & $venvPython -m pip install --no-deps $wheel.FullName
    if ($LASTEXITCODE -ne 0) { throw "isolated wheel installation failed" }
    & $venvPython -m noetide_micro --data-dir $dataPath init
    if ($LASTEXITCODE -ne 0) { throw "module smoke check failed" }
    & (Join-Path $venvPath "Scripts\noetide.exe") --data-dir $dataPath status
    if ($LASTEXITCODE -ne 0) { throw "console smoke check failed" }
    Write-Output "Synthetic local demo is ready: $dataPath"
    exit 0
}
catch {
    Write-Error "Noetide synthetic demo setup failed: $($_.Exception.Message)"
    exit 1
}
