# AI KNOWLEDGE REFRESH AND STATUS PANEL — OJO DE DIOS

## Propósito

Definir cómo Ojo de Dios refresca el conocimiento de LaIA/Mistral y Hermes Agent y cómo lo muestra al usuario.

Esta especificación es documental. No crea panel, backend ni embeddings en esta ronda.

## Cuándo refrescar

Debe refrescarse cuando cambie:

- README;
- MASTER_PLAN;
- AI_HANDOFF;
- docs/;
- registry;
- technique metadata;
- tool catalog;
- VersionLock;
- ToolHealth;
- EvidenceStore;
- ScoringEngine;
- Hermes proposals;
- Hermes promoted;
- plugins;
- CVE cache;
- Attack Surface Graph schema;
- JSON schemas;
- context pack definitions.

## Tipos de refresh

- manual_refresh;
- first_run_refresh;
- docs_only_refresh;
- registry_refresh;
- tool_catalog_refresh;
- evidence_refresh;
- scoring_refresh;
- hermes_refresh;
- cve_intelligence_refresh;
- full_refresh.

## Qué NO debe hacer refresh

No debe:

- ejecutar herramientas;
- lanzar scans;
- descargar modelos sin permiso;
- instalar dependencias;
- cambiar producción;
- promocionar Hermes;
- borrar evidence;
- borrar VersionLock;
- sobrescribir .env;
- indexar secretos.

## Panel de estado IA

Debe existir documentación para un panel futuro con:

- Mistral/Ollama status;
- embeddings backend status;
- Knowledge Base status;
- last refresh;
- docs indexed;
- chunks count;
- embeddings count;
- registry status;
- tools indexed;
- techniques indexed;
- modules indexed;
- context packs available;
- JSON schema status;
- Hermes Agent knowledge status;
- CVE cache status;
- ToolHealth status;
- VersionLock status;
- warnings;
- stale sources;
- missing required sources;
- missing optional sources;
- button refresh knowledge;
- button rebuild index;
- button validate LaIA JSON;
- button validate Hermes protocol.

## Estados visuales

- OK;
- WARNING;
- STALE;
- PARTIAL;
- FAILED;
- DISABLED;
- DEMO_ONLY.

## Regla de seguridad

El panel puede mostrar rutas y estados, pero no secretos.

No debe exponer tokens, claves API, cookies, credenciales, payloads privados ni evidence marcada como sensible.

## Integración con X5

X5 debe poder consultar:

- knowledge_status;
- last_refresh_at;
- context_pack_status;
- ai_json_schema_status;
- hermes_protocol_status.

Si algo está STALE o FAILED, X5 debe degradar a demo/dry_run o pedir confirmación según política.

## Integración con Hermes

Hermes solo puede crear proposals promocionables si:

- Hermes Agent knowledge status está OK;
- registry index está disponible;
- source precedence está cargado;
- contracts están cargados;
- promotion pipeline está cargado;
- approval policy está cargada.

## Resultado esperado del panel

El usuario debe poder saber si LaIA/Hermes Agent están listos, parcialmente listos, obsoletos o deshabilitados antes de confiar en planes, proposals o análisis.
