# HERMES PROMOTION PIPELINE — OJO DE DIOS

## Principio

Hermes puede crear cosas nuevas, pero no puede ponerlas en producción directamente.

Hermes trabaja así:

sandbox → manifest → evidence → tests estructurales → revisión Mistral → diff → aprobación usuario → promoción controlada → VersionLock → registry reload

## Estados

- draft
- designed
- generated
- tested
- review_required
- approved_by_user
- promoted
- rejected
- archived
- rolled_back

## Qué puede crear Hermes

Hermes puede crear en sandbox:

- técnica nueva;
- variante de técnica;
- wrapper;
- parser;
- worker stub;
- panel field;
- schema;
- evidence writer;
- fixture;
- plugin pip;
- skill;
- documentación;
- regla scoring;
- conector;
- herramienta interna de laboratorio.

## Qué NO puede hacer Hermes directamente

Hermes no puede:

- autoaprobarse;
- tocar producción sin aprobación;
- instalar plugin sin aprobación;
- activar técnica sensible sin pasar por X5;
- saltarse permisos;
- saltarse EvidenceStore;
- saltarse Kill Switch;
- marcar stub como funcional;
- ocultar diff;
- borrar rastros.

## Manifest obligatorio de una propuesta Hermes

Cada propuesta debe tener:

- proposal_id
- title
- module_id
- technique_id opcional
- proposal_type
- risk_level
- created_at
- created_by
- files_created
- files_modified
- entry_points si aplica
- permissions_requested
- requires_user_implementation
- expected_evidence
- tests_created
- demo_fixture
- mistral_review
- approval_status
- rollback_plan

## Evidence obligatoria

Cada propuesta Hermes debe guardar:

```text
storage/hermes_lab/evidence/<proposal_id>/
├─ manifest.json
├─ summary.md
├─ diff.patch
├─ files_created.txt
├─ files_modified.txt
├─ tests.txt
├─ mistral_review.md
├─ approval.json
└─ rollback.md
```

## Promoción

Una propuesta solo puede promocionarse si:

- tiene manifest;
- tiene diff;
- tiene evidence;
- tiene revisión Mistral;
- tiene aprobación usuario;
- no rompe registry;
- no rompe imports;
- no marca stub como funcional;
- declara permisos;
- declara rollback.

## Puesta en práctica

Cuando una propuesta está promoted:

1. Registry recarga.
2. VersionLock registra.
3. Panel la muestra.
4. LaIA puede verla.
5. X5 puede planificarla.
6. PolicyEngine valida permisos.
7. JobRunner la ejecuta solo si el modo lo permite.
8. EvidenceStore registra resultado.


## Extensión Ronda 0-F — Promotion Pipeline para CVE/tools

Las propuestas Hermes basadas en CVE o herramientas externas deben incluir fuentes, fechas, hashes cuando aplique, risk, limitations, generated_files, modified_files, evidence demo, tests estructurales, estado Mistral y aprobación de usuario.

Una propuesta CVE/tool solo puede considerarse disponible si pasa por approval, promoción, VersionLock, registry reload y Knowledge Base refresh. Antes de eso no es producción ni técnica funcional.
