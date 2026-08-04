@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Exportar ZIP Ojo de Dios - Windows Ready

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\..\"
pushd "%PROJECT_ROOT%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se pudo resolver la raiz del proyecto.
    pause
    exit /b 1
)
if not exist "scripts\export_project_zip.py" (
    echo [ERROR] Falta scripts\export_project_zip.py
    popd >nul 2>&1
    pause
    exit /b 1
)

set "PY_CMD="
py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>nul
if not errorlevel 1 set "PY_CMD=py -3.12"
if not defined PY_CMD (
    python -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>nul
    if not errorlevel 1 set "PY_CMD=python"
)
if not defined PY_CMD (
    echo [ERROR] Necesitas Python 3.12 instalado y en PATH.
    popd >nul 2>&1
    pause
    exit /b 1
)

%PY_CMD% scripts\export_project_zip.py --repo-root "%PROJECT_ROOT%"
if errorlevel 1 (
    echo [ERROR] Exportacion fallida.
    popd >nul 2>&1
    pause
    exit /b 1
)

echo.
echo [OK] ZIP creado en dist\. Revisa dist\latest_zip_export_manifest.json
popd >nul 2>&1
pause
exit /b 0
