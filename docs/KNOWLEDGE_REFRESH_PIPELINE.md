# KNOWLEDGE REFRESH PIPELINE — OJO DE DIOS

## Objetivo

Mantener actualizada la Knowledge Base de LaIA.

## Cuándo refrescar

Refrescar Knowledge Base cuando:

- cambia documentación;
- cambia registry;
- cambia VersionLock;
- cambia ToolHealth;
- se añade plugin;
- Hermes promociona propuesta;
- se añade evidence importante;
- se actualiza herramienta;
- se añade técnica;
- se modifica panel schema;
- se modifica worker;
- se modifica evidence contract.

## Proceso

1. Detectar cambios por hash/timestamp.
2. Recolectar documentos.
3. Excluir secretos.
4. Dividir en chunks.
5. Generar embeddings.
6. Actualizar índice.
7. Registrar refresh log.
8. LaIA puede consultar versión nueva.

## Refresh log

Guardar:

`storage/knowledge_base/refresh_log.json`

Campos:

- refresh_id;
- timestamp;
- files_indexed;
- files_skipped;
- chunks_created;
- embeddings_created;
- errors;
- index_version.


## Extensión Ronda 0-G — Refresh obligatorio v1

Knowledge Refresh es requisito v1 junto con First Run Knowledge Load y AI status panel. Debe refrescar docs, registry, technique metadata, tool catalog, VersionLock, ToolHealth, EvidenceStore, ScoringEngine, Hermes proposals/promoted, plugins, CVE cache, JSON schemas y context pack definitions cuando cambien.

Refresh no debe ejecutar tools, lanzar scans, instalar dependencias, descargar modelos sin permiso, promocionar Hermes ni indexar secretos. Si falla, debe marcar STALE/FAILED/DEMO_ONLY y X5 debe degradar.
