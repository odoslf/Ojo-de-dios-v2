# AI KNOWLEDGE BOOTSTRAP V1 REQUIREMENT — OJO DE DIOS

## Decisión definitiva

Ojo de Dios v1 debe incluir Knowledge Bootstrap para LaIA/Mistral y Hermes Agent.

No es una mejora futura.
No es v2.
No es opcional.
No sustituye a X5/OjoRouter.
No convierte documentación aspiracional en funcionalidad real.

LaIA/Mistral y Hermes Agent deben arrancar con conocimiento local indexado del proyecto antes de operar de forma fiable.

## Por qué es obligatorio

Ojo de Dios tiene demasiados módulos, técnicas, contratos, permisos, herramientas, states, docs, evidence, VersionLock, ToolHealth y flujos Hermes como para depender de prompts gigantes o memoria de chat.

LaIA/Mistral debe saber consultar el proyecto.
Hermes debe saber crear propuestas compatibles.
X5 debe poder validar lo que LaIA/Hermes Agent proponen.

Sin Knowledge Bootstrap, un modelo puede explicar texto suelto, pero no puede operar de forma fiable dentro de la arquitectura de Ojo de Dios.

## Qué se considera Knowledge Bootstrap

Knowledge Bootstrap es el proceso que prepara la base local de conocimiento antes del uso real:

- leer documentación raíz;
- leer docs/;
- leer registry generado;
- leer técnicas registradas;
- leer permisos;
- leer contracts;
- leer module inventory;
- leer docs/tools;
- leer VersionLock;
- leer ToolHealth;
- leer EvidenceStore;
- leer ScoringEngine;
- leer Hermes proposals;
- leer Hermes promoted;
- leer plugin manifests;
- leer CVE Intelligence cache cuando exista;
- crear chunks;
- crear embeddings cuando el backend esté disponible;
- crear índices por módulo/técnica/tool/CVE/target/proposal;
- crear source manifest;
- crear source precedence map;
- crear resúmenes canónicos;
- validar context packs;
- validar JSON schemas;
- validar que LaIA/Hermes Agent conocen sus límites.

## Qué NO es Knowledge Bootstrap

No es:

- fine-tuning;
- reentrenamiento de pesos;
- ejecución de herramientas;
- descarga obligatoria de CVE;
- ejecución ofensiva;
- bypass;
- generación de exploits;
- sustitución de X5;
- aprobación automática de Hermes;
- demostración de que las técnicas están funcionales.

## Requisito de acabado v1

Ojo de Dios v1 no se considera acabado si falta:

- Knowledge Bootstrap documentado;
- Knowledge Refresh documentado;
- context packs documentados;
- AI status panel documentado;
- validación JSON documentada;
- separación RAG vs fine-tuning documentada;
- Hermes initial knowledge documentado;
- reglas de bloqueo si Knowledge Base falta o está desactualizada.

## Estados del Knowledge Bootstrap

Estados oficiales:

- NOT_CREATED
- CREATED_EMPTY
- INDEXING
- READY_DOCS_ONLY
- READY_WITH_REGISTRY
- READY_WITH_TOOLS
- READY_WITH_EVIDENCE
- READY_WITH_HERMES
- READY_WITH_CVE_CACHE
- STALE
- FAILED
- DISABLED
- DEMO_ONLY

## Regla de operación

Si Knowledge Bootstrap no está READY_WITH_REGISTRY como mínimo:

- LaIA puede explicar documentación;
- LaIA puede ayudar en modo demo;
- X5 no debe aceptar planes operativos IA como fiables;
- Hermes no debe generar propuestas promocionables;
- el panel debe mostrar aviso visible.

## Requisito mínimo para uso real

Para uso real controlado:

- registry indexado;
- permisos indexados;
- docs principales indexados;
- context packs funcionando;
- JSON schemas validados;
- source precedence activo;
- ToolHealth disponible aunque haya herramientas opcionales ausentes;
- VersionLock disponible;
- EvidenceStore disponible;
- X5 validando todo.

## Relación con documentación aspiracional

Knowledge Bootstrap debe indexar documentación aspiracional como aspiracional. El estado funcional solo puede venir de código real, registry real, workers reales, permisos, VersionLock, ToolHealth, EvidenceStore y validación X5.
