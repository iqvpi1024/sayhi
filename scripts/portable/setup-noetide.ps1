[CmdletBinding()]
param(
    [string]$DataDirectory,
    [switch]$Yes
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Step([string]$Message) { Write-Output "[sayhi Setup] $Message" }

try {
    $bundleRoot = Split-Path -Parent $PSScriptRoot
    $runtime = Join-Path $bundleRoot "runtime\python.exe"
    if (-not (Test-Path -LiteralPath $runtime)) { throw "embedded Python runtime is missing; reinstall the Noetide beta bundle" }

    $settingsRoot = Join-Path $env:LOCALAPPDATA "Noetide"
    $settingsPath = Join-Path $settingsRoot "data_dir.txt"
    $privacyPath = Join-Path $settingsRoot "privacy.json"
    $defaultDirectory = Join-Path $settingsRoot "data"

    $ackLocalOnly = $false
    $ackSyntheticOnly = $false
    $ackUnsigned = $false

    if ($Yes) {
        $ackLocalOnly = $true
        $ackSyntheticOnly = $true
        $ackUnsigned = $true
        if ([string]::IsNullOrWhiteSpace($DataDirectory)) { $DataDirectory = $defaultDirectory }
    }
    else {
        Add-Type -AssemblyName System.Windows.Forms
        $notice = [System.Windows.Forms.MessageBox]::Show(
            "Noetide is local-first: your data stays in the folder you choose unless you explicitly enable remote access.`nYou own the data and can export or back it up at any time.`n`nContinue with setup?",
            "Noetide Beta - Privacy",
            [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Information
        )
        if ($notice -ne [System.Windows.Forms.DialogResult]::Yes) { throw "setup cancelled by user" }
        $ackLocalOnly = $true
        $ackSyntheticOnly = $true

        $unsigned = [System.Windows.Forms.MessageBox]::Show(
            "This beta package is not code-signed. Windows SmartScreen may show a warning; this is expected.`nVerify the SHA-256 file shipped with the download if you need integrity assurance.`n`nAcknowledge and continue?",
            "Noetide Beta - Unsigned Package",
            [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Warning
        )
        if ($unsigned -ne [System.Windows.Forms.DialogResult]::Yes) { throw "setup cancelled by user" }
        $ackUnsigned = $true

        if ([string]::IsNullOrWhiteSpace($DataDirectory)) {
            $useDefault = [System.Windows.Forms.MessageBox]::Show(
                "Choose where your Noetide data lives. You own this folder; uninstalling the app never deletes it.`n`nUse the default folder?`n$defaultDirectory",
                "Noetide Beta - Data Folder",
                [System.Windows.Forms.MessageBoxButtons]::YesNo,
                [System.Windows.Forms.MessageBoxIcon]::Question
            )
            if ($useDefault -eq [System.Windows.Forms.DialogResult]::Yes) {
                $DataDirectory = $defaultDirectory
            }
            else {
                $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
                $dialog.Description = "Choose a local folder you own for Noetide data"
                $dialog.SelectedPath = $defaultDirectory
                if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) { throw "a local data folder is required" }
                $DataDirectory = $dialog.SelectedPath
            }
        }
    }

    $resolvedData = [IO.Path]::GetFullPath($DataDirectory)
    $resolvedLower = $resolvedData.TrimEnd('\').ToLowerInvariant()
    $bundleLower = ([IO.Path]::GetFullPath($bundleRoot)).TrimEnd('\').ToLowerInvariant()
    if ($resolvedLower -eq $bundleLower -or $resolvedLower.StartsWith($bundleLower + '\')) {
        throw "the data folder must be outside the application folder so upgrades and uninstalls can never touch it"
    }
    New-Item -ItemType Directory -Force -Path $resolvedData, $settingsRoot | Out-Null
    if (-not (Test-Path -LiteralPath $resolvedData -PathType Container)) { throw "data folder is not writable: $resolvedData" }

    & $runtime -m noetide_micro --data-dir $resolvedData product-init
    if ($LASTEXITCODE -ne 0) { throw "data initialization failed; the existing folder was not modified - pick an empty folder or restore from a backup" }

    $privacy = [ordered]@{
        schema_version = "noetide.privacy.v1"
        chosen_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        data_directory = $resolvedData
        acknowledged_local_only = $ackLocalOnly
        acknowledged_synthetic_only = $false
        acknowledged_unsigned = $ackUnsigned
    }
    ($privacy | ConvertTo-Json -Depth 4) | Set-Content -LiteralPath $privacyPath -Encoding utf8
    Set-Content -LiteralPath $settingsPath -Value $resolvedData -Encoding utf8 -NoNewline

    Write-Step "data folder: $resolvedData"
    Write-Step "privacy choices recorded: $privacyPath"
    # 健康检查走产品层 NoetideApp:`status` 命令面向 demo fixture 库,对
    # product-init 的数据库会误报 SeedConflictError(2026-08-08 实测确认)
    & $runtime -c "from noetide_micro.product import NoetideApp; app = NoetideApp(r'$resolvedData'); app.overview(); app.close()"
    if ($LASTEXITCODE -ne 0) { throw "health check failed after setup" }
    Write-Step "setup complete. Use 'sayhi Start.cmd' to open the web management UI, or 'sayhi Shell.cmd' for command line."
    exit 0
}
catch {
    Write-Error "Noetide setup failed: $($_.Exception.Message)"
    exit 1
}
