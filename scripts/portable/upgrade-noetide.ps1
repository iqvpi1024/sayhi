[CmdletBinding()]
param(
    [string]$TargetInstall,
    [switch]$Yes
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Step([string]$Message) { Write-Output "[sayhi Upgrade] $Message" }

try {
    $newBundle = Split-Path -Parent $PSScriptRoot
    $newRuntime = Join-Path $newBundle "runtime\python.exe"
    if (-not (Test-Path -LiteralPath $newRuntime)) { throw "this script must run from inside the new Noetide bundle (runtime missing)" }

    $settingsRoot = Join-Path $env:LOCALAPPDATA "Noetide"
    $settingsPath = Join-Path $settingsRoot "data_dir.txt"
    $dataDirectory = $null
    if (Test-Path -LiteralPath $settingsPath) {
        $dataDirectory = (Get-Content -LiteralPath $settingsPath -Raw).Trim()
    }

    if ([string]::IsNullOrWhiteSpace($TargetInstall)) {
        if ($Yes) { throw "-TargetInstall is required in non-interactive mode" }
        Add-Type -AssemblyName System.Windows.Forms
        $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
        $dialog.Description = "Choose the existing Noetide installation folder to upgrade"
        if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) { throw "upgrade cancelled by user" }
        $TargetInstall = $dialog.SelectedPath
    }
    $target = ([IO.Path]::GetFullPath($TargetInstall)).TrimEnd([char]92)
    if (-not (Test-Path -LiteralPath (Join-Path $target "runtime\python.exe"))) {
        throw "target folder is not a Noetide installation (runtime\python.exe missing): $target"
    }
    $newBundleNorm = ([IO.Path]::GetFullPath($newBundle)).TrimEnd([char]92)
    if ($newBundleNorm -ieq $target) {
        throw "target install must differ from the new bundle folder"
    }

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupRoot = Join-Path $settingsRoot "backups"
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null

    if (-not [string]::IsNullOrWhiteSpace($dataDirectory) -and (Test-Path -LiteralPath $dataDirectory -PathType Container)) {
        $dataBackup = Join-Path $backupRoot "pre-upgrade-data-$timestamp.zip"
        Compress-Archive -LiteralPath $dataDirectory -DestinationPath $dataBackup -Force
        $backupItem = Get-Item -LiteralPath $dataBackup
        if (-not $backupItem -or $backupItem.Length -le 0) { throw "data backup verification failed; upgrade aborted, nothing was changed" }
        Write-Step "data backup verified: $dataBackup ($($backupItem.Length) bytes)"
    }
    else {
        Write-Step "no existing data folder found; continuing with application files only"
    }

    $appBackup = Join-Path $backupRoot "pre-upgrade-app-$timestamp"
    New-Item -ItemType Directory -Force -Path $appBackup | Out-Null
    foreach ($part in @("app", "scripts")) {
        $sourcePart = Join-Path $target $part
        if (Test-Path -LiteralPath $sourcePart) { Copy-Item -Recurse -Force $sourcePart (Join-Path $appBackup $part) }
    }
    $manifestSource = Join-Path $target "RUNTIME_MANIFEST.json"
    if (Test-Path -LiteralPath $manifestSource) { Copy-Item -Force $manifestSource (Join-Path $appBackup "RUNTIME_MANIFEST.json") }
    Write-Step "previous application files preserved: $appBackup"

    foreach ($part in @("runtime", "app", "scripts")) {
        $destinationPart = Join-Path $target $part
        if (Test-Path -LiteralPath $destinationPart) { Remove-Item -LiteralPath $destinationPart -Recurse -Force }
        Copy-Item -Recurse -Force (Join-Path $newBundle $part) $destinationPart
    }
    foreach ($file in @("RUNTIME_MANIFEST.json", "LICENSE", "README.md", "SUPPORT.md")) {
        $sourceFile = Join-Path $newBundle $file
        if (Test-Path -LiteralPath $sourceFile) { Copy-Item -Force $sourceFile $target }
    }
    Write-Step "application files replaced in: $target"

    if (-not [string]::IsNullOrWhiteSpace($dataDirectory) -and (Test-Path -LiteralPath $dataDirectory -PathType Container)) {
        $upgradedRuntime = Join-Path $target "runtime\python.exe"
        & $upgradedRuntime -m noetide_micro --data-dir $dataDirectory status
        if ($LASTEXITCODE -ne 0) {
            Write-Error "upgrade smoke failed: the new version could not read your data. Your data was not modified. Restore the previous application files from $appBackup and keep using the old version, then report this failure."
            exit 1
        }
    }

    Write-Step "upgrade complete. Data folder untouched: $dataDirectory"
    Write-Step "rollback: restore application files from $appBackup; data backups live in $backupRoot"
    exit 0
}
catch {
    Write-Error "Noetide upgrade failed: $($_.Exception.Message). Your data folder was not modified."
    exit 1
}
