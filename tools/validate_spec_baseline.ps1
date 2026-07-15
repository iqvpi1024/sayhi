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

function Normalize-Newlines([string]$content) {
    return $content.Replace("`r`n", "`n").Replace("`r", "`n")
}

function Read-RepoFile([string]$relativePath) {
    $content = Get-Content -LiteralPath (Join-Path $root $relativePath) -Raw -Encoding UTF8
    return Normalize-Newlines $content
}

function Get-Sha256Hex([byte[]]$bytes) {
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($sha256.ComputeHash($bytes))).Replace('-', '').ToUpperInvariant()
    } finally {
        $sha256.Dispose()
    }
}

function Get-CanonicalTextHash([string]$relativePath) {
    $encoding = [System.Text.UTF8Encoding]::new($false)
    return Get-Sha256Hex $encoding.GetBytes((Read-RepoFile $relativePath))
}

function Expand-LocalTestRefs([string]$text, [string]$prefix) {
    $refs = [System.Collections.Generic.HashSet[string]]::new()

    foreach ($match in [regex]::Matches($text, "\b$prefix-AT-[0-9]{3}\b")) {
        $null = $refs.Add($match.Value)
    }

    foreach ($match in [regex]::Matches($text, '\bAT(?<list>[0-9]{3}(?:-[0-9]{3})?(?:/[0-9]{3}(?:-[0-9]{3})?)*)\b')) {
        foreach ($segment in $match.Groups['list'].Value.Split('/')) {
            if ($segment -match '^([0-9]{3})-([0-9]{3})$') {
                $start = [int]$Matches[1]
                $end = [int]$Matches[2]
                if ($end -lt $start) {
                    Add-Error "Descending invariant coverage range for ${prefix}: AT$segment"
                    continue
                }
                foreach ($number in $start..$end) {
                    $null = $refs.Add(('{0}-AT-{1:D3}' -f $prefix, $number))
                }
            } else {
                $null = $refs.Add("$prefix-AT-$segment")
            }
        }
    }

    return $refs
}

function Assert-ClosedEnum([string]$relativePath, [string]$fieldName, [string[]]$expectedValues) {
    $content = Read-RepoFile $relativePath
    $pattern = '(?m)^\s*' + [regex]::Escape($fieldName) + ':\s*\[([^\]]*)\]\s*$'
    $matches = [regex]::Matches($content, $pattern)
    if ($matches.Count -ne 1) {
        Add-Error "Closed enum $fieldName must have exactly one machine-readable declaration in $relativePath"
        return
    }

    $actualValues = @($matches[0].Groups[1].Value.Split(',') | ForEach-Object { $_.Trim() })
    $actualUnique = @($actualValues | Sort-Object -Unique)
    $expectedUnique = @($expectedValues | Sort-Object -Unique)
    if ($actualValues.Count -ne $actualUnique.Count -or (Compare-Object -ReferenceObject $expectedUnique -DifferenceObject $actualUnique)) {
        Add-Error "Closed enum $fieldName differs from its expected positive set in $relativePath"
    }
}

function Validate-MicroTextBlock([string]$label, [string]$block) {
    $inlineMatch = [regex]::Match($block, '(?m)^\s+inline_content: "([^"]*)"$')
    if (-not $inlineMatch.Success) {
        Add-Error "$label inline_content is missing or not parseable"
        return
    }

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($inlineMatch.Groups[1].Value)
    $hash = (Get-Sha256Hex $bytes).ToLowerInvariant()
    if (-not $block.Contains("content_hash: $hash")) { Add-Error "$label content_hash does not match inline_content" }
    if (-not $block.Contains("byte_length: $($bytes.Length)")) { Add-Error "$label byte_length does not match inline_content" }
    if (-not $block.Contains("end_byte_exclusive: $($bytes.Length)")) { Add-Error "$label locator does not cover the full UTF-8 content" }
    Add-Check "$label UTF-8 locator/hash agree on $($bytes.Length) bytes"
}

$expectedPreviousPrdHash = 'F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC'
$expectedCurrentPrdHash = '34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7'
$actualPreviousPrdHash = Get-CanonicalTextHash 'PRDv04.md'
$actualCurrentPrdHash = Get-CanonicalTextHash 'PRDv05.md'
if ($actualPreviousPrdHash -ne $expectedPreviousPrdHash) {
    $rawHash = (Get-FileHash -LiteralPath (Join-Path $root 'PRDv04.md') -Algorithm SHA256).Hash
    Add-Error "Historical PRD v0.4 canonical LF hash mismatch: canonical=$actualPreviousPrdHash raw=$rawHash"
} else {
    Add-Check 'Historical PRD v0.4 canonical LF hash remains immutable'
}
if ($actualCurrentPrdHash -ne $expectedCurrentPrdHash) {
    $rawHash = (Get-FileHash -LiteralPath (Join-Path $root 'PRDv05.md') -Algorithm SHA256).Hash
    Add-Error "Current PRD v0.5 canonical LF hash mismatch: canonical=$actualCurrentPrdHash raw=$rawHash"
} else {
    Add-Check 'Current PRD v0.5 canonical LF hash matches the approved product baseline'
}
$productIndex = Read-RepoFile 'docs/product/CURRENT_PRODUCT_BASELINE.md'
foreach ($requiredIndexValue in @(
    'current_prd_path: PRDv05.md',
    "current_prd_canonical_lf_sha256: $expectedCurrentPrdHash",
    'previous_prd_path: PRDv04.md',
    "previous_prd_canonical_lf_sha256: $expectedPreviousPrdHash"
)) {
    if (-not $productIndex.Contains($requiredIndexValue)) {
        Add-Error "Product baseline index missing or stale: $requiredIndexValue"
    }
}
Add-Check 'Product baseline index points to PRD v0.5 and protects v0.4 history'

$attributes = Read-RepoFile '.gitattributes'
foreach ($requiredAttribute in @('.gitattributes text eol=lf', '*.md text eol=lf', '*.ps1 text eol=lf', '*.yaml text eol=lf', '*.yml text eol=lf')) {
    if (-not ($attributes -split "`n" | Where-Object { $_ -eq $requiredAttribute })) {
        Add-Error ".gitattributes missing: $requiredAttribute"
    }
}
Add-Check 'Repository text EOL policy is explicit'

$workflowRequiredFiles = @(
    'AGENTS.md',
    'docs/process/README.md',
    'docs/process/CHANGE_CONTROL.md',
    'docs/architecture/README.md',
    'docs/adrs/README.md',
    'docs/adrs/ADR_TEMPLATE.md',
    'docs/planning/README.md',
    'docs/planning/IMPLEMENTATION_PLAN_TEMPLATE.md',
    'docs/testing/README.md',
    'docs/testing/SUITE_MATERIALIZATION_CHECKLIST.md',
    'docs/testing/VERIFICATION_RESULT_TEMPLATE.md',
    'docs/testing/results/README.md',
    'docs/reviews/README.md',
    'docs/reviews/GATE_REVIEW_TEMPLATE.md',
    'docs/releases/README.md',
    'docs/releases/RECOVERY_POINT_TEMPLATE.md',
    'tests/README.md',
    'tests/fixtures/README.md',
    'tests/semantic/README.md',
    'tests/integration/README.md'
)
$workflowErrorsBefore = $errors.Count
foreach ($relativePath in $workflowRequiredFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $relativePath) -PathType Leaf)) {
        Add-Error "Missing workflow foundation file: $relativePath"
    }
}
if ($errors.Count -eq $workflowErrorsBefore) {
    Add-Check "$($workflowRequiredFiles.Count) workflow foundation files are present"
}

$specs = [ordered]@{
    SOM = @{ Path = 'docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md'; Version = '0.5'; Tests = 28; Invariants = 16 }
    BTE = @{ Path = 'docs/specs/02_BITEMPORAL_EVIDENCE_SPEC.md'; Version = '0.4'; Tests = 38; Invariants = 16 }
    CS  = @{ Path = 'docs/specs/03_CHANGESET_CONSISTENCY_SPEC.md'; Version = '0.4'; Tests = 32; Invariants = 16 }
    PAP = @{ Path = 'docs/specs/04_PRIVACY_ACCESS_POLICY_SPEC.md'; Version = '0.4'; Tests = 31; Invariants = 16 }
    SHP = @{ Path = 'docs/specs/05_SHILING_POLICY_SPEC.md'; Version = '0.4'; Tests = 34; Invariants = 14 }
    HTH = @{ Path = 'docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md'; Version = '0.4'; Tests = 27; Invariants = 12 }
    SIP = @{ Path = 'docs/specs/07_STORAGE_INDEX_PORTABILITY_SPEC.md'; Version = '0.3'; Tests = 27; Invariants = 14 }
    MCP = @{ Path = 'docs/specs/08_MCP_CONTRACT_SPEC.md'; Version = '0.3'; Tests = 27; Invariants = 12 }
    IMM = @{ Path = 'docs/specs/09_INGESTION_MIGRATION_SPEC.md'; Version = '0.4'; Tests = 31; Invariants = 17 }
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
    $sections = @([regex]::Matches($content, '(?m)^## ([0-9]+)\.') | ForEach-Object { [int]$_.Groups[1].Value })
    if ($sections.Count -ne 22 -or (Compare-Object -ReferenceObject (0..21) -DifferenceObject $sections)) {
        Add-Error "$prefix sections are not exactly 0..21"
    }

    $versionPattern = '(?m)^\| [^|\r\n]+ \| `' + [regex]::Escape([string]$metadata.Version) + '` \|$'
    if (-not [regex]::IsMatch($content, $versionPattern)) {
        Add-Error "$prefix version is not $($metadata.Version)"
    }
    if (-not [regex]::IsMatch($content, '(?m)^\| [^|\r\n]+ \| `Approved` \|$')) {
        Add-Error "$prefix is not Approved"
    }
    $hasCurrentProductBaseline = $content.Contains('`PRDv05.md`') -and $content.Contains('PRD v0.5')
    $hasHistoricalProductReference = $content.Contains('PRDv04.md')
    if (($hasCurrentProductBaseline -eq $false) -or ($hasHistoricalProductReference -eq $true)) {
        Add-Error "$prefix does not bind exclusively to the current PRD v0.5 baseline"
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
    $testIds = @([regex]::Matches($content, $testPattern) | ForEach-Object { $_.Value } | Sort-Object -Unique)
    $expectedTestIds = @(1..$metadata.Tests | ForEach-Object { '{0}-AT-{1:D3}' -f $prefix, $_ })
    if (Compare-Object -ReferenceObject $expectedTestIds -DifferenceObject $testIds) {
        Add-Error "$prefix test IDs are not contiguous 001..$('{0:D3}' -f $metadata.Tests)"
    }
    foreach ($id in $testIds) {
        if (-not $allTestIds.Add($id)) { Add-Error "Duplicate cross-suite test ID: $id" }
    }

    $invariantPattern = "\b$prefix-INV-[0-9]{3}\b"
    $invariantIds = @([regex]::Matches($content, $invariantPattern) | ForEach-Object { $_.Value } | Sort-Object -Unique)
    $expectedInvariantIds = @(1..$metadata.Invariants | ForEach-Object { '{0}-INV-{1:D3}' -f $prefix, $_ })
    if (Compare-Object -ReferenceObject $expectedInvariantIds -DifferenceObject $invariantIds) {
        Add-Error "$prefix invariant IDs are not contiguous 001..$('{0:D3}' -f $metadata.Invariants)"
    }
    foreach ($id in $invariantIds) {
        if (-not $allInvariantIds.Add($id)) { Add-Error "Duplicate cross-suite invariant ID: $id" }
    }

    $section19Match = [regex]::Match($content, '(?ms)^## 19\..*?(?=^## 20\.)')
    if (-not $section19Match.Success) {
        Add-Error "$prefix has no parseable section 19 coverage region"
        continue
    }
    $coverageRegion = $section19Match.Value
    $knownLocalTests = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($testId in $testIds) { $null = $knownLocalTests.Add($testId) }

    $coverageMap = @{}
    $tableCoveragePattern = '(?m)^\|\s*`?(?<id>' + $prefix + '-INV-[0-9]{3})`?\s*\|\s*(?<refs>.*?)\s*\|$'
    foreach ($mapping in [regex]::Matches($coverageRegion, $tableCoveragePattern)) {
        $coverageMap[$mapping.Groups['id'].Value] = $mapping.Groups['refs'].Value
    }
    $compactCoverageLine = [regex]::Match($coverageRegion, '(?m)^(?<body>[^\r\n]*001\s*\u2192\s*AT[^\r\n]*)$')
    if ($compactCoverageLine.Success) {
        foreach ($segment in $compactCoverageLine.Groups['body'].Value.Split([char]0xFF1B)) {
            $trimmedSegment = $segment.Trim().TrimEnd([char]0x3002, [char]0x002E)
            $segmentMatch = [regex]::Match($trimmedSegment, '^[^0-9]*(?<suffix>[0-9]{3})\s*\u2192\s*(?<refs>.+)$')
            if ($segmentMatch.Success) {
                $coverageMap[('{0}-INV-{1}' -f $prefix, $segmentMatch.Groups['suffix'].Value)] = $segmentMatch.Groups['refs'].Value
            }
        }
    }

    foreach ($id in $invariantIds) {
        if (-not $coverageMap.ContainsKey($id) -or [string]::IsNullOrWhiteSpace([string]$coverageMap[$id])) {
            Add-Error "$id has no structured coverage mapping in section 19"
            continue
        }

        $mappingText = [string]$coverageMap[$id]
        if ($mappingText -notmatch '(?:^|[^A-Z])(?:[A-Z]+-)?AT') {
            $mappingText = 'AT' + $mappingText
        }

        $mappedTests = @(Expand-LocalTestRefs $mappingText $prefix)
        if ($mappedTests.Count -eq 0) {
            Add-Error "$id coverage mapping contains no acceptance-test reference"
            continue
        }
        foreach ($mappedTest in $mappedTests) {
            if (-not $knownLocalTests.Contains($mappedTest)) {
                Add-Error "$id maps to unknown local test: $mappedTest"
            }
        }
    }
}

if ($allTestIds.Count -eq 275) {
    Add-Check '275 SPEC acceptance-test IDs are contiguous and unique'
} else {
    Add-Error "Expected 275 unique SPEC test IDs, found $($allTestIds.Count)"
}
if ($allInvariantIds.Count -eq 133) {
    Add-Check '133 invariant IDs are contiguous and structurally mapped to existing tests'
} else {
    Add-Error "Expected 133 unique invariant IDs, found $($allInvariantIds.Count)"
}

$micro = Read-RepoFile 'docs/testing/MICRO_MVP_ACCEPTANCE.md'
$microIds = @([regex]::Matches($micro, '\bMM-[0-9]{3}\b') | ForEach-Object { $_.Value } | Sort-Object -Unique)
$expectedMicroIds = @(1..10 | ForEach-Object { 'MM-{0:D3}' -f $_ })
if (Compare-Object -ReferenceObject $expectedMicroIds -DifferenceObject $microIds) {
    Add-Error 'Micro test IDs are not exactly MM-001..MM-010'
} else {
    Add-Check '10 Micro-MVP scenario IDs are present'
}
foreach ($flag in @('| `suite_materialized` | `false` |', '| `suite_executed` | `false` |', '| `suite_passed` | `false` |')) {
    if (-not $micro.Contains($flag)) { Add-Error "Micro status missing: $flag" }
}

$primarySourceMatch = [regex]::Match($micro, '(?ms)^intake_request:.*?(?=^historical_source_fixture:)')
$historicalSourceMatch = [regex]::Match($micro, '(?ms)^historical_source_fixture:.*?(?=^```\s*$)')
if (-not $primarySourceMatch.Success) {
    Add-Error 'Micro primary Source block is missing'
} else {
    Validate-MicroTextBlock 'Micro primary Source' $primarySourceMatch.Value
}
if (-not $historicalSourceMatch.Success) {
    Add-Error 'Micro historical Source block is missing'
} else {
    Validate-MicroTextBlock 'Micro historical Source' $historicalSourceMatch.Value
}

$knownTestIds = [System.Collections.Generic.HashSet[string]]::new()
foreach ($id in $allTestIds) { $null = $knownTestIds.Add($id) }
foreach ($id in $microIds) { $null = $knownTestIds.Add($id) }

$requiredBlock = [regex]::Match($micro, '(?ms)^micro_required_contract_slices:\s*\n(?<rows>.*?)(?=^```\s*$)')
if (-not $requiredBlock.Success) {
    Add-Error 'Micro required contract-slice mapping is missing or not parseable'
} else {
    $requiredRows = [regex]::Matches($requiredBlock.Groups['rows'].Value, '(?m)^\s{2}(MM-[0-9]{3}):\s*\[([^\]]+)\]\s*$')
    $requiredKeys = @($requiredRows | ForEach-Object { $_.Groups[1].Value })
    if ($requiredRows.Count -ne 10 -or (Compare-Object -ReferenceObject $expectedMicroIds -DifferenceObject ($requiredKeys | Sort-Object -Unique))) {
        Add-Error 'Micro required contract-slice mapping must contain MM-001..MM-010 exactly once'
    }

    $requiredUpstreamRefs = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($row in $requiredRows) {
        $refs = @($row.Groups[2].Value.Split(',') | ForEach-Object { $_.Trim() })
        if ($refs.Count -eq 0) { Add-Error "$($row.Groups[1].Value) has no required upstream test" }
        foreach ($ref in $refs) {
            if ($ref -notmatch '^(SOM|BTE|CS|PAP|SHP|IMM)-AT-[0-9]{3}$') {
                Add-Error "Invalid or deferred Micro upstream test reference: $ref"
                continue
            }
            if (-not $knownTestIds.Contains($ref)) { Add-Error "Unknown Micro upstream test reference: $ref" }
            $null = $requiredUpstreamRefs.Add($ref)
        }
    }
    Add-Check "Micro required mapping covers 10 scenarios and $($requiredUpstreamRefs.Count) unique upstream tests"
}

$prd = Read-RepoFile 'PRDv05.md'
$matrix = Read-RepoFile 'docs/traceability/REQUIREMENTS_MATRIX.md'
$prdFrs = @([regex]::Matches($prd, '\bFR-[0-9]{3}\b') | ForEach-Object { $_.Value } | Sort-Object -Unique)
$matrixRowMatches = [regex]::Matches($matrix, '(?m)^\| (FR-[0-9]{3}) \|')
$matrixRows = @($matrixRowMatches | ForEach-Object { $_.Groups[1].Value })
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
foreach ($match in [regex]::Matches($matrix, '`?((?:SOM|BTE|CS|PAP|SHP|HTH|SIP|MCP|IMM)-AT-)([0-9]{3})`?\s*\u81F3\s*`?(?:(?:SOM|BTE|CS|PAP|SHP|HTH|SIP|MCP|IMM)-AT-)?([0-9]{3})`?')) {
    $start = [int]$match.Groups[2].Value
    $end = [int]$match.Groups[3].Value
    if ($end -lt $start) {
        Add-Error "Descending matrix Chinese test range: $($match.Value)"
    } else {
        foreach ($number in $start..$end) { $null = $matrixTestRefs.Add($match.Groups[1].Value + ('{0:D3}' -f $number)) }
    }
}
foreach ($id in $matrixTestRefs) {
    if (-not $knownTestIds.Contains($id)) { Add-Error "Unknown matrix test reference: $id" }
}
Add-Check "$($matrixTestRefs.Count) unique matrix test references resolve"

$enumErrorsBefore = $errors.Count
Assert-ClosedEnum 'docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md' 'source_append_status_values' @('received', 'validating', 'stored', 'duplicate', 'rejected')
Assert-ClosedEnum 'docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md' 'changeset_status_values' @('proposed', 'reviewing', 'approved', 'rejected', 'publishing', 'published', 'conflicted', 'failed', 'reverted')
Assert-ClosedEnum 'docs/specs/02_BITEMPORAL_EVIDENCE_SPEC.md' 'canonical_unknown_answer_status_values' @('unknown')
Assert-ClosedEnum 'docs/specs/03_CHANGESET_CONSISTENCY_SPEC.md' 'changeset_status_values' @('proposed', 'reviewing', 'approved', 'rejected', 'publishing', 'published', 'conflicted', 'failed', 'reverted')
Assert-ClosedEnum 'docs/specs/03_CHANGESET_CONSISTENCY_SPEC.md' 'preflight_result_values' @('passed', 'conflict', 'failed')
Assert-ClosedEnum 'docs/specs/03_CHANGESET_CONSISTENCY_SPEC.md' 'proposal_operation_values' @('add', 'correct', 'end', 'merge', 'split', 'archive', 'unarchive', 'seal', 'unseal', 'soft_delete', 'restore', 'hard_delete')
Assert-ClosedEnum 'docs/specs/04_PRIVACY_ACCESS_POLICY_SPEC.md' 'third_party_present_values' @('true', 'false', 'unknown')
Assert-ClosedEnum 'docs/specs/04_PRIVACY_ACCESS_POLICY_SPEC.md' 'source_policy_resolution_status_values' @('declared', 'provisional', 'confirmed')
Assert-ClosedEnum 'docs/specs/04_PRIVACY_ACCESS_POLICY_SPEC.md' 'privacy_lifecycle_action_values' @('archive', 'unarchive', 'seal', 'unseal', 'soft_delete', 'restore', 'hard_delete')
Assert-ClosedEnum 'docs/specs/05_SHILING_POLICY_SPEC.md' 'current_automatic_publish_scope_values' @('deterministic_source_receipt_metadata')
Assert-ClosedEnum 'docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md' 'individual_test_result_values' @('passed', 'failed', 'errored', 'skipped_with_reason')
Assert-ClosedEnum 'docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md' 'run_result_values' @('passed', 'failed', 'errored', 'partial')
Assert-ClosedEnum 'docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md' 'suite_artifact_state_values' @('absent', 'materialized', 'superseded')
Assert-ClosedEnum 'docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md' 'applicability_status_values' @('current', 'superseded', 'not_applicable')
Assert-ClosedEnum 'docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md' 'verification_result_values' @('not_executed', 'passed', 'failed', 'errored', 'partial')
Assert-ClosedEnum 'docs/specs/08_MCP_CONTRACT_SPEC.md' 'irreversible_fact_answer_status_values' @('verified')
Assert-ClosedEnum 'docs/specs/09_INGESTION_MIGRATION_SPEC.md' 'intake_status_values' @('received', 'validating', 'stored', 'duplicate', 'rejected')
Assert-ClosedEnum 'docs/specs/09_INGESTION_MIGRATION_SPEC.md' 'append_receipt_status_values' @('stored', 'duplicate', 'rejected')
Assert-ClosedEnum 'docs/specs/09_INGESTION_MIGRATION_SPEC.md' 'parse_attempt_status_values' @('queued', 'parsing', 'parsed', 'candidate_ready', 'no_candidate', 'parse_failed', 'unsupported')
Assert-ClosedEnum 'docs/process/README.md' 'delivery_phase_values' @('product_defined', 'product_decided', 'spec_approved', 'traceable', 'architecture_decided', 'suite_materialized', 'implementation_planned', 'implementing', 'verified', 'review_passed', 'recovery_point_published')
if ($errors.Count -eq $enumErrorsBefore) {
    Add-Check '20 closed enums match positive machine-readable value sets'
}

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
    'AGENTS.md',
    'docs/product',
    'docs/specs',
    'docs/testing/MICRO_MVP_ACCEPTANCE.md',
    'docs/process',
    'docs/architecture',
    'docs/adrs',
    'docs/planning',
    'docs/releases',
    'docs/traceability/REQUIREMENTS_MATRIX.md',
    'docs/decisions/OPEN_QUESTIONS.md',
    'docs/reviews/PRD_V05_SPEC_COMPATIBILITY_REVIEW.md',
    'docs/PROJECT_STATE.md',
    'tests'
)
$authoritativeDocs = foreach ($relativePath in $authoritativePaths) {
    $fullPath = Join-Path $root $relativePath
    if (Test-Path -LiteralPath $fullPath -PathType Container) {
        Get-ChildItem -LiteralPath $fullPath -Recurse -File -Filter '*.md'
    } else {
        Get-Item -LiteralPath $fullPath
    }
}
$aliasErrorsBefore = $errors.Count
foreach ($checkName in $knownAliasChecks.Keys) {
    $pattern = $knownAliasChecks[$checkName]
    $matches = $authoritativeDocs | Select-String -Pattern $pattern -CaseSensitive
    if ($matches) { Add-Error $checkName }
}
if ($errors.Count -eq $aliasErrorsBefore) {
    Add-Check 'Known cross-SPEC aliases and conflated state transitions are absent'
}

$privacyFiles = @(
    Get-Item -LiteralPath (Join-Path $root 'AGENTS.md')
    Get-Item -LiteralPath (Join-Path $root 'PRDv04.md')
    Get-Item -LiteralPath (Join-Path $root 'PRDv05.md')
    Get-Item -LiteralPath (Join-Path $root 'docs/product/CURRENT_PRODUCT_BASELINE.md')
    Get-Item -LiteralPath (Join-Path $root 'docs/reviews/PRD_V05_SPEC_COMPATIBILITY_REVIEW.md')
    Get-ChildItem -LiteralPath (Join-Path $root 'docs/specs') -Recurse -File -Filter '*.md'
    Get-ChildItem -LiteralPath (Join-Path $root 'docs/testing') -Recurse -File -Filter '*.md'
    Get-ChildItem -LiteralPath (Join-Path $root 'docs/process') -Recurse -File -Filter '*.md'
    Get-ChildItem -LiteralPath (Join-Path $root 'docs/architecture') -Recurse -File -Filter '*.md'
    Get-ChildItem -LiteralPath (Join-Path $root 'docs/adrs') -Recurse -File -Filter '*.md'
    Get-ChildItem -LiteralPath (Join-Path $root 'docs/planning') -Recurse -File -Filter '*.md'
    Get-ChildItem -LiteralPath (Join-Path $root 'docs/releases') -Recurse -File -Filter '*.md'
    Get-ChildItem -LiteralPath (Join-Path $root 'docs/traceability') -Recurse -File -Filter '*.md'
    Get-ChildItem -LiteralPath (Join-Path $root 'docs/decisions') -Recurse -File -Filter '*.md'
    Get-ChildItem -LiteralPath (Join-Path $root 'tests') -Recurse -File -Filter '*.md'
    Get-Item -LiteralPath (Join-Path $root 'docs/PROJECT_STATE.md')
)
$privacyPatterns = [ordered]@{
    'mainland mobile-like number' = '(?<![0-9])1[3-9][0-9]{9}(?![0-9])'
    'email-like address' = '(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'
    'local user-directory path' = '(?i)(?:[A-Z]:\\Users\\[^\\\s]+|/home/[^/\s]+|/Users/[^/\s]+)'
}
$privacyErrorsBefore = $errors.Count
foreach ($file in $privacyFiles | Sort-Object -Property FullName -Unique) {
    $content = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    foreach ($patternName in $privacyPatterns.Keys) {
        if ([regex]::IsMatch($content, $privacyPatterns[$patternName])) {
            $relative = $file.FullName.Substring($root.Length).TrimStart('\', '/')
            Add-Error "Privacy heuristic '$patternName' matched in $relative"
        }
    }
}
if ($errors.Count -eq $privacyErrorsBefore) {
    Add-Check "Privacy heuristic scanned $($privacyFiles.Count) authoritative contract/test files"
}

$markdownFiles = Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.md' |
    Where-Object { $_.FullName -notmatch '[\\/](\.git|node_modules)[\\/]' }
foreach ($file in $markdownFiles) {
    $content = Normalize-Newlines (Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8)
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
