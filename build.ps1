# Rapid Dev Proxy - Build Script
Write-Host "Rapid Dev Proxy - Build Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Build executable
Write-Host "Building executable..." -ForegroundColor Yellow
uv run python -m PyInstaller rapid_dev_proxy.spec --clean --noconfirm

# Check if build was successful
if (Test-Path "dist\rapid-dev-proxy.exe") {
    $size = (Get-Item "dist\rapid-dev-proxy.exe").Length
    $sizeMB = [math]::Round($size / 1MB, 2)
    
    Write-Host ""
    Write-Host "✓ Build completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable created: dist\rapid-dev-proxy.exe" -ForegroundColor Cyan
    Write-Host "Size: $sizeMB MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now run the proxy with:" -ForegroundColor Yellow
    Write-Host "  .\dist\rapid-dev-proxy.exe --help" -ForegroundColor White
    Write-Host "  .\dist\rapid-dev-proxy.exe init" -ForegroundColor White
    Write-Host "  .\dist\rapid-dev-proxy.exe start -c config.json" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
} 