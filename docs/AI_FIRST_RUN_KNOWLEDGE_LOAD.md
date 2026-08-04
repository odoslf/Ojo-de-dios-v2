# AI FIRST RUN KNOWLEDGE LOAD — OJO DE DIOS

## Propósito

Definir qué debe hacer el primer arranque de Ojo de Dios para dejar preparada la base de conocimiento local de LaIA/Mistral y Hermes Agent.

Este documento no implementa scripts, embeddings ni ejecución de modelos. Define el contrato de producto para futuras rondas.

## Flujo de primer arranque IA

El primer arranque debe preparar:

1. DB.
2. Settings.
3. Admin.
4. Storage.
5. Runtime folders.
6. Registry export.
7. ToolHealth inicial.
8. VersionLock inicial.
9. Knowledge source manifest.
10. Document chunks.
11. Embeddings si backend disponible.
12. Índices estructurados.
13. Context packs.
14. JSON Schema smoke check.
15. Hermes protocol check.
16. AI status panel data.
17. Demo/dry_run default mode.

## Fuentes iniciales

Fuentes mínimas:

- README.md
- MASTER_PLAN_OJO_DE_DIOS.md
- AI_HANDOFF_OJO_DE_DIOS.md
- ROADMAP_RONDAS_OJO_DE_DIOS.md
- docs/ARCHITECTURE_LOCK_OJO_DE_DIOS.md
- docs/DEFINITION_OF_DONE.md
- docs/LAIA_*.md
- docs/HERMES_*.md
- docs/X5_OJOROUTER_ENGINE.md
- docs/MODULE_TOOL_INVENTORY.md
- docs/TOOL_DOCUMENTATION_INGESTION.md
- docs/FUTURE_UPDATES_AND_EVOLUTION.md
- docs/KALI_TOOL_KNOWLEDGE_CATALOG.md si existe
- docs/VULNERABILITY_INTELLIGENCE_PIPELINE.md si existe
- docs/AI_KNOWLEDGE_BOOTSTRAP_V1_REQUIREMENT.md
- registry exportado
- tool catalog
- settings no secretas
- VersionLock
- ToolHealth
- Hermes promoted
- Hermes proposals como conocimiento no funcional
- EvidenceStore si ya hay evidence
- ScoringEngine si ya hay historial

## Fuentes excluidas

No indexar:

- .env real;
- secretos;
- contraseñas;
- tokens;
- cookies;
- claves API;
- credenciales proxy;
- dumps sensibles;
- evidence marcada como sensible;
- archivos binarios;
- logs con secretos;
- payloads privados;
- datos fuera de scope.

## Resultado esperado

El primer arranque debe dejar un resumen tipo:

- docs_indexed;
- chunks_created;
- embeddings_created;
- registry_indexed;
- tools_indexed;
- techniques_indexed;
- modules_indexed;
- hermes_protocol_loaded;
- context_packs_available;
- json_schema_ready;
- knowledge_status;
- warnings;
- missing_optional_items;
- missing_required_items;
- last_refresh_at.

## Modo sin embeddings

Si el backend de embeddings no está disponible:

- no romper arranque;
- marcar READY_DOCS_ONLY o READY_WITH_REGISTRY según proceda;
- permitir búsqueda textual simple;
- avisar en panel;
- impedir claims de RAG semántico completo;
- mantener demo/dry_run.

## Modo sin Mistral/Ollama

Si Mistral/Ollama no está disponible:

- no romper arranque base;
- marcar IA como MISSING_OPTIONAL o MISSING_REQUIRED según configuración;
- panel debe avisar;
- Knowledge Base puede prepararse parcialmente;
- X5 no debe depender de respuesta IA;
- Hermes no debe ejecutar review IA.

## Smoke check obligatorio

Debe existir comprobación conceptual futura:

- LaIA recibe pregunta sobre módulos oficiales.
- LaIA devuelve JSON válido.
- LaIA no inventa técnica.
- LaIA reconoce X5 como decisor.
- LaIA reconoce Hermes como sandbox.
- Hermes reconoce que no puede autoaprobar.
- Hermes reconoce IMPLEMENTACION_USUARIO_REQUERIDA.
- Knowledge source precedence se respeta.

## Fallo de primer arranque

Si el Knowledge Bootstrap falla, el sistema puede arrancar en demo, pero debe mostrar estado DEMO_ONLY, FAILED o PARTIAL y no presentar IA operativa como lista.
