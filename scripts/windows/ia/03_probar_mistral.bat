@echo off
setlocal enabledelayedexpansion
title Healthcheck LaIA / Mistral - Ojo de Dios

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
set "RUNTIME_DIR=%PROJECT_ROOT%\storage\runtime"
set "LOG_DIR=%PROJECT_ROOT%\storage\logs\ia"
set "KNOWLEDGE_DIR=%PROJECT_ROOT%\storage\knowledge"
set "OLLAMA_BASE_URL=http://localhost:11434"
set "LOG_FILE=%LOG_DIR%\laia_mistral_healthcheck.log"
set "STATUS=UNKNOWN"

if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%PROJECT_ROOT%\storage\models\ollama" mkdir "%PROJECT_ROOT%\storage\models\ollama"

call :detect_python
if errorlevel 1 (
    set "STATUS=MISSING_TOOL"
    call :write_status "MISSING_TOOL" "python_3.12_64_missing" ""
    goto :fail
)

>> "%LOG_FILE%" echo ============================================
>> "%LOG_FILE%" echo Healthcheck: %date% %time%
>> "%LOG_FILE%" echo PROJECT_ROOT=%PROJECT_ROOT%

echo ============================================
echo   Healthcheck LaIA / Mistral - Ojo de Dios
echo ============================================
echo Raiz: %PROJECT_ROOT%
echo.

where ollama >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Ollama no esta instalado. Estado: MISSING_TOOL
    set "STATUS=MISSING_TOOL"
    call :write_status "MISSING_TOOL" "ollama_missing" ""
    goto :fail
)
ollama --version >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama no responde. Estado: MISSING_TOOL
    set "STATUS=MISSING_TOOL"
    call :write_status "MISSING_TOOL" "ollama_not_responding" ""
    goto :fail
)
echo [OK] Ollama detectado.

echo [1/4] Comprobando API /api/tags...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-RestMethod -Method Get -Uri '%OLLAMA_BASE_URL%/api/tags' -TimeoutSec 15 ^| ConvertTo-Json -Compress ^| Out-File -Encoding utf8 '%RUNTIME_DIR%\ollama_tags.json'; exit 0 } catch { Write-Error $_; exit 1 }" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] API Ollama no responde. Estado: FAILED
    set "STATUS=FAILED"
    call :write_status "FAILED" "ollama_api_unreachable" ""
    goto :fail
)
echo [OK] /api/tags responde.

ollama list >> "%LOG_FILE%" 2>&1
ollama list | findstr /i /c:"%MODELO_OFICIAL%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Modelo oficial ausente: %MODELO_OFICIAL%. Estado: MODEL_MISSING
    set "STATUS=MODEL_MISSING"
    call :write_status "MODEL_MISSING" "model_not_listed" ""
    goto :fail
)
echo [OK] Modelo oficial detectado.

echo [2/4] Probando /api/generate...
set "GEN_PAYLOAD=%TEMP%\laia_generate_payload.json"
> "%GEN_PAYLOAD%" echo {"model":"%MODELO_OFICIAL%","prompt":"Responde solo OK","stream":false}
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $body=Get-Content -Raw -LiteralPath '%GEN_PAYLOAD%'; $r=Invoke-RestMethod -Method Post -Uri '%OLLAMA_BASE_URL%/api/generate' -ContentType 'application/json' -Body $body -TimeoutSec 120; if (-not $r.response) { exit 2 }; $r ^| ConvertTo-Json -Compress ^| Out-File -Encoding utf8 '%RUNTIME_DIR%\laia_mistral_generate_response.json'; exit 0 } catch { Write-Error $_; exit 1 }" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] /api/generate fallo. Estado: FAILED
    set "STATUS=FAILED"
    call :write_status "FAILED" "generate_failed" "%MODELO_OFICIAL%"
    goto :fail
)
echo [OK] /api/generate responde.

echo [3/4] Probando /api/chat...
set "CHAT_PAYLOAD=%TEMP%\laia_chat_payload.json"
> "%CHAT_PAYLOAD%" echo {"model":"%MODELO_OFICIAL%","messages":[{"role":"system","content":"Responde de forma breve."},{"role":"user","content":"Responde solo OK"}],"stream":false}
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $body=Get-Content -Raw -LiteralPath '%CHAT_PAYLOAD%'; $r=Invoke-RestMethod -Method Post -Uri '%OLLAMA_BASE_URL%/api/chat' -ContentType 'application/json' -Body $body -TimeoutSec 120; if (-not $r.message.content) { exit 2 }; $r ^| ConvertTo-Json -Compress ^| Out-File -Encoding utf8 '%RUNTIME_DIR%\laia_mistral_chat_response.json'; exit 0 } catch { Write-Error $_; exit 1 }" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] /api/chat fallo. Estado: FAILED
    set "STATUS=FAILED"
    call :write_status "FAILED" "chat_failed" "%MODELO_OFICIAL%"
    goto :fail
)
echo [OK] /api/chat responde.

echo [4/4] Comprobando RAG/base de conocimiento...
if not exist "%KNOWLEDGE_DIR%\chroma.sqlite3" (
    echo [AVISO] Ollama y el modelo responden, pero falta RAG. Estado: KNOWLEDGE_MISSING
    set "STATUS=KNOWLEDGE_MISSING"
    call :write_status "KNOWLEDGE_MISSING" "knowledge_base_missing" "%MODELO_OFICIAL%"
    >> "%LOG_FILE%" echo Healthcheck ejecutado: %date% %time% - Modelo: %MODELO_OFICIAL% - Estado: KNOWLEDGE_MISSING
    popd >nul 2>&1
    pause
    exit /b 0
)

echo [OK] Base de conocimiento detectada.
set "STATUS=READY_LOCAL_AI"
call :write_status "READY_LOCAL_AI" "ok" "%MODELO_OFICIAL%"
>> "%LOG_FILE%" echo Healthcheck ejecutado: %date% %time% - Modelo: %MODELO_OFICIAL% - Estado: READY_LOCAL_AI
popd >nul 2>&1
pause
exit /b 0

:fail
>> "%LOG_FILE%" echo Healthcheck ejecutado: %date% %time% - Modelo: %MODELO_OFICIAL% - Estado: %STATUS%
popd >nul 2>&1
pause
exit /b 1

:write_status
set "JSON_STATUS=%~1"
set "JSON_REASON=%~2"
set "JSON_MODEL=%~3"
if "%JSON_MODEL%"=="" (
    echo {"status":"%JSON_STATUS%","reason":"%JSON_REASON%","checked_at":"%date% %time%"} > "%RUNTIME_DIR%\laia_mistral_status.json"
) else (
    echo {"status":"%JSON_STATUS%","reason":"%JSON_REASON%","model":"%JSON_MODEL%","checked_at":"%date% %time%"} > "%RUNTIME_DIR%\laia_mistral_status.json"
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
if not defined PY_CMD (
    echo [ERROR] Se requiere Python 3.12.x 64 bits. No se instalara Python desde este BAT.
    if defined LOG_FILE >> "%LOG_FILE%" echo [ERROR] Python 3.12.x 64 bits no detectado.
    exit /b 1
)
%PY_CMD% -c "import platform,sys; print('Python %s %s' % (sys.version.split()[0], platform.architecture()[0]))" >> "%LOG_FILE%" 2>&1
exit /b 0
