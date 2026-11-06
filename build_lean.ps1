# ==============================================================================
# Automated Lean 4.35.0 Proof Compiler & Strict Axiom Allowlist Validator
# ==============================================================================

$ErrorActionPreference = "Stop"

$leanBin = "$env:USERPROFILE\.elan\bin\lean.exe"
if (-not (Test-Path $leanBin)) {
    $leanBin = "lean"
}

Write-Host "=== Compiling Hilbert-Zermelo-Erdos Hand Proof in Lean 4 ===" -ForegroundColor Cyan
Push-Location (Join-Path $PSScriptRoot "lean4")
try {
    & $leanBin --version
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $output = & $leanBin "Connect5HandProof.lean" 2>&1
    $exitCode = $LASTEXITCODE
    $sw.Stop()
} finally {
    Pop-Location
}

$output | ForEach-Object { Write-Host $_ }

if ($exitCode -ne 0) {
    Write-Error "Lean 4 verification failed with exit code $exitCode"
    exit $exitCode
}

$allowedAxioms = @("propext", "Quot.sound")
$axiomReports = 0
foreach ($line in $output) {
    $s = $line.ToString()
    if ($s -match "^'([^']+)' does not depend on any axioms$") {
        $axiomReports++
    } elseif ($s -match "^'([^']+)' depends on axioms: \[([^\]]+)\]$") {
        $axiomReports++
        $thm = $Matches[1]
        $axs = $Matches[2].Split(",") | ForEach-Object { $_.Trim() }
        foreach ($ax in $axs) {
            if ($allowedAxioms -notcontains $ax) {
                Write-Error "Disallowed axiom '$ax' in theorem '$thm'! Only [propext, Quot.sound] are permitted."
                exit 1
            }
        }
    }
}

if ($axiomReports -ne 14) {
    Write-Error "Expected 14 #print axioms reports from Connect5HandProof.lean, got $axiomReports"
    exit 1
}

Write-Host ""
Write-Host ("All $axiomReports/14 analytic Hilbert-Erdos & Central Wall theorems verified in Lean 4 ({0:N2}s) with ZERO sorrys, ZERO custom axioms, and ZERO Classical.choice!" -f $sw.Elapsed.TotalSeconds) -ForegroundColor Green

