# LAIA CONTEXT PACKS — OJO DE DIOS

## Objetivo

LaIA no debe recibir todo el repositorio en cada petición.

Debe recibir context packs según tarea.

## Tipos de context pack

### target_planning_pack

Incluye:

- target;
- scope;
- Attack Surface Graph;
- relevant services;
- relevant techniques;
- tool health;
- scoring;
- permissions.

### technique_execution_pack

Incluye:

- technique metadata;
- inputs;
- panel_fields;
- worker;
- evidence contract;
- dry_run/demo behavior;
- permission_level;
- previous evidence.

### evidence_analysis_pack

Incluye:

- evidence summary;
- normalized output;
- expected evidence;
- scoring;
- previous attempts;
- failure reason.

### hermes_proposal_pack

Incluye:

- failure context;
- missing parser/wrapper/schema;
- relevant docs;
- related techniques;
- constraints;
- required manifest.

### report_writer_pack

Incluye:

- target summary;
- jobs;
- evidence;
- findings;
- scoring;
- limitations;
- manual_required items.

## Regla

Cada context pack debe tener:

- pack_type;
- target_id si aplica;
- module_id si aplica;
- technique_id si aplica;
- evidence_ids;
- source_paths;
- generated_at;
- max_tokens;
- checksum.


## Extensión Ronda 0-G — Validación de context packs en Bootstrap

Knowledge Bootstrap debe validar que los context packs mínimos están definidos, disponibles y limitados al caso de uso. LaIA/Hermes Agent no deben recibir todo el repo en cada prompt.

Cada context pack debe declarar:

- objetivo;
- fuentes permitidas;
- fuentes excluidas;
- JSON schema esperado;
- source_paths;
- confidence;
- estado READY/PARTIAL/STALE/FAILED;
- límites de no ejecución libre.

Si un context pack crítico está STALE o FAILED, X5 debe degradar a demo/dry_run o pedir confirmación según política.
