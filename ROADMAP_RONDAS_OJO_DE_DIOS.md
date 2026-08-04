# ROADMAP RONDAS — OJO DE DIOS

## Principio

La evolución de Ojo de Dios se hará por rondas controladas. Cada ronda debe dejar el repositorio en un estado coherente, revisable y documentado, sin fingir funcionalidad ni mezclar decisiones de arquitectura con ejecución real.

## Ronda 0 — Contexto maestro y memoria operativa

Objetivo: fijar documentación raíz, decisiones bloqueadas, mapa de módulos, roles de IA, X5/OjoRouter, Hermes, registry, plugins, extensibilidad y reglas de trabajo.

Alcance permitido:

- README inicial con orden obligatorio de lectura.
- AI handoff completo.
- Plan maestro.
- Roadmap de rondas.
- Bloqueo de arquitectura.
- Documentación de extensibilidad y plugins.
- Modelo operativo de LaIA/Mistral.
- Modelo de Hermes Lab.
- Modelo de X5/OjoRouter.
- Documento visible de IMPLEMENTACION_USUARIO_REQUERIDA.

Alcance prohibido:

- Implementar técnicas.
- Crear lógica ofensiva.
- Tocar ejecución real.
- Cambiar arquitectura funcional.
- Crear stubs de técnicas.
- Modificar tests o dependencias.


## Ronda 0-C — Autosuficiencia final y definición real de producto

Objetivo: cerrar la documentación estratégica para que el repositorio explique por sí mismo qué se construye, cómo debe acabar el programa, cómo operan LaIA/X5/Hermes, cómo se integran herramientas, cómo se protegen herramientas oficiales, cómo se crean plugins, cómo se separa chasis de lógica privada y qué significa funcionalidad real con evidence.

Documentos de cierre:

- [docs/DEFINITION_OF_DONE.md](docs/DEFINITION_OF_DONE.md)
- [docs/UI_FLOWS.md](docs/UI_FLOWS.md)
- [docs/DATA_MODEL.md](docs/DATA_MODEL.md)
- [docs/CONFIG_AND_SECRETS.md](docs/CONFIG_AND_SECRETS.md)
- [docs/MODULE_ACCEPTANCE_CRITERIA.md](docs/MODULE_ACCEPTANCE_CRITERIA.md)
- [docs/CODEX_WORKING_RULES.md](docs/CODEX_WORKING_RULES.md)
- [docs/OFFICIAL_TOOLS_AND_UPGRADE_POLICY.md](docs/OFFICIAL_TOOLS_AND_UPGRADE_POLICY.md)
- [docs/AUTONOMOUS_OPERATION_ENDSTATE.md](docs/AUTONOMOUS_OPERATION_ENDSTATE.md)
- [docs/HERMES_AUTONOMOUS_EVOLUTION_PROTOCOL.md](docs/HERMES_AUTONOMOUS_EVOLUTION_PROTOCOL.md)
- [docs/REALITY_AND_EVIDENCE_POLICY.md](docs/REALITY_AND_EVIDENCE_POLICY.md)
- [docs/PLUGIN_AND_TOOL_CREATION_PROTOCOL.md](docs/PLUGIN_AND_TOOL_CREATION_PROTOCOL.md)
- [docs/LAIA_X5_HERMES_CONTROL_LOOP.md](docs/LAIA_X5_HERMES_CONTROL_LOOP.md)

Alcance prohibido: implementar lógica funcional, crear técnicas reales, crear payloads reales, ejecutar herramientas, instalar dependencias, modificar requirements, crear tests, cambiar módulos, cambiar el Módulo 9, crear DNS como módulo independiente, sustituir herramientas u ocultar IMPLEMENTACION_USUARIO_REQUERIDA.


## Ronda 0-D — Protocolo de actualizaciones, expansión modular, plugins y promoción de creaciones Hermes

Debe ejecutarse después de Ronda 0-C y antes de iniciar auditoría X4/X5.

Objetivo: documentar cómo Ojo de Dios añadirá nuevas técnicas, herramientas, módulos o submódulos, plugins pip y creaciones Hermes sin romper arquitectura ni tocar 50 archivos manualmente.

Documentos de cierre:

- [docs/FUTURE_UPDATES_AND_EVOLUTION.md](docs/FUTURE_UPDATES_AND_EVOLUTION.md)
- [docs/HERMES_PROMOTION_PIPELINE.md](docs/HERMES_PROMOTION_PIPELINE.md)
- [docs/PLUGIN_COMPATIBILITY_CONTRACT.md](docs/PLUGIN_COMPATIBILITY_CONTRACT.md)
- [docs/MODULE_EXTENSION_PLAYBOOK.md](docs/MODULE_EXTENSION_PLAYBOOK.md)
- [docs/TOOL_ADOPTION_PLAYBOOK.md](docs/TOOL_ADOPTION_PLAYBOOK.md)
- [docs/RELEASE_AND_MIGRATION_POLICY.md](docs/RELEASE_AND_MIGRATION_POLICY.md)
- [docs/BACKWARD_COMPATIBILITY_POLICY.md](docs/BACKWARD_COMPATIBILITY_POLICY.md)
- [docs/HERMES_CREATED_TOOLS_LIFECYCLE.md](docs/HERMES_CREATED_TOOLS_LIFECYCLE.md)

Alcance prohibido: tocar `app/`, lógica funcional, `tests/`, requirements, herramientas reales, plugins reales, stubs, módulos oficiales, Módulo 9, DNS como módulo independiente, herramientas oficiales o IMPLEMENTACION_USUARIO_REQUERIDA.


## Ronda 0-E FINAL — LaIA Knowledge Base, RAG local, memoria operativa y aprendizaje controlado

Debe ejecutarse después de Ronda 0-D y antes de auditoría X4/X5.

Objetivo: documentar cómo LaIA/Mistral conoce el sistema mediante Knowledge Base local, RAG, documentación, registry, ToolHealth, VersionLock, EvidenceStore, ScoringEngine, Hermes proposals, plugins, JSON Schema, memoria estructurada y context packs, dejando fine-tuning como opción futura.

Documentos de cierre:

- [docs/LAIA_KNOWLEDGE_BASE.md](docs/LAIA_KNOWLEDGE_BASE.md)
- [docs/LAIA_RAG_ARCHITECTURE.md](docs/LAIA_RAG_ARCHITECTURE.md)
- [docs/TOOL_DOCUMENTATION_INGESTION.md](docs/TOOL_DOCUMENTATION_INGESTION.md)
- [docs/LAIA_MEMORY_AND_SCORING.md](docs/LAIA_MEMORY_AND_SCORING.md)
- [docs/LOCAL_MODEL_BACKENDS.md](docs/LOCAL_MODEL_BACKENDS.md)
- [docs/FINE_TUNING_DECISION_POLICY.md](docs/FINE_TUNING_DECISION_POLICY.md)
- [docs/LAIA_EVALUATION_AND_GUARDRAILS.md](docs/LAIA_EVALUATION_AND_GUARDRAILS.md)
- [docs/KNOWLEDGE_REFRESH_PIPELINE.md](docs/KNOWLEDGE_REFRESH_PIPELINE.md)
- [docs/LAIA_CONTEXT_PACKS.md](docs/LAIA_CONTEXT_PACKS.md)

Alcance prohibido: tocar `app/`, `tests/`, lógica funcional, requirements, modelos, descargas, embeddings reales, ejecución de Mistral/Ollama, módulos, técnicas, DNS independiente, Módulo 9 o lógica privada.

## Rondas futuras previstas

### Ronda 1 — Auditoría de estado real

Estado: cerrada como auditoría documental verificable.

Entregable:

- [docs/RONDA_01_AUDITORIA_ESTADO_REAL.md](docs/RONDA_01_AUDITORIA_ESTADO_REAL.md)

Resultado: se revisó el estado real del repositorio, se ejecutó baseline de pruebas y se dejaron gaps priorizados para Ronda 2 sin implementar técnicas, sin instalar herramientas externas del operador y sin crear stubs.

### Ronda 2 — Registry y contratos

Definir TechniqueRegistry, contratos de técnica, estados oficiales, permisos oficiales y representación de panel_fields/input_schema/evidence_contract.

### Ronda 3 — X5/OjoRouter base

Implementar la orquestación por contratos: validación, modo, permisos, scope, job state y evidence mínima.

### Ronda 4 — LaIA/Mistral estructurada

Conectar salida JSON validada, schemas, validadores y explicación operativa sin comandos libres.

### Ronda 5 — EvidenceStore, ScoringEngine y VersionLock

Persistir evidencia, versionado de herramientas/plugins y aprendizaje de resultados.

### Ronda 6 — Panel web responsive y API Android-ready

Construir Nuevo objetivo, Dashboard y vistas de técnica con estados reales.

### Ronda 7 — Hermes Lab sandbox

Crear flujo de propuestas, sandbox, tests estructurales, revisión, diff y aprobación.

### Ronda 8 — Módulos oficiales y técnicas declarativas

Añadir técnicas con contratos específicos por módulo, sin plantillas vacías genéricas y manteniendo IMPLEMENTACION_USUARIO_REQUERIDA donde aplique.

### Ronda 9 — Plugins pip y extensibilidad

Activar plugin_manager, plugin_contract, plugin_registry y entry points oficiales.

### Ronda 10 — Endurecimiento operativo

Validar kill switch, modos demo/dry_run/controlled/expert, healthcheck, diagnósticos, documentación y mantenimiento.

## Regla de promoción entre rondas

Una ronda solo queda cerrada cuando:

- no contradice las decisiones cerradas;
- no oculta IMPLEMENTACION_USUARIO_REQUERIDA;
- no rompe el índice de 16 módulos;
- no crea ejecución real por defecto;
- no introduce tests moralizantes;
- conserva evidencia documental de lo cambiado.


## Ronda 0-F — Documentación de ingesta y evolución controlada

Estado: documentación estratégica cerrada.

Entregables:

- Blueprint de ingesta LaIA/Hermes y evolución controlada.
- Precedencia de fuentes cuando hay contradicciones.
- Pipeline documental de CVE intelligence.
- Catálogo documental para Kali/tools futuras.
- Playbook Hermes para respuesta a CVE nueva.

Esta ronda no implementa funcionalidad, no crea técnicas, no crea workers, no crea IA, no cambia módulos oficiales y no convierte proposals en producción. Prepara rondas futuras para implementar Knowledge Base, ToolHealth, VersionLock, EvidenceStore, ScoringEngine, Attack Surface Graph y CVE intelligence sin tocar 50 archivos ni romper arquitectura.


## Ronda 0-G — Knowledge Bootstrap obligatorio v1 para LaIA/Mistral y Hermes

Objetivo:
Documentar que Ojo de Dios v1 debe incluir precarga/refresco local de conocimiento para LaIA/Mistral y Hermes, panel de estado IA, context packs, JSON validado, decisión RAG antes que fine-tuning y checks de comprensión Hermes.

Archivos creados:

- docs/AI_KNOWLEDGE_BOOTSTRAP_V1_REQUIREMENT.md
- docs/AI_FIRST_RUN_KNOWLEDGE_LOAD.md
- docs/AI_KNOWLEDGE_REFRESH_AND_STATUS_PANEL.md
- docs/HERMES_INITIAL_KNOWLEDGE_BOOTSTRAP.md
- docs/AI_TRAINING_VS_RAG_DECISION.md

Alcance prohibido:
No código, no tests, no requirements, no instalación, no embeddings reales, no ejecución Mistral/Ollama, no tools, no CVE fetch, no módulos/técnicas.

Esta ronda es documental, pero su contenido será obligatorio para considerar v1 acabada.

## Ronda 0-H DEFINITIVA — Documentación normativa DeepSeekAssist, Mistral cerebro, Hermes manos, ofensiva autorizada y separación Mano de Dios

Estado: documentación normativa cerrada.

Objetivo:
Fijar que Ojo de Dios es una plataforma ofensiva de auditoría interna autorizada, que Mistral/LaIA es el cerebro operativo local, que Hermes son las manos constructoras en laboratorio, que DeepSeekAssist será una consulta externa opcional de mínimo coste y que Mano de Dios queda separado.

Archivos creados:

- docs/AUTHORIZED_OFFENSIVE_DOCTRINE.md
- docs/DEEPSEEK_ASSIST_EXTERNAL_BRAIN.md
- docs/HERMES_DEEPSEEK_EVOLUTION_PIPELINE.md
- docs/MANO_DE_DIOS_SEPARATION.md

Alcance prohibido:
No código, no app, no tests, no requirements, no pyproject, no scripts, no tools, no conectores, no cliente API, no workers, no schemas funcionales, no rutas, no herramientas, no instalaciones, no lógica ofensiva y no secretos.

Reglas fijadas:

- No se bloquean técnicas por nombres ni palabras.
- El control correcto es scope, allowlist, permisos, execution_mode, evidence, kill switch, VersionLock, ToolHealth, audit log y aprobación del usuario.
- DeepSeekAssist usa deepseek-v4-pro por defecto para Ángel/Hermes; deepseek-v4-flash queda para healthcheck, resumen rápido, clasificación simple o fallback.
- deepseek-v4-pro es el modelo principal de calidad para Ángel/Hermes cuando esté habilitado; toda llamada externa debe quedar registrada y sanitizada.
- DeepSeekAssist nunca recibe repo entero ni secretos.
- X5/OjoRouter valida todo antes de ejecución.
- El usuario aprueba cualquier promoción a producción.
- Mano de Dios no se integra dentro de Ojo de Dios.

## Ronda documentación — DeepSeekAssist + Hermes Tool Adoption Pipeline + CVE-to-Technique Pipeline

Estado: documentación normativa cerrada.

Objetivo:
Documentar arquitectura definitiva para que DeepSeekAssist, Hermes Lab, Mistral/LaIA y X5/OjoRouter investiguen, preparen, prueben en sandbox, validen y promocionen nuevas técnicas, herramientas y CVEs de forma controlada.

Archivos creados:

- docs/DEEPSEEK_ASSIST_HERMES_PIPELINE.md
- docs/HERMES_TOOL_ADOPTION_PIPELINE.md
- docs/CVE_TO_TECHNIQUE_PIPELINE.md
- docs/SUPPLY_CHAIN_SANDBOX_POLICY.md
- docs/AI_RESEARCH_GATES.md
- docs/DECISION_LOG_DEEPSEEK_HERMES.md

Regla cerrada:
Research → Quarantine → Analyze → Build → Sandbox Test → Evidence → Review → Approval → Promotion.

Alcance prohibido:
No código productivo, no lógica ejecutable, no dependencias, no requirements, no workers reales, no repos externos clonados, no red real y no tests bloqueantes por nombres/categorías/juicios externos.

Nota v0.1:
Esta arquitectura forma parte de Ojo de Dios v0.1 Lab Core desde el diseño inicial, no de una versión 2.

## Corrección obligatoria — tests dinámicos y registry ampliable

Estado: documentación normativa cerrada.

Documento añadido:

- docs/DYNAMIC_REGISTRY_TESTING_POLICY.md

Regla definitiva:
“El registry de Ojo de Dios es dinámico. El número total de técnicas es una métrica informativa, no una condición bloqueante. Los tests validan invariantes y contratos de cada técnica registrada, no un conteo fijo.”

Prohibido en rondas futuras:

- tests bloqueantes basados en conteo exacto fijo de técnicas, módulos, capabilities o wrappers;
- tests que fallen porque aparece una técnica nueva legítima;
- tests que fallen porque Hermes creó una proposal nueva;
- tests por nombres, categorías, palabras o juicios externos no funcionales;
- tests que obliguen a borrar técnicas nuevas legítimas.

Permitido y obligatorio:

- conteos como métrica informativa;
- mínimos esperados cuando tenga sentido;
- validación de invariantes por técnica;
- `technique_id` único;
- estados oficiales;
- permisos oficiales;
- `IMPLEMENTACION_USUARIO_REQUERIDA` en técnicas sensibles sin lógica privada;
- ausencia de secretos en metadata;
- carga completa por X5/OjoRouter;
- separación entre proposal, sandbox, promoted y production.

Aplica a TechniqueRegistry, CapabilityRegistry, ModuleRegistry, Hermes proposals, Tool Adoption Pipeline, CVE-to-Technique Pipeline, Ransomware Resilience Lab, Export JSON/YAML, Paneles, Workers, EvidenceStore y X5/OjoRouter.

## Rondas documentales OSINT — Módulo 1

- Ronda 0-F1 — OSINT catálogo declarativo completo.
- Ronda 0-F1-CLOSE — Cierre final OSINT con LaIA, X5, Hermes, EvidenceStore y Attack Surface Graph.

## Rondas documentales Vulnerabilidades — Módulo 2

- Ronda 0-F2A — Vulnerabilidades catálogo parte 1/2.
- Ronda 0-F2B — Vulnerabilidades catálogo parte 2/2.
- Ronda 0-F2-CLOSE-1 — Vulnerabilidades adapters y conexiones.
- Ronda 0-F2-CLOSE-2 — Cierre final Vulnerabilidades.

Nota correctiva:

- Módulo 2 Vulnerabilidades no usa Docker en esta versión. Runtime permitido: Windows, Python, WSL2, API local e IA local.

## Rondas documentales Network Exploitation — Módulo 3

- Ronda 0-F3A — Network Exploitation catálogo parte 1/5.
- Ronda 0-F3B — Network Exploitation catálogo parte 2/5.
- Ronda 0-F3C — Network Exploitation catálogo parte 3/5.
- Ronda 0-F3D — Network Exploitation catálogo parte 4/5.
- Ronda 0-F3E — Network Exploitation catálogo parte 5/5.

Nota correctiva:

- Módulo 3 Explotación de Servicios de Red no usa Docker en esta versión. Runtime permitido: Windows, Python, WSL2, API local e IA local.

## Rondas documentales Web Intrusion — Módulo 4

- Ronda 0-F4A — Web Intrusion catálogo parte 1/5.
- Ronda 0-F4B — Web Intrusion catálogo parte 2/5.
- Ronda 0-F4C — Web Intrusion catálogo parte 3/5.
- Ronda 0-F4D — Web Intrusion catálogo parte 4/5.
- Ronda 0-F4E — Web Intrusion catálogo parte 5/5.

Nota correctiva:

- Módulo 4 Intrusión Web Avanzada no usa Docker en esta versión. Runtime permitido: Windows, Python, Node.js, WSL2, API local, proxy local e IA local.
