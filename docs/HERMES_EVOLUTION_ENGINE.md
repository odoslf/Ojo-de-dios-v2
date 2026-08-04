# HERMES LAB / EVOLUTION ENGINE

## Principio

Hermes es el laboratorio evolutivo de Ojo de Dios.

Hermes no ejecuta producción.
Hermes no sustituye a X5.
Hermes no sustituye a Mistral.
Hermes no es módulo 17.

## Funciones

Hermes puede crear en sandbox:

- skills;
- wrappers;
- parsers;
- schemas;
- paneles de laboratorio;
- workers de laboratorio;
- fixtures;
- tests estructurales;
- evidence writers;
- documentación;
- propuestas de nuevas técnicas;
- variantes de técnicas existentes.

## Flujo obligatorio

1. X5 o LaIA detecta necesidad.
2. Hermes crea proposal.
3. Hermes genera en sandbox.
4. Se crean tests estructurales.
5. Mistral revisa.
6. Panel muestra diff.
7. Usuario aprueba o rechaza.
8. Solo si aprueba, se promociona.
9. X5 puede usarlo.

## Estados Hermes

- draft
- designed
- generated
- tested
- review_required
- approved_by_user
- promoted
- rejected
- archived

## Permisos Hermes

Permitidos por defecto:

- read_project
- write_lab
- write_tests
- run_tests
- create_docs
- create_skill
- create_wrapper
- create_worker_stub
- request_x5_dry_run
- request_mistral_review
- request_promotion

Bloqueados por defecto:

- write_production
- modify_x5_core
- execute_live_target
- network_active_scan
- credential_testing
- rf_transmit
- android_device_action
- phishing_delivery
- cloud_mutation
- persistence_action

## Regla de seguridad estructural

Hermes debe tratar skills/plugins como componentes de software:

- permisos mínimos;
- sandbox;
- revisión;
- evidence;
- diff;
- aprobación;
- rollback.


## Extensión Ronda 0-G — Hermes Knowledge Bootstrap

Hermes Agent Evolution Engine no puede generar proposals promocionables si Hermes Agent knowledge no está preparado. Debe conocer contracts, registry schema, source precedence, Promotion Pipeline, VersionLock, ToolHealth, Sensitive Logic Boundaries, IMPLEMENTACION_USUARIO_REQUERIDA, CVE Intelligence Pipeline y Kali Tool Knowledge Catalog.

Estados recomendados: HERMES_KNOWLEDGE_NOT_READY, HERMES_KNOWLEDGE_DOCS_ONLY, HERMES_KNOWLEDGE_REGISTRY_READY, HERMES_KNOWLEDGE_PROMOTION_READY, HERMES_KNOWLEDGE_STALE, HERMES_KNOWLEDGE_FAILED.
