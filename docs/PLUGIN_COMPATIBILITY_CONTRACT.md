# PLUGIN COMPATIBILITY CONTRACT — OJO DE DIOS

## Objetivo

Permitir que Ojo de Dios crezca por plugins instalables por pip sin tocar el core.

## Entry point oficial

Grupo principal:

`ojo_de_dios.techniques`

Grupos opcionales futuros:

- `ojo_de_dios.parsers`
- `ojo_de_dios.workers`
- `ojo_de_dios.panels`
- `ojo_de_dios.evidence_writers`
- `ojo_de_dios.hermes_skills`
- `ojo_de_dios.ai_assistants`

## pyproject.toml de ejemplo conceptual

```toml
[project.entry-points."ojo_de_dios.techniques"]
my_plugin = "ojo_plugin_example:register"
```

## Función register

Un plugin debe exponer una función `register()` que devuelva un manifiesto compatible.

El manifiesto debe incluir:

- plugin_id
- name
- version
- api_version
- provided_techniques
- provided_parsers
- provided_workers
- provided_panels
- provided_evidence_writers
- required_permissions
- requires_user_implementation
- dependencies
- status

## API version

Ojo de Dios debe declarar una API pública para plugins:

`OJO_PLUGIN_API_VERSION=1`

Si el plugin usa otra versión incompatible:

PLUGIN_CONTRACT_INVALID

## Estados de plugin

- PLUGIN_AVAILABLE
- PLUGIN_ENABLED
- PLUGIN_DISABLED
- PLUGIN_LOAD_FAILED
- PLUGIN_CONTRACT_INVALID
- PLUGIN_MISSING_DEPENDENCY
- PLUGIN_REQUIRES_REVIEW
- PLUGIN_PROMOTED
- PLUGIN_ROLLED_BACK

## Regla de carga

Si un plugin falla:

- no rompe arranque;
- se marca PLUGIN_LOAD_FAILED;
- se registra error;
- se muestra en Settings/Ops;
- se puede desactivar.

## VersionLock

Cada plugin debe registrar:

- package_name
- version
- source
- hash si aplica
- installed_at
- enabled
- status
