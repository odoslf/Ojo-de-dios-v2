# MASTER PLAN — OJO DE DIOS

## Decisiones cerradas

1. Son 16 módulos oficiales.
2. Módulo 9 es Scraping Inteligente X4 + X5 + IA.
3. DNS no es módulo independiente.
4. X5/OjoRouter manda.
5. Mistral/LaIA es cerebro operativo.
6. Hermes Agent Lab evoluciona en sandbox.
7. DeepSeekAssist es consulta externa opcional y de mínimo coste, no cerebro principal.
8. Mano de Dios es producto separado y no se integra en Ojo de Dios.
9. DeepSeekAssist/Hermes Tool Adoption, CVE-to-Technique, Supply Chain Sandbox y AI Research Gates forman parte de v0.1 Lab Core desde el diseño inicial, no de una versión 2.
10. EvidenceStore es obligatorio.
11. ScoringEngine es obligatorio.
12. VersionLock es obligatorio.
13. Kill Switch es obligatorio.
14. Demo mode es obligatorio.
15. Windows 10 LTSC es entorno principal.
16. SQLite primero, PostgreSQL preparado.
17. Registry Python + JSON/YAML generado.
18. Pantalla inicial = Nuevo objetivo.
19. IA principal = Ollama + Dolphin Mistral Nemo 12B.
20. llama.cpp preparado como alternativa.
21. Web responsive primero.
22. API Android preparada.
23. X4 se usa como conector de Scraping.
24. X5 existente se usa como referencia arquitectónica.
25. Hermes no es módulo 17.
26. Attack Surface Graph es capa transversal.
27. IMPLEMENTACION_USUARIO_REQUERIDA debe ser visible.
28. Tests solo funcionales, no moralizantes.
29. Tests dinámicos: prohibido bloquear por conteo fijo de técnicas, módulos, capabilities o wrappers salvo migración temporal documentada.

## Arquitectura general

Usuario
→ Nuevo Objetivo
→ TargetFingerprint
→ Attack Surface Graph si aplica
→ LaIA/Mistral interpreta
→ DeepSeekAssist investiga solo si LaIA/Mistral no llega
→ X5/OjoRouter valida
→ TechniqueRegistry
→ PolicyEngine
→ JobRunner
→ Worker
→ Technique hook
→ EvidenceStore
→ ScoringEngine
→ LaIA analiza
→ X5 decide siguiente paso
→ Hermes propone evolución si falta una pieza

## Criterio de éxito del chasis

El chasis estará bien hecho si:

- cada módulo tiene panel;
- cada técnica tiene archivo propio;
- cada técnica tiene clase propia;
- cada técnica tiene panel_fields propios;
- cada técnica tiene input_schema propio;
- cada técnica tiene worker correcto;
- cada técnica tiene evidence_contract;
- cada técnica tiene permission_level;
- cada técnica tiene demo/dry_run behavior;
- cada técnica tiene hook exacto de lógica privada si aplica;
- Mistral sabe explicar y rellenar campos;
- X5 sabe planificar y ejecutar por contratos;
- Hermes sabe proponer mejoras sin tocar producción;
- DeepSeekAssist solo ayuda si Mistral/LaIA no llega, con contexto mínimo, sin secretos y sin decidir ejecución.


## Política de tests dinámicos y registry ampliable

La política definitiva de tests dinámicos queda documentada en:

- [docs/DYNAMIC_REGISTRY_TESTING_POLICY.md](docs/DYNAMIC_REGISTRY_TESTING_POLICY.md)

Regla obligatoria:

“El registry de Ojo de Dios es dinámico. El número total de técnicas es una métrica informativa, no una condición bloqueante. Los tests validan invariantes y contratos de cada técnica registrada, no un conteo fijo.”

Quedan prohibidos tests como `assert len(techniques) == 240`, `assert len(techniques) == 242` o `assert total_modules == 16` como bloqueo absoluto de futuro. Los 16 módulos oficiales son base obligatoria, pero módulos adicionales aprobados, capabilities transversales o proposals Hermes no deben romper tests por existir.

Los tests correctos deben validar unicidad de IDs, formato, estados oficiales, permisos, `IMPLEMENTACION_USUARIO_REQUERIDA`, panel_schema, worker_contract, evidence_contract, ai_contract, ausencia de secretos, carga por X5/OjoRouter, exports JSON/YAML desde registry real y separación entre `proposal`, `sandbox`, `promoted` y `production`.

Esta regla aplica a TechniqueRegistry, CapabilityRegistry, ModuleRegistry, Hermes proposals, Tool Adoption Pipeline, CVE-to-Technique Pipeline, Ransomware Resilience Lab, Export JSON/YAML, Paneles, Workers, EvidenceStore y X5/OjoRouter.

## No crear stubs genéricos tontos

Prohibido registrar 240 técnicas con la misma plantilla vacía.

Cada técnica debe saber:

- qué campos necesita;
- qué worker usa;
- qué evidencia espera;
- qué permisos requiere;
- si Mistral puede rellenar parámetros;
- dónde debe conectar el usuario su lógica.

Ejemplos:

- Android debe tener campos Android/payload.
- HackRF debe tener campos SDR/RF.
- Scraping debe tener campos X4/fuentes/selectores.
- Cloud debe tener campos cloud/cluster/namespace/imagen.
- OSINT debe tener campos dominio/IP/fuentes.
- Web debe tener campos URL/headers/cookies/scope.

## Inventario técnico y sandbox

El mapa de herramientas, módulos, sandbox, Hermes Agent y límites de implementación queda definido en:

- [docs/TOOLS_AND_MODULES_IMPLEMENTATION_MAP.md](docs/TOOLS_AND_MODULES_IMPLEMENTATION_MAP.md)
- [docs/MODULE_TOOL_INVENTORY.md](docs/MODULE_TOOL_INVENTORY.md)
- [docs/HERMES_SANDBOX_CAPABILITIES.md](docs/HERMES_SANDBOX_CAPABILITIES.md)
- [docs/TECHNIQUE_CONNECTION_CONTRACT.md](docs/TECHNIQUE_CONNECTION_CONTRACT.md)
- [docs/SENSITIVE_LOGIC_BOUNDARIES.md](docs/SENSITIVE_LOGIC_BOUNDARIES.md)

## Documentación final de autosuficiencia

La definición real de producto, operación autónoma, UI, datos, configuración, criterios de aceptación, reglas de trabajo, herramientas oficiales, evidencia, plugins y control loop queda definida en:

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

Estas reglas cierran Ronda 0-C: no se sustituyen herramientas silenciosamente, no se suavizan técnicas, no se finge funcionalidad, no se oculta IMPLEMENTACION_USUARIO_REQUERIDA y el sistema debe poder crecer de 240 técnicas a 241, 300 o más sin romper arquitectura.

## Evolución modular

Ojo de Dios debe evolucionar mediante:

- técnicas internas;
- plugins pip;
- wrappers;
- parsers;
- workers;
- evidence writers;
- Hermes proposals;
- herramientas creadas en sandbox;
- migraciones controladas;
- VersionLock;
- release manifest.

Nada nuevo debe romper registry, evidence, X5, LaIA, Hermes, workers, paneles ni tests funcionales.

La evolución futura queda documentada en:

- [docs/FUTURE_UPDATES_AND_EVOLUTION.md](docs/FUTURE_UPDATES_AND_EVOLUTION.md)
- [docs/HERMES_PROMOTION_PIPELINE.md](docs/HERMES_PROMOTION_PIPELINE.md)
- [docs/PLUGIN_COMPATIBILITY_CONTRACT.md](docs/PLUGIN_COMPATIBILITY_CONTRACT.md)
- [docs/MODULE_EXTENSION_PLAYBOOK.md](docs/MODULE_EXTENSION_PLAYBOOK.md)
- [docs/TOOL_ADOPTION_PLAYBOOK.md](docs/TOOL_ADOPTION_PLAYBOOK.md)
- [docs/RELEASE_AND_MIGRATION_POLICY.md](docs/RELEASE_AND_MIGRATION_POLICY.md)
- [docs/BACKWARD_COMPATIBILITY_POLICY.md](docs/BACKWARD_COMPATIBILITY_POLICY.md)
- [docs/HERMES_CREATED_TOOLS_LIFECYCLE.md](docs/HERMES_CREATED_TOOLS_LIFECYCLE.md)

## Memoria y conocimiento de LaIA

Ojo de Dios debe crear una Knowledge Base local para LaIA.

LaIA debe conocer herramientas actuales y futuras consultando documentación e índices actualizados del repo y runtime.

LaIA debe usar context packs para no depender de prompts gigantes.

LaIA no se entrena primero con fine-tuning: primero se usa RAG local, JSON Schema, memoria estructurada, scoring, documentación de herramientas y evaluación.

La estrategia de conocimiento y aprendizaje queda documentada en:

- [docs/LAIA_KNOWLEDGE_BASE.md](docs/LAIA_KNOWLEDGE_BASE.md)
- [docs/LAIA_RAG_ARCHITECTURE.md](docs/LAIA_RAG_ARCHITECTURE.md)
- [docs/TOOL_DOCUMENTATION_INGESTION.md](docs/TOOL_DOCUMENTATION_INGESTION.md)
- [docs/LAIA_MEMORY_AND_SCORING.md](docs/LAIA_MEMORY_AND_SCORING.md)
- [docs/LOCAL_MODEL_BACKENDS.md](docs/LOCAL_MODEL_BACKENDS.md)
- [docs/FINE_TUNING_DECISION_POLICY.md](docs/FINE_TUNING_DECISION_POLICY.md)
- [docs/LAIA_EVALUATION_AND_GUARDRAILS.md](docs/LAIA_EVALUATION_AND_GUARDRAILS.md)
- [docs/KNOWLEDGE_REFRESH_PIPELINE.md](docs/KNOWLEDGE_REFRESH_PIPELINE.md)
- [docs/LAIA_CONTEXT_PACKS.md](docs/LAIA_CONTEXT_PACKS.md)


## Ronda 0-F — Ingesta LaIA/Hermes Agent, CVE Intelligence y evolución controlada

Queda cerrado que LaIA/Mistral y Hermes Agent no aprenden el sistema por prompt gigante ni por fine-tuning inicial. El camino oficial es Knowledge Base local, RAG, context packs mínimos, registry real, ToolHealth, VersionLock, EvidenceStore, ScoringEngine, CVE intelligence cache y propuestas Hermes Agent controladas.

Documentos normativos añadidos:

- [docs/LAIA_HERMES_INGESTION_AND_EVOLUTION_BLUEPRINT.md](docs/LAIA_HERMES_INGESTION_AND_EVOLUTION_BLUEPRINT.md)
- [docs/KNOWLEDGE_SOURCE_PRECEDENCE.md](docs/KNOWLEDGE_SOURCE_PRECEDENCE.md)
- [docs/VULNERABILITY_INTELLIGENCE_PIPELINE.md](docs/VULNERABILITY_INTELLIGENCE_PIPELINE.md)
- [docs/KALI_TOOL_KNOWLEDGE_CATALOG.md](docs/KALI_TOOL_KNOWLEDGE_CATALOG.md)
- [docs/HERMES_CVE_RESPONSE_PLAYBOOK.md](docs/HERMES_CVE_RESPONSE_PLAYBOOK.md)

Regla cerrada: LaIA recomienda, X5/OjoRouter valida y manda, Hermes propone en sandbox, Mistral revisa, el usuario aprueba y solo Promotion Pipeline + VersionLock + registry reload convierten una propuesta en capacidad disponible. La documentación aspiracional nunca equivale a funcionalidad real.


## Knowledge Bootstrap obligatorio v1

Knowledge Bootstrap para LaIA/Mistral y Hermes Agent es requisito de acabado de v1.

- No es v2.
- No es opcional.
- No es fine-tuning.
- LaIA/Hermes Agent deben arrancar con Knowledge Base local.
- El primer arranque debe preparar conocimiento del repo, registry, módulos, técnicas, herramientas, VersionLock, ToolHealth, EvidenceStore, ScoringEngine, CVE Intelligence, proposals Hermes Agent y promoted Hermes.
- El panel IA debe mostrar estado de Knowledge Base, Mistral/Ollama, embeddings, context packs, JSON schemas y Hermes Agent knowledge.
- X5 debe degradar o bloquear planes IA si Knowledge Base está STALE/FAILED o no llega al mínimo READY_WITH_REGISTRY.
- Hermes no debe crear proposals promocionables si su Knowledge Bootstrap no está OK.
- Fine-tuning queda como opción posterior solo si RAG/memoria/evaluación no bastan.

Documentos normativos:

- [docs/AI_KNOWLEDGE_BOOTSTRAP_V1_REQUIREMENT.md](docs/AI_KNOWLEDGE_BOOTSTRAP_V1_REQUIREMENT.md)
- [docs/AI_FIRST_RUN_KNOWLEDGE_LOAD.md](docs/AI_FIRST_RUN_KNOWLEDGE_LOAD.md)
- [docs/AI_KNOWLEDGE_REFRESH_AND_STATUS_PANEL.md](docs/AI_KNOWLEDGE_REFRESH_AND_STATUS_PANEL.md)
- [docs/HERMES_INITIAL_KNOWLEDGE_BOOTSTRAP.md](docs/HERMES_INITIAL_KNOWLEDGE_BOOTSTRAP.md)
- [docs/AI_TRAINING_VS_RAG_DECISION.md](docs/AI_TRAINING_VS_RAG_DECISION.md)

## Catálogos declarativos de módulos

- Módulo 1 OSINT: catálogo declarativo completo en docs/techniques/01_OSINT.md. Contiene 47 técnicas, integración X4/X5 para scraping inteligente, workers Windows/WSL2/API/Python/Browser/IA y salida hacia EvidenceStore, TargetFingerprint y Attack Surface Graph.

## Catálogo declarativo Vulnerabilidades

- Módulo 2 Vulnerabilidades: catálogo declarativo completo en docs/techniques/02_VULNERABILITIES.md. Este módulo no usa Docker; todo va por binarios Windows, Python, WSL2, API local o IA local. Contiene 19 técnicas y prepara handoff a explotación, web, credenciales, cloud y ops.

## Catálogo declarativo Network Exploitation

- Módulo 3 Explotación de Servicios de Red: catálogo declarativo completo en docs/techniques/03_NETWORK_EXPLOITATION.md. Este módulo no usa Docker; todo va por binarios Windows, Python, WSL2, API local o IA local. Contiene 73 técnicas divididas en 11 submódulos.

## Catálogo declarativo Web Intrusion

- Módulo 4 Intrusión Web Avanzada: catálogo declarativo completo en docs/techniques/04_WEB_INTRUSION.md. Este módulo no usa Docker; todo va por binarios Windows, Python, Node.js, WSL2, API local, proxies locales o IA local. Contiene 64 técnicas divididas en 9 submódulos.
