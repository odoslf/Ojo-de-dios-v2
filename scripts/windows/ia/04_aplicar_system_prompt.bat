@echo off
setlocal enabledelayedexpansion
title Alias opcional de system prompt - LaIA / Mistral

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
set "PROMPT_PATH=%PROJECT_ROOT%\docs\ai_prompts\laia_mistral_system_prompt.md"
set "LOG_DIR=%PROJECT_ROOT%\storage\logs\ia"
set "RUNTIME_DIR=%PROJECT_ROOT%\storage\runtime"
set "TEMP_MODELFILE=%TEMP%\Modelfile_laia.txt"
set "NOMBRE_PROMPT=laia-mistral-con-prompt"
set "LOG_FILE=%LOG_DIR%\aplicar_prompt.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"

echo ============================================
echo   Alias opcional de system prompt - LaIA / Mistral
echo ============================================
echo Modelo oficial: %MODELO_OFICIAL%
echo Alias de prueba: %NOMBRE_PROMPT%
echo.
>> "%LOG_FILE%" echo ============================================
>> "%LOG_FILE%" echo Inicio: %date% %time%

where ollama >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Ollama no esta instalado.
    >> "%LOG_FILE%" echo [ERROR] Ollama no instalado.
    popd >nul 2>&1
    pause
    exit /b 1
)

ollama list | findstr /i /c:"%MODELO_OFICIAL%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Modelo oficial no encontrado: %MODELO_OFICIAL%
    echo Ejecuta scripts\windows\ia\01_instalar_ollama.bat primero.
    >> "%LOG_FILE%" echo [ERROR] Modelo oficial no encontrado: %MODELO_OFICIAL%
    popd >nul 2>&1
    pause
    exit /b 1
)

if not exist "%PROMPT_PATH%" (
    echo [ERROR] Archivo de prompt no encontrado: %PROMPT_PATH%
    echo [INFO] No se crea alias. El modelo oficial permanece: %MODELO_OFICIAL%
    >> "%LOG_FILE%" echo [ERROR] Prompt no encontrado: %PROMPT_PATH%
    popd >nul 2>&1
    pause
    exit /b 1
)

> "%TEMP_MODELFILE%" echo FROM %MODELO_OFICIAL%
>> "%TEMP_MODELFILE%" echo.
>> "%TEMP_MODELFILE%" echo SYSTEM """
type "%PROMPT_PATH%" >> "%TEMP_MODELFILE%"
>> "%TEMP_MODELFILE%" echo """

ollama create %NOMBRE_PROMPT% -f "%TEMP_MODELFILE%" > "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] Fallo al crear alias opcional: %NOMBRE_PROMPT%
    del "%TEMP_MODELFILE%" >nul 2>&1
    popd >nul 2>&1
    pause
    exit /b 1
)

del "%TEMP_MODELFILE%" >nul 2>&1
echo [OK] Alias opcional creado: %NOMBRE_PROMPT%
echo [INFO] El modelo oficial sigue siendo: %MODELO_OFICIAL%
echo [INFO] La app debe enviar MISTRAL_SYSTEM_PROMPT_PATH en cada peticion.
echo [INFO] No se cambia MISTRAL_MODEL ni laia_mistral_default_model.txt salvo eleccion explicita del usuario.
>> "%LOG_FILE%" echo [OK] Alias opcional creado sin cambiar modelo oficial.

echo {"status":"PROMPT_ALIAS_READY","official_model":"%MODELO_OFICIAL%","prompt_alias":"%NOMBRE_PROMPT%","checked_at":"%date% %time%"} > "%RUNTIME_DIR%\laia_mistral_prompt_alias_status.json"

popd >nul 2>&1
pause
exit /b 0
