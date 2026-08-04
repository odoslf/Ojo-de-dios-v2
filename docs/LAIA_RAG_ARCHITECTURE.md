# LAIA RAG ARCHITECTURE — OJO DE DIOS

## Decisión

LaIA usará RAG local antes que fine-tuning.

RAG permite consultar documentación actualizada del proyecto, herramientas, registry, evidence y plugins sin reentrenar el modelo cada vez que cambie algo.

## Componentes

### 1. Document collector

Recoge contenido de:

- docs/
- README.md
- AI_HANDOFF_OJO_DE_DIOS.md
- MASTER_PLAN_OJO_DE_DIOS.md
- registry generado;
- VersionLock;
- ToolHealth;
- Evidence summaries;
- Hermes proposals;
- plugin manifests.

### 2. Chunker

Divide documentos en bloques pequeños.

Cada bloque debe guardar metadata:

- source_path;
- doc_type;
- module_id si aplica;
- technique_id si aplica;
- tool_id si aplica;
- plugin_id si aplica;
- hermes_proposal_id si aplica;
- created_at;
- updated_at;
- hash.

### 3. Embeddings

Genera vectores para búsqueda semántica.

Backend local preferente:

- Ollama embeddings.

Opcional futuro:

- Mistral embeddings;
- sentence-transformers;
- otro backend local.

### 4. Vector store

Primera versión:

- SQLite + tabla de embeddings si es suficiente;
- o Chroma/FAISS si se decide en ronda específica.

No meter dependencia pesada hasta ronda concreta.

### 5. Retriever

Recupera contexto relevante según:

- pregunta;
- target;
- module_id;
- technique_id;
- tool_id;
- error;
- evidence;
- Hermes proposal.

### 6. Context builder

Construye el contexto para LaIA:

- instrucciones base;
- datos del target;
- registry relevante;
- evidence relevante;
- docs relevantes;
- tool health;
- scoring;
- límites de ejecución.

### 7. JSON validator

Toda respuesta operativa de LaIA pasa por JSON Schema.

Si no valida:

X5 no ejecuta.

## Seguridad del conocimiento

No indexar:

- .env real;
- API keys;
- tokens;
- credenciales;
- private keys;
- certificados privados;
- evidence sensible sin anonimizar;
- dumps reales;
- logs con secretos;
- binarios;
- archivos IQ sensibles.


## Extensión Ronda 0-F — RAG por context packs

El RAG debe construir context packs mínimos y no enviar todo el repo a LaIA en cada petición. Los packs oficiales mínimos son:

- target_planning_pack;
- technique_execution_pack;
- evidence_analysis_pack;
- hermes_proposal_pack;
- cve_intelligence_pack;
- tool_usage_pack;
- module_assistant_pack;
- report_writer_pack;
- failure_recovery_pack.

Cada pack debe respetar [KNOWLEDGE_SOURCE_PRECEDENCE.md](KNOWLEDGE_SOURCE_PRECEDENCE.md), incluir `source_paths`, diferenciar documentación de runtime y devolver UNKNOWN/MISSING_DOC cuando falte base suficiente.


## Extensión Ronda 0-G — RAG como requisito inicial antes que fine-tuning

RAG local, Knowledge Bootstrap, context packs, JSON Schema y memoria estructurada son requisito v1. Fine-tuning no es requisito inicial.

La arquitectura RAG debe:

- usar source manifest;
- respetar source precedence;
- no indexar secretos;
- producir context packs mínimos;
- indicar source_paths y confidence;
- degradar si embeddings no están disponibles;
- impedir claims de RAG semántico completo si solo hay búsqueda textual;
- alimentar el panel de estado IA/Hermes Agent.
