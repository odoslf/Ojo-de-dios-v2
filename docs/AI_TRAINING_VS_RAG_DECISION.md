# AI TRAINING VS RAG DECISION — OJO DE DIOS

## Decisión

Para Ojo de Dios v1:

Usar:

- RAG local;
- Knowledge Bootstrap;
- embeddings;
- context packs;
- JSON Schema;
- memoria estructurada;
- EvidenceStore;
- ScoringEngine;
- ToolHealth;
- VersionLock;
- Hermes proposals;
- evaluación.

No usar fine-tuning como requisito inicial.

## Por qué no fine-tuning inicial

No usar fine-tuning inicial porque:

- el proyecto cambia;
- las herramientas cambian;
- CVE cambian;
- registry cambia;
- proposals Hermes cambian;
- evidence cambia;
- scoring cambia;
- una base RAG se puede refrescar sin reentrenar;
- fine-tuning puede memorizar información obsoleta;
- fine-tuning no sustituye permisos, registry, X5 ni EvidenceStore.

## Cuándo considerar fine-tuning

Solo considerar fine-tuning si:

- RAG local funciona;
- Knowledge Bootstrap funciona;
- JSON Schema funciona;
- context packs funcionan;
- evaluación existe;
- dataset limpio existe;
- no hay secretos;
- no hay datos sensibles;
- existe rollback;
- hay mejora medible;
- no rompe seguridad;
- no sustituye X5.

## Qué podría entrenarse en el futuro

Solo patrones no sensibles:

- formato de respuesta;
- clasificación de intención;
- explicación de módulos;
- elección de context pack;
- resumen de evidence;
- redacción de informes;
- estilo operativo;
- detección de missing_information;
- clasificación de estado.

## No entrenar

No entrenar:

- secretos;
- credenciales;
- payloads privados;
- bypass;
- exploits;
- datos sensibles;
- evidence confidencial;
- datos fuera de scope.

## Regla de producto

Fine-tuning nunca convierte una técnica en funcional.
La funcionalidad viene de código real, registry, worker, permissions, evidence y X5.

## Relación con Knowledge Bootstrap

Knowledge Bootstrap es requisito v1. Fine-tuning es una optimización futura posible y condicionada. Si no hay Knowledge Bootstrap, no hay base confiable para evaluar fine-tuning.
