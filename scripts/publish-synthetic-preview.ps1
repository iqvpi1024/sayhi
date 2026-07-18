[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$Version = "0.1.3",
    [string]$Tag = "v0.1.3-synthetic-preview",
    [string]$OutputDirectory = (Join-Path $PSScriptRoot "..\dist"),
    [switch]$BuildOnly
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
    & (Join-Path $PSScriptRoot "build-portable-preview.ps1") -OutputDirectory $OutputDirectory -Version $Version -Ref $Tag
    if ($LASTEXITCODE -ne 0) { throw "portable preview archive build failed" }

    $archive = Join-Path ([IO.Path]::GetFullPath($OutputDirectory)) "Noetide-synthetic-preview-v$Version.zip"
    $checksums = Join-Path ([IO.Path]::GetFullPath($OutputDirectory)) "SHA256SUMS.txt"
    $portableArchive = Join-Path ([IO.Path]::GetFullPath($OutputDirectory)) "Noetide-synthetic-preview-v$Version-win64.zip"
    $portableChecksums = Join-Path ([IO.Path]::GetFullPath($OutputDirectory)) "SHA256SUMS-$Version-win64.txt"
    $notes = Join-Path $repoRoot "docs\releases\PUBLIC_PREVIEW_V0.1.3_RELEASE_NOTES.md"
    if (-not (Test-Path -LiteralPath $archive) -or -not (Test-Path -LiteralPath $checksums) -or -not (Test-Path -LiteralPath $portableArchive) -or -not (Test-Path -LiteralPath $portableChecksums) -or -not (Test-Path -LiteralPath $notes)) {
        throw "required release files are missing"
    }

    if ($BuildOnly) {
        Write-Output "Built and verified release assets without creating a GitHub Release."
    }
    elseif ($PSCmdlet.ShouldProcess("GitHub release $Tag", "create release and upload verified preview assets")) {
        & $gh.Source release create $Tag $archive $checksums $portableArchive $portableChecksums --title "Noetide v$Version Synthetic Preview" --notes-file $notes --prerelease --verify-tag
        if ($LASTEXITCODE -ne 0) { throw "GitHub Release creation failed" }
    }
    exit 0
}
catch {
    Write-Error "Noetide public preview publication failed: $($_.Exception.Message)"
    exit 1
}
