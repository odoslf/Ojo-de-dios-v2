@echo off
setlocal enabledelayedexpansion
title Preparar primera estacion Windows - Ojo de Dios

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\..\..\"
pushd "%PROJECT_ROOT%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No estas dentro de Ojo de Dios.
    pause
    exit /b 1
)
if not exist ".env.example" (
    echo [ERROR] No se encontro .env.example. Ejecuta este BAT desde el ZIP/copia final de Ojo de Dios.
    popd >nul 2>&1
    pause
    exit /b 1
)
for %%I in (.) do set "PROJECT_ROOT=%%~fI"

set "RUNTIME_DIR=%PROJECT_ROOT%\storage\runtime"
set "LOG_DIR=%PROJECT_ROOT%\storage\logs\ia"
set "OLLAMA_MODELS_DIR=%PROJECT_ROOT%\storage\models\ollama"
set "KNOWLEDGE_DIR=%PROJECT_ROOT%\storage\knowledge"
set "LAB_DIR=%PROJECT_ROOT%\modules\laboratory"
set "LOG_FILE=%LOG_DIR%\primera_estacion_preflight.log"
set "STATUS_FILE=%RUNTIME_DIR%\first_station_status.json"
set "MODELO_OFICIAL=CognitiveComputations/dolphin-mistral-nemo:12b"

if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%OLLAMA_MODELS_DIR%" mkdir "%OLLAMA_MODELS_DIR%"
if not exist "%KNOWLEDGE_DIR%" mkdir "%KNOWLEDGE_DIR%"
if not exist "%LAB_DIR%" mkdir "%LAB_DIR%"
if not exist "%LAB_DIR%\_inbox" mkdir "%LAB_DIR%\_inbox"
if not exist "%LAB_DIR%\_reviews" mkdir "%LAB_DIR%\_reviews"
if not exist "%LAB_DIR%\_sandbox" mkdir "%LAB_DIR%\_sandbox"
if not exist "%LAB_DIR%\_promoted_manifest" mkdir "%LAB_DIR%\_promoted_manifest"

>> "%LOG_FILE%" echo ============================================
>> "%LOG_FILE%" echo Primera estacion preflight: %date% %time%
>> "%LOG_FILE%" echo PROJECT_ROOT=%PROJECT_ROOT%
>> "%LOG_FILE%" echo MODELO_OFICIAL=%MODELO_OFICIAL%

echo ============================================
echo   Preparar primera estacion Windows - Ojo de Dios
echo ============================================
echo Raiz: %PROJECT_ROOT%
echo Modelo oficial: %MODELO_OFICIAL%
echo.
echo [INFO] Este preflight NO instala Ollama, NO descarga modelos y NO llama a DeepSeek.
echo [INFO] Solo crea rutas locales, valida .env.example y deja .env preparado si falta.

if not exist ".env" (
    copy ".env.example" ".env" >nul
    if errorlevel 1 (
        echo [ERROR] No se pudo crear .env desde .env.example.
        echo {"status":"FAILED","reason":"env_copy_failed","checked_at":"%date% %time%"} > "%STATUS_FILE%"
        popd >nul 2>&1
        pause
        exit /b 1
    )
    echo [OK] .env creado desde .env.example. Edita solo secretos reales en esta estacion.
    >> "%LOG_FILE%" echo [OK] .env creado desde .env.example.
) else (
    echo [OK] .env ya existe. No se sobrescribe.
    >> "%LOG_FILE%" echo [OK] .env ya existia.
)

set "MISSING_VARS="
call :require_env_example "AI_ENABLED=0"
call :require_env_example "MISTRAL_ENABLED=0"
call :require_env_example "MISTRAL_MODEL=%MODELO_OFICIAL%"
call :require_env_example "MISTRAL_API_URL=http://localhost:11434"
call :require_env_example "OLLAMA_MODELS=storage/models/ollama"
call :require_env_example "ANGEL_ENABLED=0"
call :require_env_example "ANGEL_WORKSPACE=modules/laboratory"
call :require_env_example "DEEPSEEK_API_KEY=ALAZAN_REEMPLAZAR_EN_ENV_LOCAL"
call :require_env_example "DEEPSEEK_API_URL=https://api.deepseek.com"
call :require_env_example "DEEPSEEK_MODEL=deepseek-v4-pro"
call :require_env_example "DEEPSEEK_FAST_MODEL=deepseek-v4-flash"

if defined MISSING_VARS (
    echo [ERROR] .env.example no contiene variables obligatorias: !MISSING_VARS!
    >> "%LOG_FILE%" echo [ERROR] Missing vars: !MISSING_VARS!
    echo {"status":"PARTIAL","reason":"env_example_missing_required_values","missing":"!MISSING_VARS!","model":"%MODELO_OFICIAL%","checked_at":"%date% %time%"} > "%STATUS_FILE%"
    popd >nul 2>&1
    pause
    exit /b 1
)

set "OLLAMA_MODELS=%OLLAMA_MODELS_DIR%"
setx OLLAMA_MODELS "%OLLAMA_MODELS_DIR%" >> "%LOG_FILE%" 2>&1
echo [OK] OLLAMA_MODELS preparado para esta estacion: %OLLAMA_MODELS_DIR%
echo [OK] Workspace Hermes Agent preparado: %LAB_DIR%
echo [OK] Logs IA: %LOG_DIR%
echo [OK] Runtime: %RUNTIME_DIR%

echo {"status":"READY_FOR_WINDOWS_INSTALLATION","downloads_performed":false,"external_api_calls_performed":false,"model":"%MODELO_OFICIAL%","ollama_models":"%OLLAMA_MODELS_DIR:\=\\%","hermes_workspace":"modules/laboratory","next_steps":["scripts\\windows\\ia\\instalar_laia_mistral.bat opcion 1","scripts\\windows\\ia\\03_probar_mistral.bat","scripts\\windows\\ia\\preparar_estacion_angel_hermes.bat","scripts\\windows\\ia\\comprobar_angel_hermes.bat"],"checked_at":"%date% %time%"} > "%STATUS_FILE%"
>> "%LOG_FILE%" echo [OK] READY_FOR_WINDOWS_INSTALLATION

echo.
echo [OK] Primera estacion preparada sin descargas ni llamadas externas.
echo [SIGUIENTE] Ejecuta instalar_laia_mistral.bat opcion 1 cuando quieras descargar el modelo en Windows.
popd >nul 2>&1
pause
exit /b 0

:require_env_example
findstr /c:"%~1" ".env.example" >nul 2>&1
if errorlevel 1 (
    if defined MISSING_VARS (
        set "MISSING_VARS=!MISSING_VARS!,%~1"
    ) else (
        set "MISSING_VARS=%~1"
    )
)
exit /b 0
