# Contrato universal de evidencias — Ojo de Dios

Este documento define la base documental del Vector 3 de M16 para evidencias,
identificadores universales, tipos, estados y calidad. No crea implementación,
endpoints, workers, base de datos ni almacenamiento nuevo.

## Contrato JSON evidence_record

```json
{
  "type": "evidence_record",
  "evidence_id": "ev-uuid",
  "run_id": "run-uuid",
  "trace_id": "trace-uuid",
  "span_id": "span-uuid",
  "target_id": "target-uuid",
  "target_fingerprint_id": "fp-uuid",
  "module_id": "android",
  "technique_id": "android.analysis.secrets",
  "worker_id": "android_worker",
  "evidence_type": "json_result",
  "title": "Resultado normalizado",
  "description": "Evidencia asociada a una ejecución",
  "storage_path": "storage/evidence/android/run-uuid/artifacts/result.json",
  "mime_type": "application/json",
  "size_bytes": 2048,
  "sha256": "sha256...",
  "quality": "high",
  "confidence": 0.95,
  "redaction_policy": "masked_by_default",
  "sensitivity": "sensitive",
  "source_tool": "tool_name",
  "source_tool_version": "versionlock-reference",
  "versionlock_id": "vl-uuid",
  "created_at": "2026-06-01T12:00:00Z",
  "operator_id": "admin",
  "scope": "laboratory",
  "status": "stored",
  "tags": [],
  "metadata": {},
  "audit_event_ids": []
}
```

## Tipos oficiales de evidencia

- `text_log`
- `json_result`
- `csv_result`
- `pcap`
- `image`
- `audio`
- `video`
- `binary_artifact`
- `archive`
- `database_extract`
- `memory_dump`
- `configuration_snapshot`
- `before_after_snapshot`
- `tool_report`
- `manual_terminal_session`
- `ai_summary`
- `final_report`
- `unknown_evidence`

## Estados oficiales de evidencia

- `pending`
- `collecting`
- `stored`
- `verified`
- `redacted`
- `exported`
- `corrupted`
- `missing`
- `rejected`
- `archived`

## Calidad de evidencia

- `none`: no existe evidencia útil.
- `low`: evidencia indirecta o incompleta.
- `medium`: evidencia válida pero limitada.
- `high`: evidencia clara, verificable y relacionada con el resultado.
- `critical`: evidencia directa de impacto relevante, preservada y reproducible.

Reglas:

- éxito sin evidencia útil no puntúa;
- evidencia corrupta no puntúa;
- demo o simulación no puntúa como ejecución real;
- evidencia duplicada no aumenta score;
- LaIA puede explicar calidad, pero no cambiarla sin contrato y AuditLog;
- X5 exige "evidence_ids" válidos antes de actualizar scoring;
- toda fecha usa ISO 8601 UTC;
- todo hash de archivo usa SHA-256;
- ninguna evidencia se sobrescribe silenciosamente.

## Contrato JSON evidence_event

```json
{
  "type": "evidence_event",
  "event_id": "evt-uuid",
  "evidence_id": "ev-uuid",
  "run_id": "run-uuid",
  "trace_id": "trace-uuid",
  "span_id": "span-uuid",
  "event_type": "created",
  "actor_type": "worker",
  "actor_id": "android_worker",
  "timestamp": "2026-06-01T12:00:00Z",
  "previous_event_hash": null,
  "event_hash": "sha256...",
  "details": {}
}
```

Lista exacta de `event_type`:

"created", "written", "hashed", "verified", "viewed", "revealed_full", "redacted", "exported", "handed_off", "linked_to_finding", "linked_to_report", "archived", "integrity_failed".

Reglas:

- cada evento debe conservar "trace_id";
- "event_hash" usa SHA-256;
- "previous_event_hash" enlaza el evento anterior de la misma evidencia;
- el primer evento usa "previous_event_hash: null";
- ningún evento se elimina ni se sobrescribe;
- una rotura de cadena marca la evidencia como "corrupted".

## Cadena de custodia interna

- registrar quién creó la evidencia;
- registrar técnica, herramienta y versión de origen;
- registrar fecha y hora de creación;
- registrar cada visualización;
- registrar cada revelado de contenido completo;
- registrar cada redacción;
- registrar cada exportación;
- registrar cada handoff;
- registrar hash antes y después de cualquier transformación;
- una modificación crea nueva versión o nuevo "evidence_id";
- AuditLog referencia siempre "evidence_id", "event_id", "run_id" y "trace_id".

## Contrato JSON evidence_handoff

```json
{
  "type": "evidence_handoff",
  "handoff_id": "handoff-uuid",
  "trace_id": "trace-uuid",
  "source_module": "android",
  "target_module": "ops_quality",
  "run_id": "run-uuid",
  "evidence_ids": ["ev-001", "ev-002"],
  "finding_ids": ["finding-001"],
  "handoff_reason": "session_closed",
  "redaction_policy": "masked_by_default",
  "requires_confirmation": false,
  "operator_id": "admin",
  "created_at": "2026-06-01T12:00:00Z"
}
```

Reglas:

- M16 acepta handoff desde todos los módulos;
- el módulo receptor no modifica la evidencia original;
- todo handoff conserva "trace_id", "run_id" y "evidence_ids";
- datos sensibles usan redacción por defecto;
- un handoff incompleto se rechaza y registra en AuditLog.

## Contrato JSON before_after_comparison

```json
{
  "type": "before_after_comparison",
  "comparison_id": "cmp-uuid",
  "run_id": "run-uuid",
  "trace_id": "trace-uuid",
  "before_evidence_ids": ["ev-before"],
  "after_evidence_ids": ["ev-after"],
  "differences": [],
  "impact_proven": true,
  "quality": "high",
  "created_at": "2026-06-01T12:00:00Z"
}
```

Reglas:

- "before_evidence_ids" y "after_evidence_ids" son obligatorios;
- "impact_proven" solo puede ser "true" con evidencia válida;
- LaIA puede explicar diferencias, pero no inventarlas;
- ScoringEngine consulta la calidad de la comparación;
- rollback, si existe, debe relacionarse con la comparación.

## Estructura futura de almacenamiento

```text
storage/evidence/<module_id>/<run_id>/
  evidence_manifest.json
  timeline.json
  artifacts/
  reports/
  exports/
```

Reglas:

- "evidence_manifest.json" es obligatorio por cada "run_id";
- "timeline.json" contiene todos los "evidence_event" de la ejecución;
- "artifacts/" contiene evidencias originales;
- "reports/" contiene informes derivados;
- "exports/" contiene paquetes exportados;
- ningún archivo original se sobrescribe;
- cada archivo almacenado debe tener SHA-256;
- toda ruta se guarda relativa a la raíz del proyecto;
- los nombres de archivo no contienen secretos ni datos sensibles.

## Contrato JSON evidence_manifest

```json
{
  "type": "evidence_manifest",
  "manifest_id": "manifest-uuid",
  "run_id": "run-uuid",
  "trace_id": "trace-uuid",
  "module_id": "android",
  "target_id": "target-uuid",
  "technique_id": "android.analysis.secrets",
  "evidence_ids": ["ev-001", "ev-002"],
  "finding_ids": ["finding-001"],
  "report_ids": [],
  "versionlock_ids": ["vl-001"],
  "created_at": "2026-06-01T12:00:00Z",
  "updated_at": "2026-06-01T12:00:00Z",
  "operator_id": "admin",
  "manifest_sha256": "sha256...",
  "status": "verified"
}
```

Reglas:

- el manifest lista todas las evidencias del "run_id";
- "manifest_sha256" se recalcula al crear una nueva versión;
- una actualización conserva la versión anterior;
- "status" solo puede ser "pending", "verified", "corrupted" o "archived";
- un manifest corrupto bloquea exportación y scoring.

## Relaciones de evidencia

Relaciones exactas:

- "EVIDENCE_SUPPORTS_FINDING"
- "EVIDENCE_DERIVED_FROM_EVIDENCE"
- "EVIDENCE_CREATED_BY_RUN"
- "EVIDENCE_INCLUDED_IN_REPORT"
- "EVIDENCE_EXPORTED_AS_PACKAGE"
- "EVIDENCE_HANDED_OFF_TO_MODULE"
- "EVIDENCE_VERIFIED_BY_OPERATOR"

Regla:

Una evidencia derivada nunca sustituye ni modifica la evidencia original.

## Sensibilidad y redacción

Políticas de sensibilidad:

- "public"
- "internal"
- "sensitive"
- "restricted"

Políticas de redacción:

- "none"
- "masked_by_default"
- "metadata_only"
- "full_access_requires_confirmation"

Reglas:

- "restricted" nunca se muestra completo por defecto;
- revelar contenido completo genera "evidence_event: revealed_full";
- una redacción genera nueva evidencia derivada;
- informes y exports usan redacción por defecto;
- LaIA solo recibe contenido permitido por "redaction_policy".

## Contrato JSON evidence_export

```json
{
  "type": "evidence_export",
  "export_id": "export-uuid",
  "run_id": "run-uuid",
  "trace_id": "trace-uuid",
  "evidence_ids": ["ev-001", "ev-002"],
  "format": "zip",
  "redaction_policy": "masked_by_default",
  "package_path": "storage/evidence/android/run-uuid/exports/export-uuid.zip",
  "package_sha256": "sha256...",
  "operator_id": "admin",
  "reason": "internal_report",
  "created_at": "2026-06-01T12:00:00Z",
  "status": "verified"
}
```

Reglas:

- toda exportación requiere manifest válido;
- exportación completa de datos "restricted" requiere confirmación;
- el paquete exportado debe tener SHA-256;
- exportar genera "evidence_event: exported";
- el export conserva "run_id", "trace_id" y "evidence_ids";
- una exportación fallida no se marca como verificada.

## Persistencia futura

Estas tablas futuras se documentan como contrato de persistencia previsto; no se
crean en esta ronda, no añaden migraciones y no afirman capacidad operativa:

- "evidence_records"
- "evidence_events"
- "evidence_relationships"
- "evidence_handoffs"
- "evidence_exports"
- "evidence_manifests"
- "before_after_comparisons"
- "evidence_quality_scores"

Reglas:

- "evidence_id" es clave primaria de "evidence_records";
- todas las tablas relacionadas conservan "run_id" y "trace_id";
- las relaciones usan claves foráneas;
- SQLite debe activar validación de claves foráneas en cada conexión futura;
- ningún registro de evidencia se elimina físicamente sin política de archivado;
- una evidencia corrupta bloquea scoring, handoff y exportación;
- PostgreSQL futuro debe conservar los mismos contratos.
