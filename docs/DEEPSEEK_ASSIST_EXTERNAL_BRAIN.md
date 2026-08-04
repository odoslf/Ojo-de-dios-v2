DEEPSEEK ASSIST — EXTERNAL BRAIN WITH MINIMUM COST POLICY

Principio

DeepSeekAssist es un backend IA externo opcional para Ojo de Dios.

No sustituye a Mistral/LaIA.
No sustituye a X5/OjoRouter.
No sustituye a Hermes.
No ejecuta herramientas.
No instala herramientas.
No promociona técnicas.
No decide producción.

Su función es ayudar cuando Mistral/LaIA local no tenga suficiente conocimiento, contexto o capacidad para analizar una técnica nueva, CVE reciente, advisory, herramienta nueva, documentación grande o lógica moderna.

DeepSeekAssist debe diseñarse con política de gasto mínimo.

El usuario no quiere un sistema que gaste tokens de forma libre.
El objetivo es que funcione cuando sea necesario, pero usando el mínimo recurso posible.

Estado operativo externo

El usuario ya dispone de:

- API key de DeepSeek creada en su cuenta privada;
- crédito inicial aproximado de 10 € en DeepSeek;
- intención de usar DeepSeek solo como refuerzo externo de mínimo coste.

Reglas:

- no guardar la API key en el repositorio;
- no escribir la API key en documentación;
- no meter la API key real en ".env.example";
- no guardar una API key casi real;
- la futura configuración real irá en entorno local privado del usuario;
- la documentación solo debe hablar de variables futuras y placeholders falsos, nunca de valores reales.

Placeholder ficticio permitido para documentación:

DEEPSEEK_API_KEY=ALAZAN_REEMPLAZAR_EN_ENV_LOCAL

Roles oficiales

- Mistral/LaIA = cerebro operativo local.
- Hermes = manos operativas y agente constructor en laboratorio.
- DeepSeekAssist = cerebro externo de consulta cuando Mistral/LaIA no sabe.
- X5/OjoRouter = juez, validador y enrutador de ejecución.
- Usuario = aprobación final de producción.

Esquema oficial

Usuario define objetivo autorizado
↓
Mistral/LaIA interpreta, planifica y decide qué falta
↓
Si Mistral/LaIA sabe:
X5/OjoRouter valida y sigue el flujo normal
↓
Si Mistral/LaIA no sabe:
prepara una consulta mínima a DeepSeekAssist
↓
DeepSeekAssist investiga y devuelve JSON corto
↓
Mistral/LaIA interpreta la respuesta
↓
Hermes construye lo necesario en laboratorio:
wrapper
parser
schema
panel
instalador controlado
integración
informe de credibilidad
↓
X5/OjoRouter valida:
scope
permisos
modo
evidence
riesgo
registry
↓
Usuario aprueba producción si procede

Modelos DeepSeek

Modelos objetivo para futuras rondas:

- "deepseek-v4-flash";
- "deepseek-v4-pro".

Política obligatoria:

- "deepseek-v4-pro" es el modelo principal por defecto de Hermes Agent para calidad.
- "deepseek-v4-flash" queda reservado para healthcheck, resumen rápido, clasificación simple o fallback.
- "deepseek-v4-pro" puede usarse como modelo principal configurado; las llamadas externas siguen requiriendo AI_ENABLED, ANGEL_ENABLED y clave local.
- No debe existir auto-escalado automático fuera de los modelos configurados ni sin registrar motivo operativo.
- Toda llamada externa debe registrar motivo, modelo usado y contexto sanitizado.

Compatibilidad técnica esperada

DeepSeekAssist debe diseñarse como adaptador externo, no como dependencia central.

Capacidades esperadas de la API DeepSeek:

- formato API compatible con OpenAI para chat completion;
- modelos "deepseek-v4-flash" y "deepseek-v4-pro";
- JSON Output;
- Tool Calls / function calling;
- Context Caching;
- uso por tokens;
- endpoint externo configurable;
- API key por variable de entorno local privada.

La futura integración debe ocultarse detrás de un cliente propio, por ejemplo:

- DeepSeekClient;
- DeepSeekAssistService;
- ExternalBrainAdapter;
- DeepSeekCostGuard;
- DeepSeekCache;
- DeepSeekRequestMinifier.

Esta ronda no crea esos archivos. Solo reserva el camino.

Política de coste mínimo

Regla principal:

«Local primero. DeepSeek solo cuando sea estrictamente necesario.»

Orden obligatorio antes de llamar a DeepSeekAssist:

1. Consultar documentación local del repo.
2. Consultar Knowledge Bootstrap.
3. Consultar RAG/memoria local si existe.
4. Consultar EvidenceStore y resultados previos.
5. Consultar registry y contratos internos.
6. Usar Mistral/LaIA local.
7. Si sigue faltando conocimiento moderno o CVE reciente, pedir ayuda a DeepSeekAssist.

DeepSeekAssist no debe usarse para preguntas normales.
DeepSeekAssist no debe usarse para repetir información que ya está en el repo.
DeepSeekAssist no debe usarse para analizar el repositorio completo.
DeepSeekAssist no debe usarse en cada ejecución.
DeepSeekAssist no debe usarse como chat libre.

Uso permitido

DeepSeekAssist puede usarse de forma justificada cuando:

- aparece un CVE nuevo;
- aparece una técnica nueva;
- aparece una herramienta nueva;
- Mistral/LaIA devuelve baja confianza;
- falta contexto moderno;
- hay que comparar advisories;
- hay que analizar documentación técnica externa;
- hay que ayudar a Hermes a diseñar un wrapper, parser, schema o panel;
- hay que investigar cómo integrar una herramienta nueva en Ojo de Dios;
- hay que preparar una propuesta de laboratorio para Hermes;
- hay que generar JSON de investigación para que X5 lo valide.

Uso prohibido

DeepSeekAssist no debe usarse para:

- ejecutar comandos;
- lanzar herramientas;
- enviar secretos;
- enviar ".env";
- enviar cookies;
- enviar tokens;
- enviar contraseñas;
- enviar credenciales reales;
- enviar datos internos innecesarios;
- saltarse X5/OjoRouter;
- saltarse scope;
- saltarse kill switch;
- saltarse aprobación del usuario;
- enviar el repo entero;
- enviar documentación entera si basta un resumen;
- enviar logs completos si basta un extracto;
- generar gasto automático continuo.

Presupuesto inicial recomendado

Configuración conceptual futura:

- monthly_budget_eur: 10;
- monthly_budget_usd_equivalent: dynamic;
- daily_budget_usd: 0.25;
- hard_stop_on_budget: true;
- default_model: deepseek-v4-pro;
- fast_model: deepseek-v4-flash;
- auto_escalate_to_pro: false;
- deepseek_mode: manual;
- send_full_repo: false;
- send_full_docs: false;
- require_cost_estimate: true.

El presupuesto podrá subirse después si el usuario lo decide.

Perfiles de gasto futuros

OFF

DeepSeekAssist desactivado.

ULTRA_LOW

Perfil recomendado inicial.

- Solo manual.
- Usar `deepseek-v4-pro` como modelo principal configurado cuando Hermes Agent esté habilitado.
- Usar `deepseek-v4-flash` solo para healthcheck, resumen rápido, clasificación simple o fallback.
- No contexto completo.
- Solo snippets.
- Solo CVE/técnica/herramienta nueva.
- Presupuesto mensual bajo.
- Requiere motivo claro.

LOW

- DeepSeekAssist puede usarse de forma asistida.
- Sigue usando `deepseek-v4-pro` como modelo principal y `deepseek-v4-flash` solo para tareas rápidas/fallback.
- Presupuesto mensual moderado.
- Prohibido llamar a DeepSeek sin AI_ENABLED, ANGEL_ENABLED y clave local; `deepseek-v4-pro` es el modelo principal configurado.

CONTROLLED

- Se permite más contexto.
- Se permite DeepSeekAssist para propuestas Hermes más largas.
- Sigue existiendo presupuesto mensual.
- Sigue prohibido mandar secretos.

MANUAL_PRO

- Uso puntual de "deepseek-v4-pro".
- Requiere aprobación explícita del usuario.
- Requiere registrar motivo y coste estimado.

Reducción de tokens

DeepSeekAssist debe usar siempre estrategias de ahorro:

- resumir antes de enviar;
- enviar solo fragmentos relevantes;
- deduplicar contexto;
- usar cache local;
- usar hashes de documentos ya analizados;
- no reenviar documentación repetida;
- enviar IDs y extractos, no archivos completos;
- limitar salida esperada;
- pedir JSON corto;
- pedir unknowns y next_steps, no explicaciones largas;
- reutilizar resultados previos;
- cachear respuestas por CVE, tool_id, version y hash;
- cortar conversaciones largas;
- no mantener chat multi-turn si una llamada basta.

Contexto máximo recomendado

Valores conceptuales para futuras rondas:

- ultra_low_max_input_tokens: 20000;
- low_max_input_tokens: 50000;
- controlled_max_input_tokens: 150000;
- max_output_tokens_default: 2000;
- max_output_tokens_research: 4000;
- max_output_tokens_proposal: 6000.

No usar contexto de 1M tokens salvo aprobación explícita del usuario.

Flujo mínimo para CVE

Flujo futuro de mínimo coste:

1. Detectar CVE.
2. Consultar cache local por CVE ID.
3. Si existe resultado reciente, reutilizar.
4. Consultar NVD/CISA/EPSS/GitHub/fabricante mediante conectores normales.
5. Resumir localmente.
6. Pedir a Mistral/LaIA que analice el resumen.
7. Si Mistral/LaIA tiene confianza suficiente, no llamar a DeepSeek.
8. Si Mistral/LaIA no sabe, llamar a DeepSeekAssist con solo:
   - CVE ID;
   - productos afectados;
   - versiones relevantes;
   - resumen de fuentes;
   - fragmentos clave;
   - pregunta exacta;
   - formato JSON obligatorio.
9. Guardar respuesta en cache.
10. Pasar JSON validado a X5/OjoRouter.
11. Si falta capacidad, Hermes crea propuesta en laboratorio.

Sanitización obligatoria

Antes de llamar a DeepSeekAssist debe existir una capa futura de sanitización.

Nombres conceptuales reservados para futuras rondas:

- ContextSanitizer;
- SecretRedactor;
- TokenBudgetManager;
- ExternalBrainAuditLog;
- DeepSeekCostGuard;
- DeepSeekCache;
- DeepSeekRequestMinifier.

Debe eliminar o anonimizar:

- claves API;
- contraseñas;
- usuarios sensibles;
- tokens;
- cookies;
- secretos de proxy;
- rutas internas innecesarias;
- datos privados no requeridos.

Estados futuros reservados

Estados conceptuales para futuras rondas:

- DEEPSEEK_DISABLED;
- DEEPSEEK_AVAILABLE;
- DEEPSEEK_MANUAL_ONLY;
- DEEPSEEK_REQUESTED;
- DEEPSEEK_SKIPPED_LOCAL_SUFFICIENT;
- DEEPSEEK_SKIPPED_CACHE_HIT;
- DEEPSEEK_SKIPPED_BUDGET;
- DEEPSEEK_BUDGET_EXCEEDED;
- DEEPSEEK_RATE_LIMITED;
- DEEPSEEK_JSON_INVALID;
- DEEPSEEK_LOW_CONFIDENCE;
- DEEPSEEK_REVIEW_REQUIRED;
- DEEPSEEK_ASSIST_OK.

Modos futuros reservados

- off;
- manual;
- ultra_low;
- low;
- controlled;
- manual_pro.

Modo inicial recomendado: "manual" o "ultra_low".

Variables futuras previstas

Estas variables se documentan para futuras rondas.
No se implementan en esta ronda.

Ejemplo conceptual:

DEEPSEEK_ENABLED=1
DEEPSEEK_MODE=manual
DEEPSEEK_API_KEY=ALAZAN_REEMPLAZAR_EN_ENV_LOCAL
DEEPSEEK_MODEL=deepseek-v4-pro
DEEPSEEK_FAST_MODEL=deepseek-v4-flash
DEEPSEEK_PRO_MODEL=deepseek-v4-pro
DEEPSEEK_PRO_ENABLED=0
DEEPSEEK_AUTO_ESCALATE_TO_PRO=0
DEEPSEEK_MONTHLY_BUDGET_EUR=10
DEEPSEEK_DAILY_BUDGET_USD=0.25
DEEPSEEK_HARD_STOP_ON_BUDGET=1
DEEPSEEK_SEND_FULL_REPO=0
DEEPSEEK_SEND_FULL_DOCS=0
DEEPSEEK_REQUIRE_COST_ESTIMATE=1
DEEPSEEK_CACHE_ENABLED=1
DEEPSEEK_MAX_INPUT_TOKENS_ULTRA_LOW=20000
DEEPSEEK_MAX_OUTPUT_TOKENS_DEFAULT=2000

Salida obligatoria futura

DeepSeekAssist debe devolver JSON estructurado y validable.

Nada debe pasar a X5 como texto libre sin validación.

Ejemplo conceptual no implementable en esta ronda:

{
"kind": "external_research_assist",
"budget_profile": "ultra_low",
"model": "deepseek-v4-flash",
"confidence": 0.82,
"topic": "cve_or_tool_or_technique",
"summary": "",
"evidence_sources": [],
"affected_products": [],
"affected_versions": [],
"recommended_detection": [],
"recommended_lab_actions": [],
"requires_hermes": true,
"requires_user_approval": true,
"unknowns": [],
"risk_notes": [],
"estimated_cost_usd": 0.0,
"cache_key": ""
}

Regla final

DeepSeek no es el cerebro principal.
DeepSeek no es chat libre.
DeepSeek no se usa por comodidad.
DeepSeek se usa solo cuando aporta conocimiento externo necesario.

DeepSeek investiga y razona.
Mistral/LaIA decide si necesita ayuda.
Hermes construye si falta capacidad.
X5 valida.
El usuario aprueba producción.
