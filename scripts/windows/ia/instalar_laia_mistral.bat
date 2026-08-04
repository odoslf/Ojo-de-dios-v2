@echo off
setlocal enabledelayedexpansion
title Instalador LaIA / Mistral local - Ojo de Dios

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
set "LOG_FILE=%LOG_DIR%\instalar_laia_mistral.log"
set "PRIVATE_LOG=%LOG_DIR%\laia_mistral_private_flow.log"
set "DEFAULT_MODEL_FILE=%RUNTIME_DIR%\laia_mistral_default_model.txt"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if not exist "%OLLAMA_MODELS_DIR%" mkdir "%OLLAMA_MODELS_DIR%"

call :detect_python
if errorlevel 1 (
    echo [ERROR] Python 3.12.x 64 bits requerido. No se instala Python desde este BAT.
    echo [ERROR] Python 3.12.x 64 bits no detectado. >> "%LOG_FILE%"
    popd >nul 2>&1
    pause
    exit /b 1
)

set "OLLAMA_MODELS=%OLLAMA_MODELS_DIR%"
setx OLLAMA_MODELS "%OLLAMA_MODELS_DIR%" >> "%LOG_FILE%" 2>&1
echo [INFO] OLLAMA_MODELS=%OLLAMA_MODELS_DIR%
echo [AVISO] reinicia Ollama/CMD si no respeta la ruta.
>> "%LOG_FILE%" echo ============================================
>> "%LOG_FILE%" echo Inicio instalador: %date% %time%
>> "%LOG_FILE%" echo PROJECT_ROOT=%PROJECT_ROOT%
>> "%LOG_FILE%" echo PY_CMD=%PY_CMD%

:menu_principal
cls
echo ============================================
echo   Instalador LaIA / Mistral local - Ojo de Dios
echo ============================================
echo Raiz detectada: %PROJECT_ROOT%
echo Modelo oficial: %MODELO_OFICIAL%
echo.
echo 0. Preparar primera estacion sin descargar ni llamar APIs
echo 1. Instalar/comprobar Ollama y descargar modelo oficial
echo 2. Crear alias opcional con system prompt de prueba
echo 3. Ejecutar flujo privado funcional del usuario
echo 4. Probar modelo y guardar healthcheck
echo 5. SALIR
echo ============================================
set /p OPCION="Elige una opcion (0, 1, 2, 3, 4 o 5): "

if "%OPCION%"=="0" goto preparar_primera_estacion
if "%OPCION%"=="1" goto instalar_ollama
if "%OPCION%"=="2" goto aplicar_prompt
if "%OPCION%"=="3" goto flujo_privado
if "%OPCION%"=="4" goto probar_modelo
if "%OPCION%"=="5" goto salir
echo Opcion no valida.
pause
goto menu_principal

:preparar_primera_estacion
cls
echo [INFO] Ejecutando preflight de primera estacion sin descargas...
call "%SCRIPT_DIR%00_preparar_primera_estacion.bat"
echo [INFO] 00_preparar_primera_estacion.bat finalizo con codigo !errorlevel!. >> "%LOG_FILE%"
pause
goto menu_principal

:instalar_ollama
cls
echo [INFO] Ejecutando instalador Ollama/Mistral...
call "%SCRIPT_DIR%01_instalar_ollama.bat"
echo [INFO] 01_instalar_ollama.bat finalizo con codigo !errorlevel!. >> "%LOG_FILE%"
pause
goto menu_principal

:aplicar_prompt
cls
echo [INFO] Creando alias opcional de system prompt si existe el prompt...
call "%SCRIPT_DIR%04_aplicar_system_prompt.bat"
echo [INFO] 04_aplicar_system_prompt.bat finalizo con codigo !errorlevel!. >> "%LOG_FILE%"
pause
goto menu_principal

:probar_modelo
cls
echo [INFO] Ejecutando healthcheck LaIA/Mistral...
call "%SCRIPT_DIR%03_probar_mistral.bat"
echo [INFO] 03_probar_mistral.bat finalizo con codigo !errorlevel!. >> "%LOG_FILE%"
pause
goto menu_principal

:flujo_privado
cls
echo ============================================
echo   Ejecutar flujo privado funcional del usuario
echo ============================================
echo [INFO] No se modifica el algoritmo privado; solo se valida chasis, rutas, PY_CMD y logs.
>> "%PRIVATE_LOG%" echo ============================================
>> "%PRIVATE_LOG%" echo Inicio flujo privado: %date% %time%
>> "%PRIVATE_LOG%" echo PROJECT_ROOT=%PROJECT_ROOT%
>> "%PRIVATE_LOG%" echo PY_CMD=%PY_CMD%

call :preflight_private
if errorlevel 1 (
    call :write_private_status "PRIVATE_VARIANT_FAILED" "preflight_failed"
    echo [ERROR] Preflight privado fallido. Revisa: %PRIVATE_LOG%
    pause
    goto menu_principal
)

set "PRIVATE_ENTRY="
if defined MISTRAL_PRIVATE_FLOW_CMD set "PRIVATE_ENTRY=%MISTRAL_PRIVATE_FLOW_CMD%"
if not defined PRIVATE_ENTRY if exist "%SCRIPT_DIR%flujo_privado_laia_mistral.bat" set "PRIVATE_ENTRY=%SCRIPT_DIR%flujo_privado_laia_mistral.bat"
if not defined PRIVATE_ENTRY if exist "%SCRIPT_DIR%laia_mistral_private_flow.bat" set "PRIVATE_ENTRY=%SCRIPT_DIR%laia_mistral_private_flow.bat"
if not defined PRIVATE_ENTRY if exist "%SCRIPT_DIR%abliterar_mistral_privado.bat" set "PRIVATE_ENTRY=%SCRIPT_DIR%abliterar_mistral_privado.bat"
if not defined PRIVATE_ENTRY if exist "%PROJECT_ROOT%\private\laia_mistral_private_flow.bat" set "PRIVATE_ENTRY=%PROJECT_ROOT%\private\laia_mistral_private_flow.bat"

if not defined PRIVATE_ENTRY (
    echo [ERROR] No se encontro el flujo privado del usuario.
    echo [INFO] Define MISTRAL_PRIVATE_FLOW_CMD o coloca uno de estos BAT privados:
    echo        %SCRIPT_DIR%flujo_privado_laia_mistral.bat
    echo        %SCRIPT_DIR%laia_mistral_private_flow.bat
    echo        %SCRIPT_DIR%abliterar_mistral_privado.bat
    echo        %PROJECT_ROOT%\private\laia_mistral_private_flow.bat
    >> "%PRIVATE_LOG%" echo [ERROR] PRIVATE_VARIANT_FAILED: no se encontro entrada privada.
    call :write_private_status "PRIVATE_VARIANT_FAILED" "private_entry_missing"
    pause
    goto menu_principal
)

>> "%PRIVATE_LOG%" echo [INFO] Ejecutando entrada privada: %PRIVATE_ENTRY%
echo [INFO] Ejecutando entrada privada: %PRIVATE_ENTRY%
call "%PRIVATE_ENTRY%" >> "%PRIVATE_LOG%" 2>&1
set "PRIVATE_EXIT=!errorlevel!"
>> "%PRIVATE_LOG%" echo [INFO] Codigo salida flujo privado: !PRIVATE_EXIT!
if not "!PRIVATE_EXIT!"=="0" (
    echo [ERROR] El flujo privado fallo. No se borra nada. Estado: PRIVATE_VARIANT_FAILED
    call :write_private_status "PRIVATE_VARIANT_FAILED" "private_flow_exit_!PRIVATE_EXIT!"
    pause
    goto menu_principal
)

call :detect_private_model
if errorlevel 1 (
    echo [ERROR] No se detecto el modelo privado esperado en ollama list.
    echo [INFO] Configura MISTRAL_PRIVATE_MODEL o crea storage\runtime\laia_mistral_private_model.txt desde tu flujo privado.
    call :write_private_status "PRIVATE_VARIANT_FAILED" "private_model_missing"
    pause
    goto menu_principal
)

echo !PRIVATE_MODEL! > "%DEFAULT_MODEL_FILE%"
call :write_private_status "PRIVATE_VARIANT_READY" "ok"
echo [OK] Variante privada lista: !PRIVATE_MODEL!
echo [OK] Modelo por defecto escrito en: %DEFAULT_MODEL_FILE%
>> "%PRIVATE_LOG%" echo [OK] PRIVATE_VARIANT_READY: !PRIVATE_MODEL!
pause
goto menu_principal

:preflight_private
where ollama >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Ollama no esta instalado.
    >> "%PRIVATE_LOG%" echo [ERROR] Ollama no esta instalado.
    exit /b 1
)
ollama --version >> "%PRIVATE_LOG%" 2>&1
if errorlevel 1 exit /b 1
ollama list | findstr /i /c:"%MODELO_OFICIAL%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Modelo base no descargado: %MODELO_OFICIAL%
    >> "%PRIVATE_LOG%" echo [ERROR] Modelo base ausente: %MODELO_OFICIAL%
    exit /b 1
)
if not defined PY_CMD exit /b 1
where git >nul 2>nul
if errorlevel 1 (
    echo [AVISO] git no esta disponible. Si tu flujo privado usa git, fallara.
    >> "%PRIVATE_LOG%" echo [AVISO] git no disponible.
) else (
    git --version >> "%PRIVATE_LOG%" 2>&1
)
exit /b 0

:detect_private_model
set "PRIVATE_MODEL="
if defined MISTRAL_PRIVATE_MODEL set "PRIVATE_MODEL=%MISTRAL_PRIVATE_MODEL%"
if not defined PRIVATE_MODEL if exist "%RUNTIME_DIR%\laia_mistral_private_model.txt" set /p PRIVATE_MODEL=<"%RUNTIME_DIR%\laia_mistral_private_model.txt"
if not defined PRIVATE_MODEL set "PRIVATE_MODEL=laia-mistral-privado"
ollama list | findstr /c:"!PRIVATE_MODEL!" >nul 2>&1
if errorlevel 1 exit /b 1
exit /b 0

:write_private_status
set "PRIVATE_STATUS=%~1"
set "PRIVATE_REASON=%~2"
if defined PRIVATE_MODEL (
    echo {"status":"%PRIVATE_STATUS%","reason":"%PRIVATE_REASON%","model":"!PRIVATE_MODEL!","checked_at":"%date% %time%"} > "%RUNTIME_DIR%\laia_mistral_status.json"
) else (
    echo {"status":"%PRIVATE_STATUS%","reason":"%PRIVATE_REASON%","checked_at":"%date% %time%"} > "%RUNTIME_DIR%\laia_mistral_status.json"
)
exit /b 0

:detect_python
set "PY_CMD="
py -3.12 -c "import platform,sys; assert sys.version_info[:2]==(3,12); assert platform.architecture()[0]=='64bit'" >nul 2>&1
if not errorlevel 1 set "PY_CMD=py -3.12"
if not defined PY_CMD (
    python -c "import platform,sys; assert sys.version_info[:2]==(3,12); assert platform.architecture()[0]=='64bit'" >nul 2>&1
    if not errorlevel 1 set "PY_CMD=python"
)
if not defined PY_CMD exit /b 1
%PY_CMD% -c "import platform,sys; print('Python %s %s' % (sys.version.split()[0], platform.architecture()[0]))" >> "%LOG_FILE%" 2>&1
exit /b 0

:salir
echo Saliendo del instalador...
echo Fin instalador LaIA / Mistral local: %date% %time% >> "%LOG_FILE%"
popd >nul 2>&1
exit /b 0
