# LAIA / HERMES INGESTION AND EVOLUTION BLUEPRINT — OJO DE DIOS

## Propósito

Explicar cómo Ojo de Dios convierte documentación, herramientas, CVE, evidencias y resultados en conocimiento usable por LaIA/Mistral y Hermes Agent.

Este documento cierra la regla estratégica: LaIA/Mistral y Hermes Agent deben entender el repositorio por capas verificables, no por memoria informal, promesas futuras ni inferencias del modelo.

## Decisión principal

Primero RAG local + JSON Schema + memoria estructurada + scoring.

Fine-tuning queda como opción futura y solo si RAG/memoria/evaluación no bastan. El fine-tuning no sustituye registry, EvidenceStore, VersionLock, ToolHealth, permisos, scope, approvals ni validación por X5/OjoRouter.

## Responsabilidad de LaIA/Mistral

LaIA debe:

- interpretar intención del usuario;
- leer context packs;
- consultar Knowledge Base;
- entender target y scope;
- entender Attack Surface Graph;
- proponer planes con técnicas registradas;
- rellenar parámetros permitidos;
- explicar paneles;
- analizar evidence;
- pedir fallback a X5;
- pedir evolución a Hermes cuando falte una pieza;
- devolver siempre JSON validado para acciones operativas.

LaIA no debe:

- ejecutar comandos libres;
- inventar técnicas;
- inventar herramientas;
- inventar versiones;
- inventar evidencias;
- marcar éxito sin EvidenceStore;
- saltarse X5/OjoRouter;
- saltarse permisos;
- saltarse mode demo/dry_run/controlled/expert;
- saltarse allowlist/scope;
- sustituir una técnica oficial por otra sin documentarlo.

## Responsabilidad de X5/OjoRouter

X5 debe:

- validar plan LaIA;
- validar JSON;
- validar registry;
- validar permisos;
- validar modo;
- validar scope/allowlist;
- decidir worker;
- decidir fallback;
- bloquear si falta evidencia;
- enviar a Hermes una petición de evolución si procede;
- registrar resultados en EvidenceStore;
- actualizar ScoringEngine.

X5 manda la ejecución. LaIA recomienda. Hermes propone. Usuario aprueba.

## Responsabilidad de Hermes

Hermes debe evolucionar el sistema en sandbox.

Hermes puede crear:

- propuestas;
- wrappers;
- parsers;
- schemas;
- panel fields;
- fixtures;
- tests estructurales;
- documentación;
- conectores;
- tools internas de laboratorio;
- plugins preparados;
- plantillas de detección controlada;
- hooks con IMPLEMENTACION_USUARIO_REQUERIDA.

Hermes no puede:

- ejecutar producción;
- autoaprobarse;
- tocar producción sin promoción;
- activar lógica sensible;
- instalar plugins sin aprobación;
- saltarse X5;
- saltarse EvidenceStore;
- saltarse VersionLock;
- saltarse Kill Switch;
- marcar una propuesta como funcional si solo es stub.

## Fuentes que deben ingerirse

La Knowledge Base y el índice RAG deben poder incorporar, con metadatos y rutas de origen:

- README.md
- AI_HANDOFF_OJO_DE_DIOS.md
- MASTER_PLAN_OJO_DE_DIOS.md
- ROADMAP_RONDAS_OJO_DE_DIOS.md
- docs/
- docs/tools/
- registry generado
- VersionLock
- ToolHealth
- EvidenceStore
- ScoringEngine
- Attack Surface Graph
- Hermes proposals
- Hermes promoted
- plugins manifest
- CVE intelligence cache
- Kali tool catalog
- Nuclei templates catalog si se decide en ronda futura
- OSV/SBOM data si se decide en ronda futura

## Context packs mínimos

Cada context pack debe incluir solo la información necesaria. No pasar todo el repo a LaIA en cada petición.

### target_planning_pack

Incluye target, normalized target, scope/allowlist, modo, módulos permitidos, registry filtrado, permisos, VersionLock relevante, ToolHealth relevante y documentos de policy mínimos.

### technique_execution_pack

Incluye technique contract, input schema, modo permitido, worker previsto, evidence contract, versión bloqueada, ToolHealth, permisos y límites. No incluye herramientas no relacionadas.

### evidence_analysis_pack

Incluye evidence real, parser usado, scoring previo, target, técnica, timestamp, confidence, fuentes y falsos positivos conocidos.

### hermes_proposal_pack

Incluye problema detectado, piezas faltantes, constraints de arquitectura, archivos permitidos, estado IMPLEMENTACION_USUARIO_REQUERIDA, evidence demo esperada, tests estructurales y Promotion Pipeline.

### cve_intelligence_pack

Incluye CVE normalizada, CPE/product/version, KEV/EPSS/OSV, Attack Surface Graph relevante, técnicas candidatas, evidence existente y estados de confirmación.

### tool_usage_pack

Incluye ficha docs/tools, VersionLock, ToolHealth, permisos, formatos de entrada/salida, parser, known_errors y notes_for_laia/x5/hermes.

### module_assistant_pack

Incluye definición del módulo oficial, capacidades, técnicas registradas, herramientas asociadas, panel fields, permisos y límites.

### report_writer_pack

Incluye findings confirmados por evidence, confidence, timeline, scope, falsos positivos, recomendaciones y referencias. No incluye findings candidatos como confirmados.

### failure_recovery_pack

Incluye error real, ToolHealth, logs permitidos, missing inputs, missing docs, missing tool, fallback X5, propuesta Hermes si procede y límites de no ejecución libre.

## Flujo operativo completo

Usuario crea objetivo
→ TargetFingerprint
→ Attack Surface Graph si aplica
→ LaIA interpreta con context pack
→ LaIA devuelve JSON
→ X5 valida JSON/registry/permisos/scope/modo
→ Worker o demo/dry_run
→ EvidenceStore
→ ScoringEngine
→ LaIA analiza resultado
→ X5 decide siguiente paso
→ Hermes propone evolución si falta pieza
→ Mistral revisa proposal
→ usuario aprueba/rechaza
→ promoción controlada
→ VersionLock
→ Knowledge Base refresh

## Regla de verdad

La verdad operativa está en:

- código real;
- registry real;
- evidence real;
- ToolHealth real;
- VersionLock real;
- scoring real;
- aprobaciones reales.

LaIA y Hermes nunca deben tratar documentación aspiracional como funcionalidad real.

## Estados permitidos cuando falta algo

- UNKNOWN
- MISSING_DOC
- MISSING_TOOL
- MISSING_INPUT
- MISSING_PLUGIN
- MISSING_EVIDENCE
- IMPLEMENTACION_USUARIO_REQUERIDA
- HARDWARE_REQUIRED
- MANUAL_REQUIRED
- DISABLED_BY_POLICY

## Conexión con subsistemas futuros

- Registry define qué existe como técnica visible para X5.
- VersionLock define qué versión puede considerarse fijada.
- ToolHealth define disponibilidad real de herramientas.
- EvidenceStore define si algo ocurrió y con qué evidencia.
- ScoringEngine ajusta confianza solo con evidence real.
- Attack Surface Graph conecta targets, servicios, versiones, CVE, técnicas y evidence.
- Hermes proposals son insumos de evolución, no producción.
- Hermes promoted solo cuenta tras aprobación, promoción, VersionLock y recarga de registry.

## Resultado esperado

El repositorio debe poder explicar a cualquier agente futuro cómo Ojo de Dios aprende, decide, evoluciona y evita inventar funcionalidad.
