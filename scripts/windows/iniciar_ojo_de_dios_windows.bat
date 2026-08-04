@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Iniciar Ojo de Dios - Windows

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\..\"
pushd "%PROJECT_ROOT%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se pudo abrir la raiz del proyecto.
    pause
    exit /b 1
)
if not exist "app\main.py" (
    echo [ERROR] No se encontro app\main.py. Ejecuta este BAT desde la copia/ZIP completo del proyecto.
    popd >nul 2>&1
    pause
    exit /b 1
)
for %%I in (.) do set "PROJECT_ROOT=%%~fI"

set "RUNTIME_DIR=%PROJECT_ROOT%\storage\runtime"
set "LOG_DIR=%PROJECT_ROOT%\storage\logs\app"
set "STATUS_FILE=%RUNTIME_DIR%\windows_app_start_status.json"
set "LOG_FILE=%LOG_DIR%\windows_app_start.log"
set "VENV_PY=%PROJECT_ROOT%\.venv\Scripts\python.exe"
set "HOST=127.0.0.1"
set "PORT=8000"

if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

>> "%LOG_FILE%" echo ============================================
>> "%LOG_FILE%" echo Inicio aplicacion Windows: %date% %time%
>> "%LOG_FILE%" echo PROJECT_ROOT=%PROJECT_ROOT%

echo ============================================
echo   Ojo de Dios - inicio Windows
echo ============================================
echo Raiz: %PROJECT_ROOT%
echo.

call :detect_python
if errorlevel 1 goto fail

if not exist "%PROJECT_ROOT%\.venv" (
    echo [INFO] Creando entorno Python local .venv...
    >> "%LOG_FILE%" echo [INFO] Creando .venv con %PY_CMD%
    %PY_CMD% -m venv "%PROJECT_ROOT%\.venv" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 goto fail
)
if not exist "%VENV_PY%" (
    echo [ERROR] Falta Python del entorno: %VENV_PY%
    goto fail
)

echo [INFO] Instalando/validando dependencias reales...
"%VENV_PY%" -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
if errorlevel 1 goto fail

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] .env creado desde .env.example. Edita secretos solo en tu PC si activas Hermes.
        >> "%LOG_FILE%" echo [OK] .env creado desde .env.example
    ) else (
        echo [ERROR] Falta .env.example.
        goto fail
    )
)

for %%D in (storage storage\runtime storage\workspaces storage\evidence storage\job_logs storage\reports storage\tmp storage\knowledge modules\laboratory modules\laboratory\_inbox modules\laboratory\_reviews modules\laboratory\_sandbox modules\laboratory\_promoted_manifest) do (
    if not exist "%%D" mkdir "%%D"
)

echo [INFO] Generando first-run status local...
"%VENV_PY%" -m app.core.windows_first_run --repo-root "%PROJECT_ROOT%" --write >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] First-run preflight fallido. Revisa %LOG_FILE%
    goto fail
)

echo {"status":"STARTING","url":"http://%HOST%:%PORT%/modules","m16_plan":"/api/ops/m16/windows-start-plan","first_run":"/api/ops/m16/first-run","m01_passive_dns":"/api/modules/m01_osint/osint/domain-snapshot","checked_at":"%date% %time%"} > "%STATUS_FILE%"

echo.
echo [OK] Preparado. Abre en el navegador:
echo      http://%HOST%:%PORT%/modules
echo.
echo [INFO] Arrancando servidor. Deja esta ventana abierta.
start "" "http://%HOST%:%PORT%/modules"
>> "%LOG_FILE%" echo [INFO] Arrancando uvicorn en %HOST%:%PORT%
"%VENV_PY%" -m uvicorn app.main:app --host %HOST% --port %PORT%
set "SERVER_RC=%ERRORLEVEL%"
>> "%LOG_FILE%" echo [INFO] uvicorn finalizo con codigo %SERVER_RC%
if not "%SERVER_RC%"=="0" goto fail
popd >nul 2>&1
exit /b 0

:detect_python
set "PY_CMD="
py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>nul
if not errorlevel 1 set "PY_CMD=py -3.12"
if not defined PY_CMD (
    python -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>nul
    if not errorlevel 1 set "PY_CMD=python"
)
if not defined PY_CMD (
    echo [ERROR] Necesitas Python 3.12 instalado y en PATH.
    >> "%LOG_FILE%" echo [ERROR] Python 3.12 no detectado.
    exit /b 1
)
echo [OK] Python detectado: %PY_CMD%
exit /b 0

:fail
echo {"status":"FAILED","url":"http://%HOST%:%PORT%/modules","checked_at":"%date% %time%"} > "%STATUS_FILE%"
echo.
echo [ERROR] No se pudo iniciar. Revisa: %LOG_FILE%
popd >nul 2>&1
pause
exit /b 1
