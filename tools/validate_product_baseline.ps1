param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$errors = [System.Collections.Generic.List[string]]::new()
$checks = [System.Collections.Generic.List[string]]::new()

function Add-Check([string]$message) { $script:checks.Add($message) }
function Add-Error([string]$message) { $script:errors.Add($message) }
function Normalize-Newlines([string]$content) { $content.Replace("`r`n", "`n").Replace("`r", "`n") }
function Read-RepoFile([string]$relativePath) {
    Normalize-Newlines (Get-Content -LiteralPath (Join-Path $root $relativePath) -Raw -Encoding UTF8)
}
function Get-Sha256Hex([string]$content) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($content)
        ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToUpperInvariant()
    } finally { $sha.Dispose() }
}
function Assert-Contains([string]$content, [string]$expected, [string]$message) {
    if (-not $content.Contains($expected)) { Add-Error $message }
}
function Assert-ClosedEnum([string]$content, [string]$field, [string[]]$expected) {
    $pattern = '(?m)^' + [regex]::Escape($field) + ':\s*\[([^\]]*)\]\s*$'
    $matches = [regex]::Matches($content, $pattern)
    if ($matches.Count -ne 1) {
        Add-Error "$field must have exactly one machine-readable declaration"
        return
    }
    $actual = @($matches[0].Groups[1].Value.Split(',') | ForEach-Object { $_.Trim() } | Sort-Object -Unique)
    $wanted = @($expected | Sort-Object -Unique)
    if (Compare-Object -ReferenceObject $wanted -DifferenceObject $actual) {
        Add-Error "$field differs from approved values"
    }
}

$v04 = Read-RepoFile 'PRDv04.md'
$v05 = Read-RepoFile 'PRDv05.md'
$index = Read-RepoFile 'docs/product/CURRENT_PRODUCT_BASELINE.md'
$questions = Read-RepoFile 'docs/decisions/OPEN_QUESTIONS.md'

$expectedV04 = 'F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC'
$expectedV05 = '34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7'
if ((Get-Sha256Hex $v04) -ne $expectedV04) { Add-Error 'PRDv04 immutable canonical hash changed' }
if ((Get-Sha256Hex $v05) -ne $expectedV05) { Add-Error 'PRDv05 approved canonical hash changed' }
if ($errors.Count -eq 0) { Add-Check 'PRD v0.4 immutable and v0.5 approved hashes match' }

foreach ($line in @(
    'current_prd_path: PRDv05.md',
    'current_prd_version: 0.5',
    'current_prd_status: approved',
    "current_prd_canonical_lf_sha256: $expectedV05",
    'previous_prd_path: PRDv04.md',
    'previous_prd_status: superseded_read_only',
    'approval_decision: DEC-PRD-V05-001'
)) { Assert-Contains $index $line "Product baseline index missing: $line" }
Add-Check 'Product baseline index points to PRD v0.5 and preserves v0.4'

foreach ($line in @(
    '> PRD v0.5 · Personal Context & Growth Engine',
    '| 文档状态 | Approved Product Baseline |',
    '| 版本 | 0.5 |',
    '| 日期 | 2026-07-15 |'
)) { Assert-Contains $v05 $line "PRDv05 metadata missing: $line" }

$sections = @([regex]::Matches($v05, '(?m)^# ([0-9]+)\.') | ForEach-Object { [int]$_.Groups[1].Value })
if ($sections.Count -ne 27 -or (Compare-Object -ReferenceObject (1..27) -DifferenceObject $sections)) {
    Add-Error 'PRDv05 top-level sections are not exactly 1..27'
} else { Add-Check 'PRDv05 top-level sections are exactly 1..27' }

$v04Frs = @([regex]::Matches($v04, '\bFR-[0-9]{3}\b') | ForEach-Object { $_.Value } | Sort-Object -Unique)
$v05Frs = @([regex]::Matches($v05, '\bFR-[0-9]{3}\b') | ForEach-Object { $_.Value } | Sort-Object -Unique)
if ($v05Frs.Count -ne 32 -or (Compare-Object -ReferenceObject $v04Frs -DifferenceObject $v05Frs)) {
    Add-Error 'PRDv05 FR set differs from the 32-item v0.4 set'
} else { Add-Check 'PRDv05 preserves all 32 FR IDs without expansion' }

$objectSection = [regex]::Match($v05, '(?ms)^# 8\..*?(?=^## 8\.1)').Value
$expectedObjects = @('Source','Entity','Episode','Assertion','Relationship','State','Hypothesis','Goal','Commitment','Decision','Outcome','ChangeSet')
$objectRows = @([regex]::Matches($objectSection, '(?m)^\| (' + ($expectedObjects -join '|') + ') \|') | ForEach-Object { $_.Groups[1].Value })
if ($objectRows.Count -ne 12 -or (Compare-Object -ReferenceObject $expectedObjects -DifferenceObject ($objectRows | Sort-Object -Unique))) {
    Add-Error 'PRDv05 core object table is not the approved 12-object set'
} else { Add-Check 'PRDv05 core object set is exactly 12' }

Assert-ClosedEnum $v05 'assertion_kind_values' @('observed','reported','quoted','opinion','inferred','analysis','predicted','fictional')
Assert-ClosedEnum $v05 'answer_status_values' @('verified','unconfirmed','disputed','not_covered','stale','unknown')
Add-Check 'Assertion kind and Answer Status positive sets are closed'

foreach ($requiredText in @(
    'Micro-MVP 不实现整张 MVP 白名单。它的 Core View 封闭集合只有 `person_card` 与 `relationship_timeline`',
    '原始 Source 使用独立、可审计的 append receipt 快速保存',
    '撤销通过新的补偿 ChangeSet 和新 revision 表达',
    '`suite_materialized`',
    'PRD -> SPEC -> Acceptance Test 追踪完整'
)) { Assert-Contains $v05 $requiredText "PRDv05 missing approved product boundary: $requiredText" }

$stalePatterns = [ordered]@{
    'five-state heading' = '(?m)^## 9\.4 五态'
    'FR-008 five-state wording' = '(?m)^- FR-008：.*五态'
    'old revert pointer wording' = '撤销后恢复原 revision'
    'old SPEC order preface' = 'PRD v0\.4 批准后，依次编写'
    'draft status' = '\| 文档状态 \| Draft for Review \|'
}
foreach ($name in $stalePatterns.Keys) {
    if ([regex]::IsMatch($v05, $stalePatterns[$name])) { Add-Error "PRDv05 retains stale wording: $name" }
}
Add-Check 'Known v0.4 contradictory wording is absent from PRDv05'

$dqIds = @([regex]::Matches($questions, '(?m)^\| (DQ-[0-9]{3}) \|') | ForEach-Object { $_.Groups[1].Value })
$expectedDq = @(1..13 | ForEach-Object { 'DQ-{0:D3}' -f $_ })
if ($dqIds.Count -ne 13 -or (Compare-Object -ReferenceObject $expectedDq -DifferenceObject ($dqIds | Sort-Object -Unique))) {
    Add-Error 'OPEN_QUESTIONS does not contain DQ-001..013 exactly once'
} else { Add-Check 'Deferred product queue contains DQ-001..013 exactly once' }

$privacyPatterns = [ordered]@{
    'mainland mobile-like number' = '(?<![0-9])1[3-9][0-9]{9}(?![0-9])'
    'email-like address' = '(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'
    'local user-directory path' = '(?i)(?:[A-Z]:\\Users\\[^\\\s]+|/home/[^/\s]+|/Users/[^/\s]+)'
}
foreach ($name in $privacyPatterns.Keys) {
    if ([regex]::IsMatch($v05, $privacyPatterns[$name])) { Add-Error "PRDv05 privacy heuristic matched: $name" }
}
Add-Check 'PRDv05 privacy heuristics found no configured pattern'

$fenceCount = [regex]::Matches($v05, '(?m)^```').Count
if (($fenceCount % 2) -ne 0) { Add-Error 'PRDv05 has unpaired Markdown fences' }
else { Add-Check 'PRDv05 Markdown fence parity is valid' }

Write-Output 'Noetide product baseline validation'
Write-Output "Root: $root"
foreach ($check in $checks) { Write-Output "PASS: $check" }
if ($errors.Count -gt 0) {
    foreach ($errorMessage in $errors) { Write-Output "FAIL: $errorMessage" }
    Write-Output "RESULT: FAILED ($($errors.Count) error(s))"
    exit 1
}
Write-Output 'RESULT: PASSED (product baseline static checks only; no SPEC compatibility or business test was executed)'
exit 0
