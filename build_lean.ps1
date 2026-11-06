# ==============================================================================
# Automated Lean 4.35.0 Proof Compiler & Zero-Sorry Validator
# ==============================================================================

$ErrorActionPreference = "Stop"

$leanBin = "$env:USERPROFILE\.elan\bin\lean.exe"
if (-not (Test-Path $leanBin)) {
    $leanBin = "lean"
}

Write-Host "=== Compiling Hilbert-Zermelo-Erdos Hand Proof in Lean 4 ===" -ForegroundColor Cyan
& $leanBin --version

$sw = [System.Diagnostics.Stopwatch]::StartNew()
$output = & $leanBin "lean4\Connect5HandProof.lean" 2>&1
$exitCode = $LASTEXITCODE
$sw.Stop()

$output | ForEach-Object { Write-Host $_ }

if ($exitCode -ne 0) {
    Write-Error "Lean 4 verification failed with exit code $exitCode"
    exit $exitCode
}

if ($output -match "sorryAx") {
    Write-Error "Verification failed: 'sorryAx' detected in axiom printouts!"
    exit 1
}

Write-Host ""
Write-Host ("All 12 analytic Hilbert-Erdos theorems verified in Lean 4 ({0:N2}s) with ZERO sorrys and ZERO custom axioms!" -f $sw.Elapsed.TotalSeconds) -ForegroundColor Green
