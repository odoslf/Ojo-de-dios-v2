# Módulo 16 — Instalación de estación LaIA/Mistral

## Estado M16

Los Vectores 1 y 2 están documentados y pendientes de validación operativa en
Windows. El Módulo 16 no se considera cerrado hasta completar Vectores 3-10.

## Verdad única LaIA/Mistral

- Modelo oficial: `CognitiveComputations/dolphin-mistral-nemo:12b`.
- `MISTRAL_MODEL` siempre apunta al modelo oficial.
- `MISTRAL_SYSTEM_PROMPT_PATH` apunta a
  `docs/ai_prompts/laia_mistral_system_prompt.md` y el contenido de ese prompt
  debe enviarse en cada petición.
- `laia-mistral-con-prompt` es un alias opcional de prueba; no es el modelo
  oficial de producción.
- API Ollama documentada:
  - `POST http://localhost:11434/api/generate`
  - `POST http://localhost:11434/api/chat`
  - `GET http://localhost:11434/api/tags`
  - `GET http://localhost:11434/api/ps`

## Precedencia de variables IA

- `AI_ENABLED` es el interruptor global.
- `MISTRAL_ENABLED` y `ANGEL_ENABLED` solo se evalúan si `AI_ENABLED=1`.
- La estación puede estar instalada y lista con `AI_ENABLED=0`, pero la
  aplicación no debe usar IA hasta activarlo explícitamente.
- `.env.example` permanece seguro por defecto: sin secretos reales y con IA
  global desactivada.

## Requisitos

- Windows 10/11.
- Acceso a internet para descargar Ollama y el modelo oficial.
- PowerShell o CMD con permisos de usuario suficientes para instalar Ollama y
  configurar variables de entorno.

## Regla Codex / primera estación Windows

En el entorno de Codex no se instala Ollama ni se descarga el modelo. El repositorio
queda preparado y vinculado para que la primera estación real se haga después en
Windows desde el ZIP/copia final del proyecto. La descarga autorizada del modelo
solo ocurre cuando el operador ejecuta el BAT de instalación en esa estación.


## Instalador completo M16 desde ZIP

Para una estación nueva descargada como ZIP desde GitHub y extraída en Windows, el punto de entrada recomendado es:

```bat
scripts\windows\ia\instalar_modulo16_completo.bat
```

Ese BAT no contiene lógica ficticia: delega en los scripts reales de preflight, instalación de Ollama/modelo, healthcheck LaIA/Mistral, construcción de base de conocimiento y preparación/comprobación de Hermes Agent. Genera `storage\runtime\m16_full_install_status.json` y `storage\logs\ia\m16_full_install.log` para poder saber exactamente hasta dónde llegó la instalación.

Para arrancar la aplicación web en Windows después de extraer el ZIP de GitHub, usa:

```bat
scripts\windows\iniciar_ojo_de_dios_windows.bat
```

Ese arranque crea `.venv`, instala `requirements.txt`, crea `.env` desde `.env.example` si falta, prepara carpetas locales y abre la aplicación en `http://127.0.0.1:8000/modules`.

## Instalación

1. Abre una consola en la raíz del proyecto.
2. Ejecuta:

   ```bat
   scripts\windows\ia\instalar_laia_mistral.bat
   ```

3. Selecciona la opción `0` para preparar rutas, `.env`, `OLLAMA_MODELS`, logs, runtime y workspace sin descargar ni llamar APIs.
4. Selecciona la opción `1` para instalar/comprobar Ollama y descargar el modelo oficial único en Windows:
   `CognitiveComputations/dolphin-mistral-nemo:12b`.
5. Selecciona la opción `2` solo si quieres crear el alias opcional de prueba
   `laia-mistral-con-prompt`, sin cambiar `MISTRAL_MODEL`.
6. Selecciona la opción `4` para ejecutar el healthcheck.

## Rutas Ollama

- `OLLAMA_MODELS` es la variable persistente de Ollama en Windows.
- `OLLAMA_MODELS_DIR` es la ruta documental/configurable de Ojo de Dios.
- Ambas deben apuntar a `storage/models/ollama` cuando el operador configure la
  estación.

El instalador configura `OLLAMA_MODELS` con `setx` apuntando a
`storage\models\ollama`. Si es la primera ejecución, reinicia Ollama para que
lea la nueva ruta persistente.

## Rutas importantes

| Uso | Ruta |
| --- | --- |
| Modelos Ollama | `storage\models\ollama` |
| Logs IA | `storage\logs\ia` |
| Runtime/status | `storage\runtime` |
| Base de conocimiento | `storage\knowledge` |
| Prompt LaIA | `docs\ai_prompts\laia_mistral_system_prompt.md` |

## Scripts relacionados

| Script | Uso |
| --- | --- |
| `scripts\windows\ia\00_preparar_primera_estacion.bat` | Preflight de primera estación: crea rutas, `.env` si falta, prepara `OLLAMA_MODELS` y no descarga ni llama APIs. |
| `scripts\windows\ia\instalar_laia_mistral.bat` | Menú principal de instalación y verificación. |
| `scripts\windows\ia\01_instalar_ollama.bat` | Instalación o comprobación aislada de Ollama. |
| `scripts\windows\ia\04_aplicar_system_prompt.bat` | Crea el alias opcional `laia-mistral-con-prompt` desde el modelo oficial para pruebas. |
| `scripts\windows\ia\03_probar_mistral.bat` | Healthcheck local de modelo, prompt y base de conocimiento. |
| `scripts\windows\ia\construir_base_conocimiento.bat` | Construcción RAG usando `.venv\Scripts\python.exe`. |

## Errores comunes y soluciones

| Error | Causa probable | Solución |
| --- | --- | --- |
| Ollama no arranca | Servicio no iniciado o instalación incompleta. | Inicia Ollama manualmente, reinicia la sesión y ejecuta la opción `1`. |
| Puerto `11434` ocupado | Otro proceso usa el puerto de Ollama. | Cierra el proceso conflictivo o cambia la configuración antes del healthcheck. |
| `MISSING_TOOL` | Falta Ollama o Python en el flujo que se está ejecutando. | Instala la herramienta requerida y repite el script. |
| `MODEL_MISSING` | Ollama funciona, pero no está descargado el modelo oficial. | Ejecuta la opción `1` del instalador. |
| `KNOWLEDGE_MISSING` | No se ejecutó el constructor RAG. | Ejecuta `scripts\windows\ia\construir_base_conocimiento.bat` con `.venv`. |
| `KNOWLEDGE_STALE` | La base RAG existe, pero no refleja la documentación actual. | Reconstruye la base de conocimiento y registra la trazabilidad. |
| `PARTIAL` | El modelo responde, pero hay una dependencia no crítica incompleta. | Revisa el JSON de estado y completa la dependencia pendiente. |
| Prompt no detectado | El prompt contractual no se envió en la petición o el alias opcional no responde. | Verifica `MISTRAL_SYSTEM_PROMPT_PATH` y repite la prueba. |
| `FAILED` | Fallo bloqueante de Ollama, modelo o respuesta. | Revisa `storage\logs\ia\laia_mistral_healthcheck.log` y repite el paso fallido. |

## Estados posibles

| Estado | Significado |
| --- | --- |
| `READY_LOCAL_AI` | LaIA/Mistral está disponible localmente y el modelo oficial responde. |
| `KNOWLEDGE_MISSING` | Ollama y modelo responden, pero falta RAG. No debe marcarse como `FAILED` por sí solo. |
| `KNOWLEDGE_STALE` | Existe RAG, pero está obsoleto frente a documentación o registry. |
| `MODEL_MISSING` | Ollama está disponible, pero falta el modelo oficial. |
| `MISSING_TOOL` | Falta una herramienta requerida para la estación local. |
| `PARTIAL` | La estación responde, pero hay una dependencia no crítica incompleta. |
| `FAILED` | Fallo bloqueante; no usar para falta aislada de RAG si Ollama y modelo responden. |


## BAT real Windows — LaIA/Mistral

Ruta esperada del repositorio en Windows: `C:\Ojo-de-Dios`.

El BAT principal es:

```bat
scripts\windows\ia\instalar_laia_mistral.bat
```

Puede ejecutarse con doble clic desde `scripts\windows\ia\` o desde CMD en
cualquier carpeta. Todos los BAT resuelven la raíz con `%~dp0`, suben tres
niveles hasta el proyecto, hacen `pushd` a la raíz normalizada y verifican que
existe `.env.example`; si no existe, muestran `No estás dentro de Ojo de Dios`.

### Python 3.12

Los BAT usan primero `py -3.12` y, si no está disponible, `python`. La versión
exigida es Python 3.12.x de 64 bits. No instalan Python automáticamente; si falta
o no es 64 bits, el flujo se detiene con error claro.

### Ollama y modelo oficial

El modelo oficial sigue siendo:

```text
CognitiveComputations/dolphin-mistral-nemo:12b
```

La carpeta de modelos se fija en:

```text
C:\Ojo-de-Dios\storage\models\ollama
```

`01_instalar_ollama.bat` crea `storage\logs\ia`, `storage\runtime` y
`storage\models\ollama`, configura `OLLAMA_MODELS` para la sesión y con `setx`,
avisa que hay que reiniciar Ollama/CMD si no respeta la ruta, comprueba
`ollama --version`, abre la descarga oficial si falta Ollama y descarga el
modelo oficial con `ollama pull`.

### Healthcheck

`03_probar_mistral.bat` comprueba:

- `GET http://localhost:11434/api/tags`;
- `POST http://localhost:11434/api/generate` con `stream:false`;
- `POST http://localhost:11434/api/chat` con `stream:false`.

Guarda:

- `storage\runtime\laia_mistral_status.json`;
- `storage\logs\ia\laia_mistral_healthcheck.log`.

Si Ollama y el modelo responden pero falta RAG, el estado es
`KNOWLEDGE_MISSING` y el BAT termina con `exit /b 0`. Si falta herramienta,
modelo o API, usa `MISSING_TOOL`, `MODEL_MISSING` o `FAILED` y termina con
`exit /b 1`.

### Flujo privado funcional preservado

La opción `3. Ejecutar flujo privado funcional del usuario` permanece en el BAT
principal. El instalador no modifica el algoritmo privado: solo valida el chasis
antes de llamarlo, conserva rutas absolutas, usa `PY_CMD` y escribe log en:

```text
storage\logs\ia\laia_mistral_private_flow.log
```

Antes de ejecutar el flujo privado comprueba Ollama, el modelo base oficial,
Python 3.12 y `git` si el flujo lo necesita. El punto de entrada privado se toma
de `MISTRAL_PRIVATE_FLOW_CMD` o de un BAT privado local con uno de estos nombres:

- `scripts\windows\ia\flujo_privado_laia_mistral.bat`;
- `scripts\windows\ia\laia_mistral_private_flow.bat`;
- `scripts\windows\ia\abliterar_mistral_privado.bat`;
- `private\laia_mistral_private_flow.bat`.

Después de ejecutarlo, el BAT comprueba el modelo privado esperado en
`ollama list`. El nombre se toma de `MISTRAL_PRIVATE_MODEL`, de
`storage\runtime\laia_mistral_private_model.txt` o, si no se indica otro, de
`laia-mistral-privado`. Si existe, lo escribe en
`storage\runtime\laia_mistral_default_model.txt` y actualiza
`laia_mistral_status.json` con `PRIVATE_VARIANT_READY`. Si falla, no borra nada,
escribe `PRIVATE_VARIANT_FAILED` e indica el log.

### Prompt

`04_aplicar_system_prompt.bat` crea el alias opcional de prueba
`laia-mistral-con-prompt` solo si existe
`docs\ai_prompts\laia_mistral_system_prompt.md`. El modelo oficial sigue siendo
`CognitiveComputations/dolphin-mistral-nemo:12b`; la aplicación debe enviar el prompt de
`MISTRAL_SYSTEM_PROMPT_PATH` en cada petición. El BAT no cambia `MISTRAL_MODEL`
ni el modelo por defecto salvo elección explícita del usuario.

### Prueba manual recomendada

```bat
scripts\windows\ia\instalar_laia_mistral.bat
scripts\windows\ia\03_probar_mistral.bat
```
