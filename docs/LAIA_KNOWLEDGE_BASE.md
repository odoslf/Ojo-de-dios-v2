# LAIA KNOWLEDGE BASE — OJO DE DIOS

## Objetivo

LaIA debe conocer Ojo de Dios desde dentro.

Debe planificar usando conocimiento real del repositorio y del runtime, no suposiciones.

## Fuentes oficiales de conocimiento

LaIA debe poder consultar:

- README.md
- AI_HANDOFF_OJO_DE_DIOS.md
- MASTER_PLAN_OJO_DE_DIOS.md
- ROADMAP_RONDAS_OJO_DE_DIOS.md
- docs/
- storage/runtime/technique_registry.generated.json
- storage/runtime/technique_registry.generated.yaml
- storage/runtime/version_locks.json
- storage/runtime/tool_health.json
- storage/evidence/
- storage/hermes_lab/proposals/
- storage/hermes_lab/promoted/
- storage/plugins/
- storage/knowledge_base/

## Qué debe saber de cada módulo

Para cada módulo:

- module_id;
- nombre visible;
- finalidad;
- técnicas;
- herramientas;
- workers;
- panel;
- evidence;
- permisos;
- estado;
- relación con Attack Surface Graph;
- relación con Hermes;
- relación con LaIA;
- relación con X5/OjoRouter.

## Qué debe saber de cada técnica

Para cada técnica:

- technique_id;
- module_id;
- herramienta;
- versión recomendada;
- versión instalada;
- runtime;
- worker;
- permission_level;
- risk_level;
- required_inputs;
- optional_inputs;
- ai_fillable_inputs;
- panel_fields;
- expected_evidence;
- implementation_status;
- requires_user_implementation;
- requires_hardware;
- can_run_in_demo;
- can_run_in_dry_run;
- scoring histórico;
- errores frecuentes;
- evidence previa;
- plugins relacionados;
- propuestas Hermes relacionadas.

## Qué debe saber de cada herramienta

Para cada herramienta:

- tool_id;
- nombre;
- versión recomendada;
- versión instalada;
- ruta local;
- runtime;
- módulo;
- técnicas asociadas;
- wrapper;
- parser;
- formato de salida;
- healthcheck;
- VersionLock;
- documentación local;
- errores conocidos;
- evidence que produce.

## Regla de no invención

Si LaIA no encuentra algo en Knowledge Base, debe responder con uno de estos estados:

- UNKNOWN
- MISSING_DOC
- MISSING_TOOL
- MISSING_INPUT
- MISSING_PLUGIN
- MISSING_EVIDENCE
- IMPLEMENTACION_USUARIO_REQUERIDA
- HARDWARE_REQUIRED
- MANUAL_REQUIRED

No debe inventar herramientas, versiones, evidencias ni resultados.


## Extensión Ronda 0-F — Fuentes de ingesta obligatorias

La Knowledge Base debe indexar conocimiento con rutas, fechas, tipo de fuente, confianza y estado runtime. La ingesta oficial debe alinearse con [LAIA_HERMES_INGESTION_AND_EVOLUTION_BLUEPRINT.md](LAIA_HERMES_INGESTION_AND_EVOLUTION_BLUEPRINT.md) y [KNOWLEDGE_SOURCE_PRECEDENCE.md](KNOWLEDGE_SOURCE_PRECEDENCE.md).

Fuentes nuevas a contemplar:

- CVE intelligence cache normalizada;
- Kali tool catalog y futuras fichas `docs/tools/`;
- Hermes proposals y Hermes promoted con estado diferenciado;
- ToolHealth real;
- VersionLock real;
- EvidenceStore real;
- ScoringEngine real;
- Attack Surface Graph;
- plugins manifest;
- OSV/SBOM y Nuclei catalog si se aprueban en rondas futuras.

La Knowledge Base no debe indexar proposals no promocionadas como funcionales. Si una fuente es aspiracional, debe quedar marcada como `documented` o `proposal`, no como `available`.


## Extensión Ronda 0-G — Knowledge Bootstrap como origen inicial

La Knowledge Base nace desde Knowledge Bootstrap, no desde memoria de chat ni prompt gigante. Debe registrar source manifest, source precedence map, chunks, embeddings si existen, índices estructurados, resúmenes canónicos, estado de knowledge y relación con panel IA/Hermes Agent.

Reglas añadidas:

- Knowledge Bootstrap prepara el estado inicial.
- Knowledge Refresh mantiene el estado.
- No se indexan secretos, credenciales, tokens, cookies, dumps sensibles ni evidence marcada sensible.
- Cada fuente debe conservar ruta, tipo, hash/fecha si aplica y autoridad.
- El estado de knowledge debe exponer READY_DOCS_ONLY, READY_WITH_REGISTRY, STALE, FAILED, DEMO_ONLY u otros estados definidos en [AI_KNOWLEDGE_BOOTSTRAP_V1_REQUIREMENT.md](AI_KNOWLEDGE_BOOTSTRAP_V1_REQUIREMENT.md).
- El panel IA/Hermes Agent debe mostrar si LaIA puede operar, solo explicar documentación o degradar a demo.
