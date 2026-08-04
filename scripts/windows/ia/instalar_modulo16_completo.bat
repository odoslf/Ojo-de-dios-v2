@echo off
setlocal enabledelayedexpansion
title Instalador completo Modulo 16 - LaIA/Mistral + Hermes Agent

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\..\..\"
pushd "%PROJECT_ROOT%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se pudo resolver la raiz del proyecto.
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

set "LOG_DIR=%PROJECT_ROOT%\storage\logs\ia"
set "RUNTIME_DIR=%PROJECT_ROOT%\storage\runtime"
set "STATUS_FILE=%RUNTIME_DIR%\m16_full_install_status.json"
set "LOG_FILE=%LOG_DIR%\m16_full_install.log"
set "MODELO_OFICIAL=CognitiveComputations/dolphin-mistral-nemo:12b"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"

>> "%LOG_FILE%" echo ============================================
>> "%LOG_FILE%" echo Inicio instalador completo M16: %date% %time%
>> "%LOG_FILE%" echo PROJECT_ROOT=%PROJECT_ROOT%
>> "%LOG_FILE%" echo MODELO_OFICIAL=%MODELO_OFICIAL%

echo ============================================
echo   Modulo 16 completo - Ojo de Dios
echo   LaIA/Mistral local + Hermes Agent Lab
echo ============================================
echo Raiz: %PROJECT_ROOT%
echo Modelo oficial: %MODELO_OFICIAL%
echo.
echo Este instalador llama a los BAT reales del proyecto y no simula pasos.
echo Puede descargar Ollama/modelo y llamar DeepSeek solo cuando eliges esas opciones.
echo Para arrancar la web usa: scripts\windows\iniciar_ojo_de_dios_windows.bat
echo.

echo 0. Preflight completo sin descargas ni APIs externas
echo 1. Instalar/comprobar Mistral local completo ^(Ollama + modelo + healthcheck^)
echo 2. Construir base de conocimiento local
echo 3. Preparar y comprobar Hermes Agent ^(requiere DEEPSEEK_API_KEY real en .env^)
echo 4. Ejecutar TODO lo posible en orden ^(preguntara en cada paso externo^)
echo 5. Salir
echo.
set /p OPCION="Elige una opcion [0]: "
if "%OPCION%"=="" set "OPCION=0"

if "%OPCION%"=="0" goto preflight
if "%OPCION%"=="1" goto mistral
if "%OPCION%"=="2" goto knowledge
if "%OPCION%"=="3" goto hermes
if "%OPCION%"=="4" goto todo
if "%OPCION%"=="5" goto salir
echo [ERROR] Opcion no valida.
goto fail

:preflight
call :run_step "00_preparar_primera_estacion.bat" "%SCRIPT_DIR%00_preparar_primera_estacion.bat"
if errorlevel 1 goto fail
call :write_status "READY_FOR_WINDOWS_INSTALLATION" "preflight_only"
goto ok

:mistral
call :run_step "00_preparar_primera_estacion.bat" "%SCRIPT_DIR%00_preparar_primera_estacion.bat"
if errorlevel 1 goto fail
call :run_step "01_instalar_ollama.bat" "%SCRIPT_DIR%01_instalar_ollama.bat"
if errorlevel 1 goto fail
call :run_step "03_probar_mistral.bat" "%SCRIPT_DIR%03_probar_mistral.bat"
if errorlevel 1 goto fail
call :write_status "READY_LOCAL_AI" "mistral_healthcheck_ok"
goto ok

:knowledge
call :run_step "construir_base_conocimiento.bat" "%SCRIPT_DIR%construir_base_conocimiento.bat"
if errorlevel 1 goto fail
call :write_status "READY_KNOWLEDGE" "knowledge_built"
goto ok

:hermes
call :run_step "preparar_estacion_angel_hermes.bat" "%SCRIPT_DIR%preparar_estacion_angel_hermes.bat"
if errorlevel 1 goto fail
call :run_step "comprobar_angel_hermes.bat" "%SCRIPT_DIR%comprobar_angel_hermes.bat"
if errorlevel 1 goto fail
call :write_status "READY_CONTROLLED" "hermes_checked"
goto ok

:todo
call :run_step "00_preparar_primera_estacion.bat" "%SCRIPT_DIR%00_preparar_primera_estacion.bat"
if errorlevel 1 goto fail
call :run_step "01_instalar_ollama.bat" "%SCRIPT_DIR%01_instalar_ollama.bat"
if errorlevel 1 goto fail
call :run_step "03_probar_mistral.bat" "%SCRIPT_DIR%03_probar_mistral.bat"
if errorlevel 1 goto fail
call :run_step "construir_base_conocimiento.bat" "%SCRIPT_DIR%construir_base_conocimiento.bat"
if errorlevel 1 goto fail
call :run_step "preparar_estacion_angel_hermes.bat" "%SCRIPT_DIR%preparar_estacion_angel_hermes.bat"
if errorlevel 1 goto fail
call :run_step "comprobar_angel_hermes.bat" "%SCRIPT_DIR%comprobar_angel_hermes.bat"
if errorlevel 1 goto fail
call :write_status "READY_CONTROLLED" "all_steps_ok"
goto ok

:run_step
set "STEP_NAME=%~1"
set "STEP_CMD=%~2"
if not exist "%STEP_CMD%" (
    echo [ERROR] Falta script real: %STEP_CMD%
    >> "%LOG_FILE%" echo [ERROR] Falta script real: %STEP_CMD%
    exit /b 1
)
echo.
echo [STEP] %STEP_NAME%
>> "%LOG_FILE%" echo [STEP] %STEP_NAME% - %date% %time%
call "%STEP_CMD%" >> "%LOG_FILE%" 2>&1
set "STEP_RC=!errorlevel!"
>> "%LOG_FILE%" echo [STEP] %STEP_NAME% exit=!STEP_RC!
if not "!STEP_RC!"=="0" (
    echo [ERROR] Paso fallido: %STEP_NAME% ^(codigo !STEP_RC!^). Revisa %LOG_FILE%
    exit /b !STEP_RC!
)
echo [OK] %STEP_NAME%
exit /b 0

:write_status
set "STATUS=%~1"
set "REASON=%~2"
echo {"status":"%STATUS%","reason":"%REASON%","model":"%MODELO_OFICIAL%","mistral_script":"scripts\\windows\\ia\\instalar_laia_mistral.bat","hermes_script":"scripts\\windows\\ia\\preparar_estacion_angel_hermes.bat","knowledge_script":"scripts\\windows\\ia\\construir_base_conocimiento.bat","app_launcher":"scripts\\windows\\iniciar_ojo_de_dios_windows.bat","checked_at":"%date% %time%"} > "%STATUS_FILE%"
exit /b 0

:ok
echo.
echo [OK] Modulo 16 completado hasta el estado solicitado.
echo Estado: %STATUS_FILE%
echo Log: %LOG_FILE%
popd >nul 2>&1
pause
exit /b 0

:fail
call :write_status "FAILED" "step_failed"
echo.
echo [ERROR] Instalacion M16 incompleta. Estado: %STATUS_FILE%
echo Log: %LOG_FILE%
popd >nul 2>&1
pause
exit /b 1

:salir
popd >nul 2>&1
exit /b 0
