@echo off
setlocal enabledelayedexpansion
title Preparador Estacion Hermes Agent — Ojo de Dios

echo ============================================
echo   Preparador Estacion Hermes Agent — Ojo de Dios
echo ============================================
echo.

:: Crear carpetas del workspace
echo [1/4] Creando carpetas de laboratorio...
if not exist "modules\laboratory" mkdir "modules\laboratory"
if not exist "modules\laboratory\_inbox" mkdir "modules\laboratory\_inbox"
if not exist "modules\laboratory\_reviews" mkdir "modules\laboratory\_reviews"
if not exist "modules\laboratory\_sandbox" mkdir "modules\laboratory\_sandbox"
if not exist "modules\laboratory\_promoted_manifest" mkdir "modules\laboratory\_promoted_manifest"
if not exist "storage\logs\ia" mkdir "storage\logs\ia"
if not exist "storage\runtime" mkdir "storage\runtime"
echo [OK] Carpetas creadas.

:: Verificar Python
echo [2/4] Verificando Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    pause
    exit /b 1
)
echo [OK] Python detectado.

:: Verificar archivo .env
echo [3/4] Verificando configuracion...
if not exist ".env" (
    if exist ".env.example" (
        echo [AVISO] Archivo .env no encontrado. Copiando desde .env.example...
        copy ".env.example" ".env" >nul
        echo [OK] Archivo .env creado desde .env.example.
        echo [AVISO] Edita el archivo .env y añade tu DEEPSEEK_API_KEY.
    ) else (
        echo [ERROR] No se encontro .env ni .env.example.
        pause
        exit /b 1
    )
)

:: Verificar API key
echo [4/4] Verificando API key de DeepSeek...
for /f "tokens=1,2 delims==" %%a in ('findstr "DEEPSEEK_API_KEY" .env') do set "API_KEY=%%b"
if "%API_KEY%"=="" (
    echo [ERROR] DEEPSEEK_API_KEY no configurada en .env.
    echo Abre el archivo .env y añade tu clave API de DeepSeek.
    echo Luego ejecuta comprobar_angel_hermes.bat para verificar.
    pause
    exit /b 1
)
if "%API_KEY%"=="ALAZAN_REEMPLAZAR_EN_ENV_LOCAL" (
    echo [ERROR] DEEPSEEK_API_KEY tiene el valor de ejemplo. Cambialo por tu clave real.
    pause
    exit /b 1
)
echo [OK] API key configurada (no se muestra por seguridad).

:: Guardar estado inicial
echo {"workspace_ready":true,"api_key_present":true,"provider":"deepseek","sandbox_only":true,"checked_at":"%date% %time%","status":"READY_CONTROLLED"} > "storage\runtime\angel_hermes_status.json"

echo.
echo [OK] Estacion Hermes Agent preparada correctamente.
echo     Ahora ejecuta comprobar_angel_hermes.bat para verificar la conexion.
pause
exit /b 0
