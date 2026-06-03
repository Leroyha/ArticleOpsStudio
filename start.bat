@echo off
setlocal

echo =============================================
echo     ArticleOps Studio 正在启动...
echo =============================================

where uv >nul 2>nul
if errorlevel 1 (
    echo 未找到 uv，请先安装 uv，或在项目目录执行：
    echo python -m pip install uv
    pause
    exit /b 1
)

cd /d "%~dp0"

set "ARTICLEOPS_RUNTIME_DIR=%~dp0articleops-runtime"
set "TEMP=%ARTICLEOPS_RUNTIME_DIR%\temp"
set "TMP=%ARTICLEOPS_RUNTIME_DIR%\temp"
set "TMPDIR=%ARTICLEOPS_RUNTIME_DIR%\temp"
set "XDG_CACHE_HOME=%ARTICLEOPS_RUNTIME_DIR%\cache"
set "UV_CACHE_DIR=%ARTICLEOPS_RUNTIME_DIR%\cache\uv"
set "PYTHONPYCACHEPREFIX=%ARTICLEOPS_RUNTIME_DIR%\cache\pycache"

if not exist "%ARTICLEOPS_RUNTIME_DIR%" mkdir "%ARTICLEOPS_RUNTIME_DIR%"
if not exist "%ARTICLEOPS_RUNTIME_DIR%\data" mkdir "%ARTICLEOPS_RUNTIME_DIR%\data"
if not exist "%ARTICLEOPS_RUNTIME_DIR%\logs" mkdir "%ARTICLEOPS_RUNTIME_DIR%\logs"
if not exist "%ARTICLEOPS_RUNTIME_DIR%\cache" mkdir "%ARTICLEOPS_RUNTIME_DIR%\cache"
if not exist "%ARTICLEOPS_RUNTIME_DIR%\temp" mkdir "%ARTICLEOPS_RUNTIME_DIR%\temp"
if not exist "%ARTICLEOPS_RUNTIME_DIR%\exports" mkdir "%ARTICLEOPS_RUNTIME_DIR%\exports"
if not exist "%ARTICLEOPS_RUNTIME_DIR%\evidence" mkdir "%ARTICLEOPS_RUNTIME_DIR%\evidence"
if not exist "%ARTICLEOPS_RUNTIME_DIR%\backups" mkdir "%ARTICLEOPS_RUNTIME_DIR%\backups"
if not exist "%ARTICLEOPS_RUNTIME_DIR%\docs" mkdir "%ARTICLEOPS_RUNTIME_DIR%\docs"

uv run articleops

if errorlevel 1 (
    echo.
    echo 启动失败，请检查 uv 环境和依赖是否已安装。
)

pause
