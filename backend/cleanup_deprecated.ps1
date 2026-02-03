# Cleanup Script - Remove Deprecated Files
# Run this after verifying the refactored code works correctly

Write-Host "Cleaning up deprecated endpoint files..." -ForegroundColor Yellow

$filesToRemove = @(
    "app\api\v1\endpoints\sessions.py",
    "app\api\v1\endpoints\versions.py"
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Write-Host "Removing: $file" -ForegroundColor Red
        Remove-Item $file -Force
        Write-Host "  ✓ Deleted" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ File not found: $file" -ForegroundColor Gray
    }
}

Write-Host "`nCleanup complete!" -ForegroundColor Green
Write-Host "The following files have been consolidated into sessions_versions.py:" -ForegroundColor Cyan
Write-Host "  - sessions.py (130 lines)" -ForegroundColor Gray
Write-Host "  - versions.py (75 lines)" -ForegroundColor Gray
Write-Host "`nNew unified file:" -ForegroundColor Cyan
Write-Host "  - sessions_versions.py (200 lines)" -ForegroundColor Green
