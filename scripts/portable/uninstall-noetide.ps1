[CmdletBinding()]
param(
    [string]$InstallRoot,
    [switch]$Yes,
    [switch]$DeleteData,
    [string]$ConfirmPath
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Step([string]$Message) { Write-Output "[Noetide Uninstall] $Message" }

try {
    if ([string]::IsNullOrWhiteSpace($InstallRoot)) { throw "-InstallRoot is required" }
    $install = ([IO.Path]::GetFullPath($InstallRoot)).TrimEnd([char]92)
    if (-not (Test-Path -LiteralPath (Join-Path $install "runtime\python.exe"))) {
        throw "install folder is not a Noetide installation (runtime\python.exe missing): $install"
    }

    $settingsRoot = Join-Path $env:LOCALAPPDATA "Noetide"
    $settingsPath = Join-Path $settingsRoot "data_dir.txt"
    $dataDirectory = $null
    if (Test-Path -LiteralPath $settingsPath) {
        $dataDirectory = (Get-Content -LiteralPath $settingsPath -Raw).Trim()
    }

    Write-Step "default behavior: only the application folder is removed. Your data stays on this computer."
    if (-not [string]::IsNullOrWhiteSpace($dataDirectory)) {
        Write-Step "data folder preserved at: $dataDirectory"
    }

    if ($DeleteData) {
        if ([string]::IsNullOrWhiteSpace($dataDirectory) -or -not (Test-Path -LiteralPath $dataDirectory -PathType Container)) {
            throw "-DeleteData requested but no existing data folder was found"
        }
        $resolvedData = ([IO.Path]::GetFullPath($dataDirectory)).TrimEnd([char]92)
        if ([string]::IsNullOrWhiteSpace($ConfirmPath)) {
            if ($Yes) { throw "-DeleteData in non-interactive mode requires -ConfirmPath with the full data folder path" }
            Write-Output "Type the full data folder path to confirm permanent deletion: $resolvedData"
            $ConfirmPath = Read-Host "Confirm path"
        }
        if (([IO.Path]::GetFullPath($ConfirmPath)).TrimEnd([char]92) -ine $resolvedData) {
            throw "confirmation path does not match the data folder; deletion refused, nothing was deleted"
        }

        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $backupRoot = Join-Path $settingsRoot "backups"
        New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
        $backupDest = Join-Path $backupRoot "pre-uninstall-$timestamp"
        $runtime = Join-Path $install "runtime\python.exe"
        Write-Step "creating a verified export backup before deletion: $backupDest"
        & $runtime -m noetide_micro --data-dir $resolvedData backup $backupDest
        if ($LASTEXITCODE -ne 0) { throw "backup failed; deletion refused, your data was not touched" }
        $packPath = $backupDest
        if (-not (Test-Path -LiteralPath (Join-Path $backupDest "manifest.json")) -or -not (Test-Path -LiteralPath (Join-Path $backupDest "checksums.sha256"))) { throw "backup pack missing after backup; deletion refused" }

        & $runtime -m noetide_micro --data-dir $resolvedData uninstall-info --confirm-delete --backup $packPath
        if ($LASTEXITCODE -ne 0) { throw "engine refused deletion; your data was not touched" }
        Write-Step "data folder deleted by engine; verified backup kept at $packPath"
    }

    if (-not $Yes) {
        Add-Type -AssemblyName System.Windows.Forms
        $message = "Remove the Noetide application folder? " + $install + [Environment]::NewLine + [Environment]::NewLine + "Your data folder and backups are kept."
        $go = [System.Windows.Forms.MessageBox]::Show(
            $message,
            "Noetide Uninstall",
            [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Question
        )
        if ($go -ne [System.Windows.Forms.DialogResult]::Yes) { throw "uninstall cancelled by user" }
    }

    Remove-Item -LiteralPath $install -Recurse -Force
    Write-Step "application folder removed: $install"
    if (-not $DeleteData) {
        Write-Step "to also delete data later, run uninstall with -DeleteData and confirm the full path; a verified backup is created first."
    }
    exit 0
}
catch {
    Write-Error "Noetide uninstall failed: $($_.Exception.Message)"
    exit 1
}
