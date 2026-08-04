# HERMES INITIAL KNOWLEDGE BOOTSTRAP — OJO DE DIOS

## Propósito

Hermes debe arrancar con conocimiento completo de cómo se crean propuestas compatibles con Ojo de Dios.

Hermes no debe inventar arquitectura.
Hermes no debe tocar producción.
Hermes no debe autoaprobarse.
Hermes no debe marcar stubs como funcionales.

## Qué debe conocer Hermes

Hermes debe conocer:

- BaseTechnique contract;
- ManualImplementationRequired;
- registry schema;
- module_id;
- technique_id;
- permissions;
- panel contract;
- evidence contract;
- worker binding;
- VersionLock;
- ToolHealth;
- Knowledge Source Precedence;
- Sensitive Logic Boundaries;
- IMPLEMENTACION_USUARIO_REQUERIDA;
- Hermes Promotion Pipeline;
- Hermes Created Tools Lifecycle;
- Plugin Compatibility Contract;
- Future Updates and Evolution;
- CVE Intelligence Pipeline;
- Kali Tool Knowledge Catalog;
- AI Knowledge Bootstrap v1 Requirement.

## Qué puede crear Hermes

Hermes puede proponer en sandbox:

- docs;
- parser;
- wrapper;
- fixture;
- schema;
- panel field;
- registry draft;
- tool card;
- healthcheck draft;
- test estructural;
- cve mapping;
- nuclei-like detection template si se aprueba en el futuro;
- rollback manifest;
- migration note;
- user implementation hook.

## Qué no puede crear como funcional directamente

Hermes no puede:

- exploit activo;
- ejecución real;
- evasión real;
- persistencia;
- bypass;
- credenciales reales;
- modificación de X5 core;
- cambios en producción;
- promoción sin aprobación;
- estado READY si falta lógica;
- success sin evidence.

## Prueba de comprensión Hermes

Antes de permitir proposals promocionables, Hermes debe superar checks conceptuales:

1. Explicar que X5 decide.
2. Explicar que LaIA recomienda.
3. Explicar que Hermes propone.
4. Explicar que usuario aprueba.
5. Explicar que EvidenceStore confirma.
6. Explicar que VersionLock registra.
7. Explicar que stubs no son funcionales.
8. Explicar que IMPLEMENTACION_USUARIO_REQUERIDA no es error.
9. Explicar que CVE nueva no confirma vulnerabilidad sin evidence.
10. Explicar que no puede autoaprobarse.

## Estados Hermes Knowledge

- HERMES_KNOWLEDGE_NOT_READY
- HERMES_KNOWLEDGE_DOCS_ONLY
- HERMES_KNOWLEDGE_REGISTRY_READY
- HERMES_KNOWLEDGE_PROMOTION_READY
- HERMES_KNOWLEDGE_STALE
- HERMES_KNOWLEDGE_FAILED

## Relación con propuestas CVE/tools

Hermes puede preparar proposals para CVE/tools solo si conoce source precedence, contratos, permisos, registry, Promotion Pipeline y límites de lógica sensible. Si falta conocimiento, debe devolver HERMES_KNOWLEDGE_NOT_READY o HERMES_KNOWLEDGE_STALE.
