[CmdletBinding()]
param(
    [string]$DataDirectory
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

try {
    $bundleRoot = Split-Path -Parent $PSScriptRoot
    $runtime = Join-Path $bundleRoot "runtime\python.exe"
    if (-not (Test-Path -LiteralPath $runtime)) { throw "embedded Python runtime is missing" }

    $settingsRoot = Join-Path $env:LOCALAPPDATA "NoetideSyntheticPreview"
    $settingsPath = Join-Path $settingsRoot "data_dir.txt"
    if ([string]::IsNullOrWhiteSpace($DataDirectory)) {
        $defaultDirectory = Join-Path $settingsRoot "data"
        Add-Type -AssemblyName System.Windows.Forms
        $selection = [System.Windows.Forms.MessageBox]::Show(
            "Noetide synthetic preview stores only demo data locally. Use the default data folder?`n$defaultDirectory",
            "Noetide Synthetic Preview",
            [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Information
        )
        if ($selection -eq [System.Windows.Forms.DialogResult]::Yes) {
            $DataDirectory = $defaultDirectory
        }
        else {
            $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
            $dialog.Description = "Choose a local folder for synthetic Noetide demo data"
            $dialog.SelectedPath = $defaultDirectory
            if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
                throw "a local data folder is required"
            }
            $DataDirectory = $dialog.SelectedPath
        }
    }

    $resolvedData = [IO.Path]::GetFullPath($DataDirectory)
    New-Item -ItemType Directory -Force -Path $resolvedData, $settingsRoot | Out-Null
    & $runtime -m noetide_micro --data-dir $resolvedData init
    if ($LASTEXITCODE -ne 0) { throw "synthetic data initialization failed" }
    Set-Content -LiteralPath $settingsPath -Value $resolvedData -Encoding utf8 -NoNewline
    Write-Output "Synthetic preview configured: $resolvedData"
    exit 0
}
catch {
    Write-Error "Noetide synthetic preview setup failed: $($_.Exception.Message)"
    exit 1
}
