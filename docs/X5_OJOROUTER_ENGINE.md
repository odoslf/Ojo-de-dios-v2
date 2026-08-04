# X5 / OJOROUTER ENGINE

## Principio

X5/OjoRouter manda la ejecución.

LaIA decide y razona.
X5 valida y ejecuta.
Workers ejecutan.
EvidenceStore demuestra.
ScoringEngine aprende.
Hermes evoluciona.

## Funciones

X5 debe:

- cargar registry;
- recibir plan de LaIA;
- validar técnica;
- validar permisos;
- validar modo;
- validar scope;
- validar herramienta;
- seleccionar worker;
- crear job;
- recibir evidence;
- actualizar scoring;
- decidir fallback;
- pedir nueva propuesta a Hermes si procede.

## Archivos previstos

- `app/core/ojo_router.py`
- `app/core/x5_strategy_engine.py`
- `app/core/scoring_engine.py`
- `app/core/policy_engine.py`
- `app/core/job_state.py`
- `app/workers/job_runner.py`

## Inspiración X5 existente

Tomar como referencia del X5 de Cantera IQ:

- contrato drop-in;
- diagnostics;
- runtime config;
- scoring;
- payload normalizado;
- validation;
- incidents;
- fallback;
- no funcionalidad falsa.

No copiar entero sin adaptar.
