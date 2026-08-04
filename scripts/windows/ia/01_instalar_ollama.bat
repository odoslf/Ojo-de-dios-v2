@echo off
setlocal enabledelayedexpansion
title Instalar Ollama y Mistral - Ojo de Dios

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\..\..\"
pushd "%PROJECT_ROOT%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No estás dentro de Ojo de Dios
    pause
    exit /b 1
)
if not exist ".env.example" (
    echo [ERROR] No estás dentro de Ojo de Dios
    popd >nul 2>&1
    pause
    exit /b 1
)
for %%I in (.) do set "PROJECT_ROOT=%%~fI"

set "MODELO_OFICIAL=CognitiveComputations/dolphin-mistral-nemo:12b"
set "LOG_DIR=%PROJECT_ROOT%\storage\logs\ia"
set "RUNTIME_DIR=%PROJECT_ROOT%\storage\runtime"
set "OLLAMA_MODELS_DIR=%PROJECT_ROOT%\storage\models\ollama"
set "LOG_FILE=%LOG_DIR%\instalar_ollama.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if not exist "%OLLAMA_MODELS_DIR%" mkdir "%OLLAMA_MODELS_DIR%"

call :detect_python
if errorlevel 1 goto :fin_error

echo ============================================
echo   Instalar Ollama y Mistral - Ojo de Dios
echo ============================================
echo Raiz: %PROJECT_ROOT%
echo Modelo oficial: %MODELO_OFICIAL%
echo Modelos Ollama: %OLLAMA_MODELS_DIR%
echo.
>> "%LOG_FILE%" echo ============================================
>> "%LOG_FILE%" echo Inicio: %date% %time%
>> "%LOG_FILE%" echo PROJECT_ROOT=%PROJECT_ROOT%
>> "%LOG_FILE%" echo PY_CMD=%PY_CMD%

set "OLLAMA_MODELS=%OLLAMA_MODELS_DIR%"
setx OLLAMA_MODELS "%OLLAMA_MODELS_DIR%" >> "%LOG_FILE%" 2>&1
echo [INFO] OLLAMA_MODELS=%OLLAMA_MODELS_DIR%
echo [AVISO] reinicia Ollama/CMD si no respeta la ruta.

where ollama >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Ollama no encontrado. Estado: MISSING_TOOL
    >> "%LOG_FILE%" echo [ERROR] MISSING_TOOL: ollama no encontrado.
    start https://ollama.com/download/windows
    echo {"status":"MISSING_TOOL","tool":"ollama","checked_at":"%date% %time%"} > "%RUNTIME_DIR%\laia_mistral_status.json"
    goto :fin_error
)

ollama --version >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama esta en PATH pero no responde. Estado: MISSING_TOOL
    >> "%LOG_FILE%" echo [ERROR] MISSING_TOOL: ollama --version fallo.
    echo {"status":"MISSING_TOOL","tool":"ollama","checked_at":"%date% %time%"} > "%RUNTIME_DIR%\laia_mistral_status.json"
    goto :fin_error
)
echo [OK] Ollama detectado.

echo [INFO] Descargando modelo oficial...
>> "%LOG_FILE%" echo [INFO] ollama pull %MODELO_OFICIAL%
ollama pull %MODELO_OFICIAL% >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] Fallo al descargar modelo oficial. Estado: MODEL_MISSING
    echo {"status":"MODEL_MISSING","model":"%MODELO_OFICIAL%","checked_at":"%date% %time%"} > "%RUNTIME_DIR%\laia_mistral_status.json"
    goto :fin_error
)

echo [INFO] Modelos disponibles:
ollama list
ollama list >> "%LOG_FILE%" 2>&1
ollama list | findstr /i /c:"%MODELO_OFICIAL%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] El modelo oficial no aparece en ollama list. Estado: MODEL_MISSING
    echo {"status":"MODEL_MISSING","model":"%MODELO_OFICIAL%","checked_at":"%date% %time%"} > "%RUNTIME_DIR%\laia_mistral_status.json"
    goto :fin_error
)

echo %MODELO_OFICIAL% > "%RUNTIME_DIR%\laia_mistral_default_model.txt"
echo {"status":"READY_LOCAL_AI","model":"%MODELO_OFICIAL%","ollama_models":"%OLLAMA_MODELS_DIR:\=\\%","checked_at":"%date% %time%"} > "%RUNTIME_DIR%\laia_mistral_status.json"
echo [OK] Modelo oficial listo: %MODELO_OFICIAL%
>> "%LOG_FILE%" echo [OK] Modelo oficial listo.
popd >nul 2>&1
pause
exit /b 0

:fin_error
popd >nul 2>&1
pause
exit /b 1

:detect_python
set "PY_CMD="
py -3.12 -c "import platform,sys; assert sys.version_info[:2]==(3,12); assert platform.architecture()[0]=='64bit'" >nul 2>&1
if not errorlevel 1 set "PY_CMD=py -3.12"
if not defined PY_CMD (
    python -c "import platform,sys; assert sys.version_info[:2]==(3,12); assert platform.architecture()[0]=='64bit'" >nul 2>&1
    if not errorlevel 1 set "PY_CMD=python"
)
if not defined PY_CMD (
    echo [ERROR] Se requiere Python 3.12.x 64 bits. No se instalara Python desde este BAT.
    if defined LOG_FILE >> "%LOG_FILE%" echo [ERROR] Python 3.12.x 64 bits no detectado.
    exit /b 1
)
%PY_CMD% -c "import platform,sys; print('Python %s %s' % (sys.version.split()[0], platform.architecture()[0]))"
exit /b 0
