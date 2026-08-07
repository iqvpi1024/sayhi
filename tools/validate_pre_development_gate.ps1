[CmdletBinding()]
param()

# ============================================================================
# 一次性门禁说明：本脚本把 2026-07-16 恢复点的“开发前置”状态固化为断言
# （无 src/ 业务实现、无依赖清单、无业务结果、Micro manifest 未执行）。
# 它仅对 2026-07-16 恢复点有效；开发启动后预期 RESULT: FAILED，属于设计使然，
# 不代表当前仓库损坏。不要删除或移动本文件——历史文档引用它。
# ============================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$errors = [System.Collections.Generic.List[string]]::new()
$checks = [System.Collections.Generic.List[string]]::new()

function Add-Error([string]$Message) {
    $errors.Add($Message)
}

function Add-Check([string]$Message) {
    $checks.Add($Message)
}

function Read-RepoFile([string]$RelativePath) {
    return Get-Content -LiteralPath (Join-Path $root $RelativePath) -Raw -Encoding UTF8
}

function Invoke-RequiredValidator([string]$RelativePath, [string]$Label) {
    $output = & "$PSHOME\powershell.exe" -ExecutionPolicy Bypass -File (Join-Path $root $RelativePath) 2>&1
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Add-Error "$Label failed (exit $exitCode): $($output -join ' | ')"
    } else {
        Add-Check "$Label passed"
    }
}

Invoke-RequiredValidator 'tools/validate_product_baseline.ps1' 'Product baseline validation'
Invoke-RequiredValidator 'tools/validate_spec_baseline.ps1' 'SPEC and suite-materialization validation'

$requiredFiles = @(
    'docs/adrs/ADR-0001_MICRO_RUNTIME_AND_PERSISTENCE.md',
    'docs/architecture/MICRO_RELATIONSHIP_ARCHITECTURE.md',
    'docs/planning/MICRO_RELATIONSHIP_IMPLEMENTATION_PLAN.md',
    'docs/reviews/MICRO_PRE_ADR_SPEC_CONSISTENCY_REVIEW_2026-07-16.md',
    'docs/testing/MICRO_SUITE_MATERIALIZATION_RESULT_2026-07-16.md',
    'tests/micro_suite_manifest.json',
    'tests/fixtures/micro_relationship_v1/fixture.json',
    'tests/fixtures/micro_relationship_v1/oracles.json',
    'tests/integration/micro_relationship_scenarios.json',
    'tests/semantic/test_micro_relationship_contract.py',
    'tests/runner/adapter_protocol.py',
    'tests/runner/runner_contract.json',
    'tests/runner/run_micro_suite.py'
)
foreach ($relativePath in $requiredFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $relativePath) -PathType Leaf)) {
        Add-Error "Missing pre-development artifact: $relativePath"
    }
}
if (@($requiredFiles | Where-Object {
    -not (Test-Path -LiteralPath (Join-Path $root $_) -PathType Leaf)
}).Count -eq 0) {
    Add-Check "$($requiredFiles.Count) pre-development artifacts are present"
}

$adr = Read-RepoFile 'docs/adrs/ADR-0001_MICRO_RUNTIME_AND_PERSISTENCE.md'
if ($adr -notmatch '(?m)^[|] Status [|] `Accepted` [|]$') {
    Add-Error 'ADR-0001 is not Accepted'
} else {
    Add-Check 'ADR-0001 is Accepted'
}

$plan = Read-RepoFile 'docs/planning/MICRO_RELATIONSHIP_IMPLEMENTATION_PLAN.md'
if ($plan -notmatch '(?m)^[|] Status [|] `Approved` [|]$') {
    Add-Error 'Implementation Plan is not Approved'
}
$taskRows = @([regex]::Matches(
    $plan,
    '(?m)^[|] `TASK-([0-9]{3})` [|].*[|] `(pending|in_progress|blocked|completed)` [|]$'
))
$taskIds = @($taskRows | ForEach-Object { $_.Groups[1].Value })
$taskStates = @($taskRows | ForEach-Object { $_.Groups[2].Value })
$expectedTaskIds = @(1..10 | ForEach-Object { '{0:D3}' -f $_ })
if ($taskRows.Count -ne 10 -or (Compare-Object $expectedTaskIds $taskIds)) {
    Add-Error 'Implementation Plan tasks are not exactly TASK-001..010'
}
if (@($taskStates | Where-Object { $_ -ne 'pending' }).Count -gt 0) {
    Add-Error 'A business implementation task was advanced before the development gate'
}
$plannedModules = @(
    'src/noetide_micro/store.py',
    'src/noetide_micro/intake.py',
    'src/noetide_micro/candidate.py',
    'src/noetide_micro/changesets.py',
    'src/noetide_micro/queries.py',
    'src/noetide_micro/views.py',
    'src/noetide_micro/testing_adapter.py'
)
foreach ($module in $plannedModules) {
    if (-not $plan.Contains($module)) {
        Add-Error "Implementation Plan missing target module: $module"
    }
}
if ($errors.Count -eq 0) {
    Add-Check 'Implementation Plan is Approved with TASK-001..010 pending and seven target modules'
}

$manifestPath = Join-Path $root 'tests/micro_suite_manifest.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (
    $manifest.flags.suite_defined -ne $true -or
    $manifest.flags.suite_materialized -ne $true -or
    $manifest.flags.suite_executed -ne $false -or
    $manifest.flags.suite_passed -ne $false
) {
    Add-Error 'Micro manifest flags are not materialized/not-executed/not-passed'
}
$manifestDigest = (Get-FileHash -Algorithm SHA256 -LiteralPath $manifestPath).Hash.ToLowerInvariant()
if ($manifestDigest -ne '54d70b993dbd5ce117605f6b07c305d2b97eba67df6a782c0e75f3afc28a5390') {
    Add-Error "Micro manifest digest mismatch: $manifestDigest"
} else {
    Add-Check 'Micro manifest digest matches the Approved Implementation Plan'
}

$questionsPath = Join-Path $root 'docs/decisions/OPEN_QUESTIONS.md'
$questionsText = [System.IO.File]::ReadAllText(
    $questionsPath,
    [System.Text.Encoding]::UTF8
)
if (
    -not $questionsText.Contains('blocking=0') -or
    -not $questionsText.Contains('important=0')
) {
    Add-Error 'OPEN_QUESTIONS does not declare blocking=0 and important=0'
} else {
    Add-Check 'Product decision gate has blocking=0 and important=0'
}

if (Test-Path -LiteralPath (Join-Path $root 'src/noetide_micro')) {
    Add-Error 'Business implementation directory exists before the development gate'
} else {
    Add-Check 'No business implementation module exists'
}

$dependencyFiles = @(
    'pyproject.toml',
    'requirements.txt',
    'requirements-dev.txt',
    'poetry.lock',
    'uv.lock',
    'Pipfile',
    'package.json',
    'package-lock.json',
    'pnpm-lock.yaml',
    'yarn.lock'
)
$presentDependencies = @($dependencyFiles | Where-Object {
    Test-Path -LiteralPath (Join-Path $root $_) -PathType Leaf
})
if ($presentDependencies.Count -gt 0) {
    Add-Error "Unexpected dependency/install manifests before development: $($presentDependencies -join ', ')"
} else {
    Add-Check 'No dependency was installed or introduced'
}

$businessResults = @(Get-ChildItem -LiteralPath (Join-Path $root 'docs/testing/results') -File -Filter '*.json')
if ($businessResults.Count -gt 0) {
    Add-Error "Business result artifacts exist before implementation: $($businessResults.Name -join ', ')"
} else {
    Add-Check 'No business Verification Result exists; business status remains not_executed'
}

& git -C $root diff --quiet -- PRDv04.md PRDv05.md
if ($LASTEXITCODE -ne 0) {
    Add-Error 'Current or historical PRD has an uncommitted diff'
} else {
    Add-Check 'PRDv04.md and PRDv05.md have no worktree diff'
}

Write-Output 'Noetide pre-development gate validation'
Write-Output "Root: $root"
foreach ($check in $checks) {
    Write-Output "PASS: $check"
}
if ($errors.Count -gt 0) {
    foreach ($message in $errors) {
        Write-Output "FAIL: $message"
    }
    Write-Output "RESULT: FAILED ($($errors.Count) error(s))"
    exit 1
}

Write-Output 'RESULT: PASSED (development-readiness artifacts only; no business test was executed)'
exit 0
