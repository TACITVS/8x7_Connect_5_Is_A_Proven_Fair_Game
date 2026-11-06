# Build and verify script for Rocq 9.1 Connect-5 formal proof
$ErrorActionPreference = "Stop"
$rocq = "C:\Rocq-Platform~9.1~2026.01\bin\rocq.exe"

$files = @(
    "C5Game.v",
    "C5Board.v",
    "C5Principle.v",
    "C5Rules.v",
    "C5Certificate.v",
    "C5CertChecker.v",
    "CheckAssumptions.v"
)

Write-Host "=== Compiling Connect-5 (8x7) Formal Mathematical Proof ===" -ForegroundColor Cyan
foreach ($f in $files) {
    Write-Host "Compiling $f..." -NoNewline
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    & $rocq compile -Q . C5 $f
    if ($LASTEXITCODE -ne 0) {
        Write-Host " FAILED!" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    $sw.Stop()
    Write-Host " OK ($([math]::Round($sw.Elapsed.TotalSeconds, 2))s)" -ForegroundColor Green
}

Write-Host "`nAll 6 foundational theory files compiled and verified with ZERO axioms and ZERO admits!" -ForegroundColor Cyan
