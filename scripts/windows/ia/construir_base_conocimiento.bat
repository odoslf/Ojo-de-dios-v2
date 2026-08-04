@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..\..") do set "PROJECT_ROOT=%%~fI"
set "PYTHON_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe"
set "SYSTEM_PYTHON=python"
set "BUILDER=%PROJECT_ROOT%\scripts\windows\ia\build_knowledge_base.py"
set "KNOWLEDGE_DIR=%PROJECT_ROOT%\storage\knowledge"
set "STATUS_FILE=%KNOWLEDGE_DIR%\knowledge_status.json"

echo ============================================================
echo   Ojo de Dios - Construccion de base de conocimiento IA
echo ============================================================
echo.
echo Este script NO descarga modelos ni llama APIs externas por defecto.
echo El modo 1 genera READY_DOCS_ONLY con Python estandar y artefactos auditables.
echo El modo 2 intenta READY_RAG semantico solo si instalas/tienes dependencias opcionales.
echo.

if not exist "%BUILDER%" (
  echo [ERROR] No encuentro el constructor: %BUILDER%
  exit /b 1
)

if not exist "%PROJECT_ROOT%\.venv" (
  echo [INFO] No existe .venv. Creando entorno virtual local...
  %SYSTEM_PYTHON% -m venv "%PROJECT_ROOT%\.venv"
  if errorlevel 1 (
    echo [ERROR] No se pudo crear .venv. Instala Python 3 y vuelve a ejecutar.
    exit /b 1
  )
)

if not exist "%PYTHON_EXE%" (
  echo [ERROR] No encuentro Python del entorno virtual: %PYTHON_EXE%
  exit /b 1
)

echo Selecciona modo de construccion:
echo   1^) READY_DOCS_ONLY - indice local JSON/JSONL sin dependencias externas
echo   2^) READY_RAG semantico - Chroma + embeddings si dependencias disponibles
set /p "KB_MODE_OPTION=Modo [1]: "
if "%KB_MODE_OPTION%"=="" set "KB_MODE_OPTION=1"

set "KB_MODE=docs-only"
if "%KB_MODE_OPTION%"=="2" set "KB_MODE=semantic"

if "%KB_MODE%"=="semantic" (
  echo.
  echo El modo semantico requiere paquetes opcionales: langchain, langchain-community,
  echo chromadb y sentence-transformers. Puede usar red si eliges instalarlos ahora.
  set /p "INSTALL_OPTIONAL=Instalar/actualizar dependencias opcionales ahora? [N/s]: "
  if /I "%INSTALL_OPTIONAL%"=="s" (
    "%PYTHON_EXE%" -m pip install --upgrade langchain langchain-community chromadb sentence-transformers
    if errorlevel 1 (
      echo [WARN] No se pudieron instalar dependencias opcionales. Se continuara y el constructor dejara constancia real.
    )
  ) else (
    echo [INFO] No se instalan dependencias opcionales. Si faltan, el resultado sera READY_DOCS_ONLY.
  )
)

if not exist "%KNOWLEDGE_DIR%" mkdir "%KNOWLEDGE_DIR%"

echo.
echo [INFO] Construyendo base de conocimiento en modo %KB_MODE%...
pushd "%PROJECT_ROOT%" >nul
"%PYTHON_EXE%" "%BUILDER%" --repo-root "%PROJECT_ROOT%" --output-dir "%KNOWLEDGE_DIR%" --mode "%KB_MODE%"
set "BUILD_RC=%ERRORLEVEL%"
popd >nul

if not "%BUILD_RC%"=="0" (
  echo [ERROR] La construccion de conocimiento fallo con codigo %BUILD_RC%.
  exit /b %BUILD_RC%
)

if not exist "%STATUS_FILE%" (
  echo [ERROR] Falta el manifiesto de estado: %STATUS_FILE%
  exit /b 1
)
if not exist "%KNOWLEDGE_DIR%\chunks.jsonl" (
  echo [ERROR] Falta el indice de fragmentos: %KNOWLEDGE_DIR%\chunks.jsonl
  exit /b 1
)
if not exist "%KNOWLEDGE_DIR%\source_manifest.json" (
  echo [ERROR] Falta el manifiesto de fuentes: %KNOWLEDGE_DIR%\source_manifest.json
  exit /b 1
)

echo.
echo [OK] Base de conocimiento construida correctamente.
echo      Estado: %STATUS_FILE%
echo      Fragmentos: %KNOWLEDGE_DIR%\chunks.jsonl
echo      Fuentes: %KNOWLEDGE_DIR%\source_manifest.json
echo.
endlocal
