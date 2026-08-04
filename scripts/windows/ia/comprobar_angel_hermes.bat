@echo off
setlocal enabledelayedexpansion
title Healthcheck Hermes Agent - Ojo de Dios

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..\..") do set "REPO_ROOT=%%~fI"
cd /d "%REPO_ROOT%" || exit /b 1

set "RUNTIME_DIR=%REPO_ROOT%\storage\runtime"
set "LOG_DIR=%REPO_ROOT%\storage\logs\ia"
set "STATUS_FILE=%RUNTIME_DIR%\angel_hermes_status.json"
set "LOG_FILE=%LOG_DIR%\angel_hermes_healthcheck.log"

if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ============================================
echo   Healthcheck Hermes Agent - Ojo de Dios
echo ============================================
echo.

echo [1/4] Verificando runtime Python...
set "PYTHON_CMD="
py -3.12 -c "import sys" >nul 2>&1
if "%ERRORLEVEL%"=="0" set "PYTHON_CMD=py -3.12"
if not defined PYTHON_CMD (
    python -c "import sys" >nul 2>&1
    if "%ERRORLEVEL%"=="0" set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
    echo [ERROR] No se encontro Python.
    echo {"status":"FAILED","reason":"python_missing","checked_at":"%date% %time%"} > "%STATUS_FILE%"
    echo Healthcheck Hermes Agent: %date% %time% - Estado: python_missing >> "%LOG_FILE%"
    exit /b 1
)

echo [2/4] Leyendo .env sin imprimir secretos...
if not exist "%REPO_ROOT%\.env" (
    echo [ERROR] Archivo .env no encontrado.
    echo {"status":"FAILED","reason":"env_missing","checked_at":"%date% %time%"} > "%STATUS_FILE%"
    echo Healthcheck Hermes Agent: %date% %time% - Estado: env_missing >> "%LOG_FILE%"
    exit /b 1
)

for /f "usebackq tokens=1,* delims==" %%A in ("%REPO_ROOT%\.env") do (
    if /i "%%A"=="DEEPSEEK_API_KEY" set "API_KEY=%%B"
    if /i "%%A"=="DEEPSEEK_API_URL" set "API_URL=%%B"
    if /i "%%A"=="DEEPSEEK_MODEL" set "MODEL=%%B"
    if /i "%%A"=="DEEPSEEK_FAST_MODEL" set "FAST_MODEL=%%B"
)
if not defined API_URL set "API_URL=https://api.deepseek.com"
if not defined MODEL set "MODEL=deepseek-v4-pro"
if not defined FAST_MODEL set "FAST_MODEL=deepseek-v4-flash"
if not defined API_KEY (
    echo [ERROR] DEEPSEEK_API_KEY no configurada.
    echo {"status":"MISSING_API_KEY","model":"%MODEL%","checked_at":"%date% %time%"} > "%STATUS_FILE%"
    echo Healthcheck Hermes Agent: %date% %time% - Estado: missing_api_key >> "%LOG_FILE%"
    exit /b 1
)

echo [3/4] Comprobando /models y /chat/completions...
set "RESULT_FILE=%TEMP%\angel_hermes_health_%RANDOM%.json"
set "PY_HEALTH=%TEMP%\angel_hermes_health_%RANDOM%.py"
> "%PY_HEALTH%" echo import json,os,sys,urllib.request;u=os.environ.get('API_URL','https://api.deepseek.com').rstrip('/');k=os.environ.get('API_KEY','');m=os.environ.get('MODEL','deepseek-v4-pro');f=os.environ.get('FAST_MODEL','deepseek-v4-flash');h={'Authorization':'Bearer '+k,'Content-Type':'application/json'}
>> "%PY_HEALTH%" echo try:
>> "%PY_HEALTH%" echo  r=urllib.request.urlopen(urllib.request.Request(u+'/models',headers=h,method='GET'),timeout=30); ids={i.get('id') for i in json.loads(r.read().decode()).get('data',[]) if isinstance(i,dict)}
>> "%PY_HEALTH%" echo  if m not in ids and f not in ids: print(json.dumps({'status':'MODEL_MISSING','model':m,'fast_model':f})); sys.exit(2)
>> "%PY_HEALTH%" echo  body=json.dumps({'model':f if f in ids else m,'messages':[{'role':'user','content':'Responde solo OK'}],'stream':False}).encode(); r=urllib.request.urlopen(urllib.request.Request(u+'/chat/completions',data=body,headers=h,method='POST'),timeout=30); c=json.loads(r.read().decode()).get('choices',[{}])[0].get('message',{}).get('content','')
>> "%PY_HEALTH%" echo  if 'OK' not in c.upper(): print(json.dumps({'status':'FAILED','reason':'unexpected_chat_response','model':m,'fast_model':f})); sys.exit(3)
>> "%PY_HEALTH%" echo  print(json.dumps({'status':'READY_CONTROLLED','model':m,'fast_model':f}))
>> "%PY_HEALTH%" echo except Exception as e:
>> "%PY_HEALTH%" echo  print(json.dumps({'status':'API_UNREACHABLE','model':m,'fast_model':f,'reason':e.__class__.__name__})); sys.exit(4)
%PYTHON_CMD% "%PY_HEALTH%" > "%RESULT_FILE%" 2>> "%LOG_FILE%"
del "%PY_HEALTH%" >nul 2>&1
set "CHECK_EXIT=%ERRORLEVEL%"
set /p CHECK_JSON=<"%RESULT_FILE%"
del "%RESULT_FILE%" >nul 2>&1

echo [4/4] Guardando estado real...
echo %CHECK_JSON% > "%STATUS_FILE%"
echo Healthcheck Hermes Agent: %date% %time% - Estado: %CHECK_JSON% >> "%LOG_FILE%"
if "%CHECK_EXIT%"=="0" (
    echo [OK] Healthcheck real correcto.
    exit /b 0
)
echo [ERROR] Healthcheck real fallido. Revisa %LOG_FILE%.
exit /b %CHECK_EXIT%
