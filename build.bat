@echo off
echo Rapid Dev Proxy - Build Script
echo ========================================

echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Building executable...
uv run python -m PyInstaller rapid_dev_proxy.spec --clean --noconfirm

if exist dist\rapid-dev-proxy.exe (
    echo.
    echo ✓ Build completed successfully!
    echo.
    echo Executable created: dist\rapid-dev-proxy.exe
    echo Size: 
    for %%A in (dist\rapid-dev-proxy.exe) do echo   %%~zA bytes
    echo.
    echo You can now run the proxy with:
    echo   dist\rapid-dev-proxy.exe --help
    echo   dist\rapid-dev-proxy.exe init
    echo   dist\rapid-dev-proxy.exe start -c config.json
) else (
    echo.
    echo ❌ Build failed!
    exit /b 1
) 