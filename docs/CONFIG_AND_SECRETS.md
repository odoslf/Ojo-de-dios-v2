# CONFIG AND SECRETS — OJO DE DIOS

## Principio

No guardar secretos reales en el repo.

`.env.example` debe incluir placeholders.

## Variables mínimas

```env
PRODUCT_DISPLAY_NAME=Ojo de Dios
DATABASE_URL=sqlite:///./storage/runtime/ojo_de_dios.sqlite3

INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=CAMBIAR_EN_PRIMER_ARRANQUE

AI_ENABLED=0
AI_BACKEND=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
MISTRAL_ENABLED=0
MISTRAL_MODEL=CognitiveComputations/dolphin-mistral-nemo:12b
MISTRAL_MODEL_DISPLAY_NAME=Dolphin Mistral Nemo 12B
MISTRAL_PROMPT_TEMPLATE=chatml
MISTRAL_CONTEXT_WINDOW_TOKENS=128000
MISTRAL_SYSTEM_PROMPT_PATH=docs/ai_prompts/laia_mistral_system_prompt.md
OLLAMA_MODELS=storage/models/ollama
OLLAMA_MODELS_DIR=storage/models/ollama

EVIDENCE_RETENTION_DAYS=90
JOB_LOG_RETENTION_DAYS=30
HERMES_EVIDENCE_RETENTION_DAYS=180
AUTO_CLEANUP_ENABLED=0

PLUGIN_DISCOVERY_ENABLED=1
PLUGIN_ENTRYPOINT_GROUP=ojo_de_dios.techniques

DEMO_MODE_DEFAULT=1
DEFAULT_EXECUTION_MODE=dry_run
```

## APIs privadas

Cualquier API privada debe estar en `.env` o settings local:

- Shodan;
- Censys;
- SecurityTrails;
- IntelX;
- Dehashed;
- cloud providers;
- SMTP;
- proxies;
- conectores privados;
- X4 local;
- plugins privados;
- DeepSeekAssist futuro.

## Regla

Nunca commitear:

- `.env` real;
- API keys;
- tokens;
- credenciales;
- certificados privados;
- dumps reales;
- evidence sensible real;
- archivos IQ sensibles;
- logs con secretos.


## DeepSeekAssist futuro

DeepSeekAssist se documenta como backend IA externo opcional de mínimo coste, pero esta ronda no lo implementa.

Reglas obligatorias futuras:

- no guardar API keys reales en el repositorio;
- no guardar API keys casi reales;
- no escribir la API key real en documentación;
- no tocar `.env.example` en la ronda documental 0-H;
- usar variable de entorno local privada cuando se implemente;
- no enviar secretos, `.env`, cookies, tokens, contraseñas ni credenciales a DeepSeekAssist;
- no enviar el repo completo;
- usar deepseek-v4-pro por defecto; deepseek-v4-flash para healthcheck/fallback;
- reservar deepseek-v4-flash para healthcheck, resumen rápido, clasificación simple o fallback.

Placeholder ficticio permitido en documentación normativa:

```env
DEEPSEEK_API_KEY=ALAZAN_REEMPLAZAR_EN_ENV_LOCAL
DEEPSEEK_API_KEY=ALAZAN_REEMPLAZAR_EN_ENV_LOCAL
```

Ese valor no es una clave real y solo indica que el usuario deberá sustituirlo en su `.env` local privado cuando exista implementación futura.
