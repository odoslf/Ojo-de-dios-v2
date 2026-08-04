# HERMES CREATED TOOLS LIFECYCLE — OJO DE DIOS

## Objetivo

Definir cómo una herramienta creada por Hermes pasa de idea a herramienta usable.

## Fases

1. Idea
2. Proposal
3. Sandbox generation
4. Manifest
5. Local evidence
6. Mistral review
7. Structural validation
8. User approval
9. Promotion
10. VersionLock
11. Registry reload
12. Controlled execution by X5
13. Scoring
14. Maintenance
15. Deprecation or upgrade

## Requisitos de una herramienta Hermes

Debe tener:

- carpeta propia;
- manifest.json;
- README.md;
- inputs;
- outputs;
- permissions;
- evidence contract;
- demo fixture;
- rollback;
- status;
- requires_user_implementation si aplica.

## Carpeta recomendada

```text
storage/hermes_lab/sandbox/<proposal_id>/
├─ manifest.json
├─ README.md
├─ src/
├─ fixtures/
├─ evidence/
├─ tests_structural/
├─ diff.patch
└─ rollback.md
```

## Promoción a plugin

Si la herramienta debe vivir fuera del core:

- empaquetar como plugin pip;
- declarar entry point;
- instalar solo tras aprobación;
- registrar en VersionLock;
- permitir desactivar.

## Promoción a core

Si la herramienta debe entrar en core:

- copiar archivos aprobados;
- actualizar registry;
- actualizar docs;
- registrar diff;
- registrar rollback;
- validar imports;
- validar panel;
- validar evidence.

## Mantenimiento

Hermes debe poder proponer mejoras posteriores si:

- falla muchas veces;
- cambia salida de herramienta externa;
- cambia API externa;
- parser queda obsoleto;
- LaIA detecta baja eficacia;
- X5 baja score.
