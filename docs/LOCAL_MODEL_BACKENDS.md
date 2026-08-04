# LOCAL MODEL BACKENDS — OJO DE DIOS

## Backend principal

Ollama + `CognitiveComputations/dolphin-mistral-nemo:12b`.

La estación local LaIA/Mistral queda fijada al modelo Dolphin Mistral Nemo 12B y
no al antiguo modelo local de 7B. La descarga del modelo no se guarda en el
repositorio: se realiza durante la primera instalación controlada mediante los scripts de
Windows cuando el operador ejecute la opción correspondiente.

## Perfil del modelo oficial

- Modelo Ollama: `CognitiveComputations/dolphin-mistral-nemo:12b`.
- Nombre visible: `Dolphin Mistral Nemo 12B`.
- Plantilla de prompt: `chatml`.
- Ventana de contexto configurada: `128000` tokens.
- Prompt contractual: `docs/ai_prompts/laia_mistral_system_prompt.md`.
- API local Ollama: `http://localhost:11434` / `http://127.0.0.1:11434`.

## Backend alternativo

`llama.cpp` queda como alternativa futura y no debe confundirse con el backend
activo. Cualquier backend adicional debe pasar por VersionLock, ToolHealth,
contratos de configuración y pruebas antes de considerarse disponible.

## Reglas

- todo local por defecto;
- JSON estructurado obligatorio;
- schemas validados;
- temperatura baja para acciones operativas;
- contexto del proyecto vía Knowledge Base/RAG cuando esté construido;
- no usar texto libre para ejecutar;
- fallback si el modelo no responde;
- timeout configurable;
- no ejecutar si JSON no valida;
- no descargar modelos durante importación, tests ni arranque normal de la app.

## Variables actuales

```env
AI_ENABLED=0
AI_BACKEND=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
AI_REQUEST_TIMEOUT_SECONDS=30

MISTRAL_ENABLED=0
MISTRAL_API_URL=http://localhost:11434
MISTRAL_CHAT_API_URL=http://localhost:11434/api/chat
MISTRAL_MODEL=CognitiveComputations/dolphin-mistral-nemo:12b
MISTRAL_MODEL_DISPLAY_NAME=Dolphin Mistral Nemo 12B
MISTRAL_PROMPT_TEMPLATE=chatml
MISTRAL_CONTEXT_WINDOW_TOKENS=128000
MISTRAL_GUARDRAILS_REQUIRED=1
MISTRAL_TIMEOUT_SECONDS=120
MISTRAL_SYSTEM_PROMPT_PATH=docs/ai_prompts/laia_mistral_system_prompt.md
OLLAMA_MODELS=storage/models/ollama
OLLAMA_MODELS_DIR=storage/models/ollama
LAIA_MODE=local
LAIA_JSON_ONLY=1
```

## Instalación y descarga diferida

La aplicación queda preparada para primera instalación, pero no incluye pesos del
modelo ni intenta descargarlos automáticamente. El flujo previsto es:

1. El operador copia `.env.example` a `.env` y mantiene `AI_ENABLED=0` hasta que
   quiera activar IA local.
2. El operador ejecuta `scripts/windows/ia/instalar_laia_mistral.bat`.
3. La opción `Instalar/comprobar Ollama y descargar modelo oficial` llama a
   `scripts/windows/ia/01_instalar_ollama.bat`.
4. Ese script configura `OLLAMA_MODELS` hacia `storage/models/ollama`, comprueba
   `ollama` y ejecuta `ollama pull CognitiveComputations/dolphin-mistral-nemo:12b`.
5. El healthcheck `scripts/windows/ia/03_probar_mistral.bat` valida `/api/tags`,
   `/api/generate`, `/api/chat` y registra si falta la Knowledge Base.

## Modelos futuros

Se podrán añadir:

- modelos más grandes;
- modelos especializados;
- modelos de embeddings;
- modelos OCR;
- modelos de clasificación;
- modelos fine-tuned.

Siempre registrados en VersionLock y sin reemplazar el modelo oficial hasta que
exista una migración aprobada.

## Extensión Ronda 0-G — Backends locales y Bootstrap

Mistral/Ollama y embeddings backend son parte del estado IA, pero su ausencia no
debe romper el arranque base. Si Mistral/Ollama no está disponible, Knowledge
Base puede prepararse parcialmente y el panel debe mostrar `MISSING_OPTIONAL` o
`MISSING_REQUIRED` según configuración.

Si embeddings no está disponible, el sistema debe permitir `READY_DOCS_ONLY` o
`READY_WITH_REGISTRY` con búsqueda textual simple, sin afirmar RAG semántico
completo.
