[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$Version = "0.1.1",
    [string]$Tag = "v0.1.1-synthetic-preview",
    [string]$OutputDirectory = (Join-Path $PSScriptRoot "..\dist")
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

try {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    $gh = Get-Command gh -ErrorAction Stop
    & $gh.Source auth status
    if ($LASTEXITCODE -ne 0) { throw "GitHub CLI authentication is required" }

    & (Join-Path $PSScriptRoot "build-public-preview.ps1") -OutputDirectory $OutputDirectory -Version $Version -Ref $Tag
    if ($LASTEXITCODE -ne 0) { throw "preview archive build failed" }

    $archive = Join-Path ([IO.Path]::GetFullPath($OutputDirectory)) "Noetide-synthetic-preview-v$Version.zip"
    $checksums = Join-Path ([IO.Path]::GetFullPath($OutputDirectory)) "SHA256SUMS.txt"
    $notes = Join-Path $repoRoot "docs\releases\PUBLIC_PREVIEW_V0.1.1_RELEASE_NOTES.md"
    if (-not (Test-Path -LiteralPath $archive) -or -not (Test-Path -LiteralPath $checksums) -or -not (Test-Path -LiteralPath $notes)) {
        throw "required release files are missing"
    }

    if ($PSCmdlet.ShouldProcess("GitHub release $Tag", "create release and upload verified preview assets")) {
        & $gh.Source release create $Tag $archive $checksums --title "Noetide v$Version Synthetic Preview" --notes-file $notes --verify-tag
        if ($LASTEXITCODE -ne 0) { throw "GitHub Release creation failed" }
    }
    exit 0
}
catch {
    Write-Error "Noetide public preview publication failed: $($_.Exception.Message)"
    exit 1
}
