param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$errors = [System.Collections.Generic.List[string]]::new()
$checks = [System.Collections.Generic.List[string]]::new()

function Add-Check([string]$message) {
    $script:checks.Add($message)
}

function Add-Error([string]$message) {
    $script:errors.Add($message)
}

function Read-RepoFile([string]$relativePath) {
    return Get-Content -LiteralPath (Join-Path $root $relativePath) -Raw -Encoding UTF8
}

$expectedPrdHash = 'F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC'
$actualPrdHash = (Get-FileHash -LiteralPath (Join-Path $root 'PRDv04.md') -Algorithm SHA256).Hash
if ($actualPrdHash -ne $expectedPrdHash) {
    Add-Error "PRD hash mismatch: $actualPrdHash"
} else {
    Add-Check 'PRD hash matches the immutable v0.4 baseline'
}

$specs = [ordered]@{
    SOM = @{ Path = 'docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md'; Version = '0.3'; Tests = 25; Invariants = 15 }
    BTE = @{ Path = 'docs/specs/02_BITEMPORAL_EVIDENCE_SPEC.md'; Version = '0.3'; Tests = 37; Invariants = 15 }
    CS  = @{ Path = 'docs/specs/03_CHANGESET_CONSISTENCY_SPEC.md'; Version = '0.2'; Tests = 29; Invariants = 14 }
    PAP = @{ Path = 'docs/specs/04_PRIVACY_ACCESS_POLICY_SPEC.md'; Version = '0.2'; Tests = 28; Invariants = 14 }
    SHP = @{ Path = 'docs/specs/05_SHILING_POLICY_SPEC.md'; Version = '0.2'; Tests = 33; Invariants = 13 }
    HTH = @{ Path = 'docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md'; Version = '0.2'; Tests = 23; Invariants = 11 }
    SIP = @{ Path = 'docs/specs/07_STORAGE_INDEX_PORTABILITY_SPEC.md'; Version = '0.2'; Tests = 27; Invariants = 14 }
    MCP = @{ Path = 'docs/specs/08_MCP_CONTRACT_SPEC.md'; Version = '0.2'; Tests = 27; Invariants = 12 }
    IMM = @{ Path = 'docs/specs/09_INGESTION_MIGRATION_SPEC.md'; Version = '0.2'; Tests = 28; Invariants = 15 }
}

$allTestIds = [System.Collections.Generic.HashSet[string]]::new()
$allInvariantIds = [System.Collections.Generic.HashSet[string]]::new()

foreach ($prefix in $specs.Keys) {
    $metadata = $specs[$prefix]
    $fullPath = Join-Path $root $metadata.Path
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        Add-Error "Missing SPEC: $($metadata.Path)"
        continue
    }

    $content = Read-RepoFile $metadata.Path
    $sections = [regex]::Matches($content, '(?m)^## ([0-9]+)\.') | ForEach-Object { [int]$_.Groups[1].Value }
    $sectionDiff = Compare-Object -ReferenceObject (0..21) -DifferenceObject $sections
    if ($sectionDiff) {
        Add-Error "$prefix sections are not exactly 0..21"
    }

    $expectedVersionToken = '| `' + $metadata.Version + '` |'
    if (-not $content.Contains($expectedVersionToken)) {
        Add-Error "$prefix version is not $($metadata.Version)"
    }
    if (-not $content.Contains('| `Approved` |')) {
        Add-Error "$prefix is not Approved"
    }
    foreach ($flag in @('suite_defined=true', 'suite_materialized=false', 'suite_executed=false', 'suite_passed=false')) {
        if (-not $content.Contains($flag)) {
            Add-Error "$prefix missing status flag $flag"
        }
    }
    foreach ($yamlFlag in @('suite_defined: true', 'suite_materialized: false', 'suite_executed: false', 'suite_passed: false')) {
        if (-not [regex]::IsMatch($content, '(?m)^' + [regex]::Escape($yamlFlag) + '$')) {
            Add-Error "$prefix suite block missing $yamlFlag"
        }
    }

    $testPattern = "\b$prefix-AT-[0-9]{3}\b"
    $testIds = [regex]::Matches($content, $testPattern) | ForEach-Object { $_.Value } | Sort-Object -Unique
    $expectedTestIds = 1..$metadata.Tests | ForEach-Object { '{0}-AT-{1:D3}' -f $prefix, $_ }
    if (Compare-Object -ReferenceObject $expectedTestIds -DifferenceObject $testIds) {
        Add-Error "$prefix test IDs are not contiguous 001..$('{0:D3}' -f $metadata.Tests)"
    }
    foreach ($id in $testIds) {
        if (-not $allTestIds.Add($id)) { Add-Error "Duplicate cross-suite test ID: $id" }
    }

    $invariantPattern = "\b$prefix-INV-[0-9]{3}\b"
    $invariantIds = [regex]::Matches($content, $invariantPattern) | ForEach-Object { $_.Value } | Sort-Object -Unique
    $expectedInvariantIds = 1..$metadata.Invariants | ForEach-Object { '{0}-INV-{1:D3}' -f $prefix, $_ }
    if (Compare-Object -ReferenceObject $expectedInvariantIds -DifferenceObject $invariantIds) {
        Add-Error "$prefix invariant IDs are not contiguous 001..$('{0:D3}' -f $metadata.Invariants)"
    }
    foreach ($id in $invariantIds) {
        if (-not $allInvariantIds.Add($id)) { Add-Error "Duplicate cross-suite invariant ID: $id" }
        $occurrences = [regex]::Matches($content, "\b$([regex]::Escape($id))\b").Count
        $suffix = $id.Substring($id.Length - 3)
        $hasCompactCoverage = [regex]::IsMatch($content, "(?:^|[^A-Z0-9-])$suffix(?:[^0-9]|$)")
        if ($occurrences -lt 2 -and -not $hasCompactCoverage) {
            Add-Error "$id has no visible coverage reference"
        }
    }
}

if ($allTestIds.Count -eq 257) {
    Add-Check '257 SPEC acceptance-test IDs are contiguous and unique'
} else {
    Add-Error "Expected 257 unique SPEC test IDs, found $($allTestIds.Count)"
}
if ($allInvariantIds.Count -eq 123) {
    Add-Check '123 invariant IDs are contiguous and have coverage references'
} else {
    Add-Error "Expected 123 unique invariant IDs, found $($allInvariantIds.Count)"
}

$micro = Read-RepoFile 'docs/testing/MICRO_MVP_ACCEPTANCE.md'
$microIds = [regex]::Matches($micro, '\bMM-[0-9]{3}\b') | ForEach-Object { $_.Value } | Sort-Object -Unique
$expectedMicroIds = 1..10 | ForEach-Object { 'MM-{0:D3}' -f $_ }
if (Compare-Object -ReferenceObject $expectedMicroIds -DifferenceObject $microIds) {
    Add-Error 'Micro test IDs are not exactly MM-001..MM-010'
} else {
    Add-Check '10 Micro-MVP scenario IDs are present'
}
foreach ($flag in @('| `suite_materialized` | `false` |', '| `suite_executed` | `false` |', '| `suite_passed` | `false` |')) {
    if (-not $micro.Contains($flag)) { Add-Error "Micro status missing: $flag" }
}

$inlineContentMatch = [regex]::Match($micro, '(?m)^\s+inline_content: "([^"]*)"$')
if (-not $inlineContentMatch.Success) {
    Add-Error 'Micro inline_content is missing or not uniquely parseable'
} else {
    $microBytes = [System.Text.Encoding]::UTF8.GetBytes($inlineContentMatch.Groups[1].Value)
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $microHash = ([BitConverter]::ToString($sha256.ComputeHash($microBytes))).Replace('-', '').ToLowerInvariant()
    } finally {
        $sha256.Dispose()
    }
    if (-not $micro.Contains("content_hash: $microHash")) { Add-Error 'Micro content_hash does not match inline_content' }
    if (-not $micro.Contains("byte_length: $($microBytes.Length)")) { Add-Error 'Micro byte_length does not match inline_content' }
    if (-not $micro.Contains("end_byte_exclusive: $($microBytes.Length)")) { Add-Error 'Micro locator does not cover the full UTF-8 content' }
    Add-Check "Micro UTF-8 locator/hash agree on $($microBytes.Length) bytes"
}

$knownTestIds = [System.Collections.Generic.HashSet[string]]::new()
foreach ($id in $allTestIds) { $null = $knownTestIds.Add($id) }
foreach ($id in $microIds) { $null = $knownTestIds.Add($id) }

$prd = Read-RepoFile 'PRDv04.md'
$matrix = Read-RepoFile 'docs/traceability/REQUIREMENTS_MATRIX.md'
$prdFrs = [regex]::Matches($prd, '\bFR-[0-9]{3}\b') | ForEach-Object { $_.Value } | Sort-Object -Unique
$matrixRows = [regex]::Matches($matrix, '(?m)^\| (FR-[0-9]{3}) \|') | ForEach-Object { $_.Groups[1].Value }
if ($prdFrs.Count -ne 32) { Add-Error "PRD unique FR count is $($prdFrs.Count), expected 32" }
if ($matrixRows.Count -ne 32 -or (Compare-Object -ReferenceObject $prdFrs -DifferenceObject ($matrixRows | Sort-Object -Unique))) {
    Add-Error 'Authoritative matrix rows do not match the 32 PRD FR IDs'
} else {
    Add-Check '32 authoritative FR rows exactly match the PRD'
}

$coverageMatches = [regex]::Matches($matrix, '(?m)^\| FR-[0-9]{3} \| `([^`]+)` \|')
$coverageCounts = @{}
foreach ($match in $coverageMatches) {
    $level = $match.Groups[1].Value
    if (-not $coverageCounts.ContainsKey($level)) { $coverageCounts[$level] = 0 }
    $coverageCounts[$level]++
}
$expectedCoverageCounts = @{
    micro_required_slice = 9
    specified_not_implemented = 8
    boundary_only_deferred = 15
}
foreach ($level in $expectedCoverageCounts.Keys) {
    if ($coverageCounts[$level] -ne $expectedCoverageCounts[$level]) {
        Add-Error "Coverage level $level count is $($coverageCounts[$level]), expected $($expectedCoverageCounts[$level])"
    }
}
foreach ($level in $coverageCounts.Keys) {
    if (-not $expectedCoverageCounts.ContainsKey($level)) { Add-Error "Unknown coverage level: $level" }
}
Add-Check 'FR coverage levels are 9 micro slices, 8 specified, and 15 deferred boundaries'

$matrixTestRefs = [System.Collections.Generic.HashSet[string]]::new()
foreach ($match in [regex]::Matches($matrix, '\b(?:SOM|BTE|CS|PAP|SHP|HTH|SIP|MCP|IMM)-AT-[0-9]{3}\b|\bMM-[0-9]{3}\b')) {
    $null = $matrixTestRefs.Add($match.Value)
}
foreach ($match in [regex]::Matches($matrix, '\b((?:SOM|BTE|CS|PAP|SHP|HTH|SIP|MCP|IMM)-AT-)([0-9]{3}(?:/[0-9]{3})+)')) {
    $prefix = $match.Groups[1].Value
    foreach ($number in $match.Groups[2].Value.Split('/')) { $null = $matrixTestRefs.Add($prefix + $number) }
}
foreach ($match in [regex]::Matches($matrix, '\b(MM-)([0-9]{3}(?:/[0-9]{3})+)')) {
    foreach ($number in $match.Groups[2].Value.Split('/')) { $null = $matrixTestRefs.Add('MM-' + $number) }
}
foreach ($match in [regex]::Matches($matrix, '\b((?:SOM|BTE|CS|PAP|SHP|HTH|SIP|MCP|IMM)-AT-)([0-9]{3})-([0-9]{3})\b')) {
    $start = [int]$match.Groups[2].Value
    $end = [int]$match.Groups[3].Value
    if ($end -lt $start) {
        Add-Error "Descending matrix test range: $($match.Value)"
    } else {
        foreach ($number in $start..$end) { $null = $matrixTestRefs.Add($match.Groups[1].Value + ('{0:D3}' -f $number)) }
    }
}
foreach ($id in $matrixTestRefs) {
    if (-not $knownTestIds.Contains($id)) { Add-Error "Unknown matrix test reference: $id" }
}
Add-Check "$($matrixTestRefs.Count) unique matrix test references resolve"

$knownAliasChecks = [ordered]@{
    'docs must not use source_type' = '\bsource_type\b'
    'docs must not use entity_type' = '\bentity_type\b'
    'docs must not reference PolicyRequest' = '\bPolicyRequest\b'
    'docs must not use single_confirm alias' = '\bsingle_confirm\b'
    'docs must not use double_confirm alias' = '\bdouble_confirm\b'
    'docs must not conflate stored Source with parsing' = 'stored -> parsing'
    'docs must not supersede immutable exported Pack' = 'exported -> superseded'
    'docs must not model trust as State' = 'state\[relationship\.trust\]'
    'docs must not model closeness as State' = 'state\[relationship\.closeness\]'
    'docs must not duplicate sealed sensitivity with seal_state' = '\bseal_state\b'
    'traceability must use micro_required_slice' = '\bmicro_required\b'
}
$authoritativePaths = @(
    'docs/specs',
    'docs/testing/MICRO_MVP_ACCEPTANCE.md',
    'docs/traceability/REQUIREMENTS_MATRIX.md',
    'docs/decisions/OPEN_QUESTIONS.md',
    'docs/PROJECT_STATE.md'
)
$authoritativeDocs = foreach ($relativePath in $authoritativePaths) {
    $fullPath = Join-Path $root $relativePath
    if (Test-Path -LiteralPath $fullPath -PathType Container) {
        Get-ChildItem -LiteralPath $fullPath -Recurse -File -Filter '*.md'
    } else {
        Get-Item -LiteralPath $fullPath
    }
}
foreach ($checkName in $knownAliasChecks.Keys) {
    $pattern = $knownAliasChecks[$checkName]
    $matches = $authoritativeDocs | Select-String -Pattern $pattern -CaseSensitive
    if ($matches) { Add-Error $checkName }
}
if (-not ($knownAliasChecks.Keys | Where-Object { $errors.Contains($_) })) {
    Add-Check 'Known cross-SPEC aliases and conflated state transitions are absent'
}

$markdownFiles = Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.md' |
    Where-Object { $_.FullName -notmatch '[\\/](\.git|node_modules)[\\/]' }
foreach ($file in $markdownFiles) {
    $content = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    $fenceCount = [regex]::Matches($content, '(?m)^```').Count
    if (($fenceCount % 2) -ne 0) { Add-Error "Unpaired Markdown fence: $($file.FullName)" }
}
Add-Check "Markdown fence parity checked for $($markdownFiles.Count) files"

Write-Output 'Noetide specification baseline validation'
Write-Output "Root: $root"
foreach ($check in $checks) { Write-Output "PASS: $check" }
if ($errors.Count -gt 0) {
    foreach ($errorMessage in $errors) { Write-Output "FAIL: $errorMessage" }
    Write-Output "RESULT: FAILED ($($errors.Count) error(s))"
    exit 1
}

Write-Output 'RESULT: PASSED (static contract checks only; no business test was executed)'
exit 0
