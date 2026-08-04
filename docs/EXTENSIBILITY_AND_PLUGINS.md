# EXTENSIBILITY AND PLUGINS — OJO DE DIOS

## Objetivo

Ojo de Dios debe crecer fácil.

Debe poder pasar de 240 técnicas a 241, 300 o más sin romper tests ni tocar 20 archivos.

## Formas de añadir técnicas

Hay dos formas:

1. Técnica interna del repo.
2. Plugin instalable por pip.

## Técnica interna

Ruta:

`app/modules/<module_name>/<technique_name>.py`

Cada técnica define una clase BaseTechnique.

Debe declarar:

- technique_id;
- module_id;
- display_name;
- description;
- tool_name;
- recommended_version;
- runtime;
- worker;
- permission_level;
- risk_level;
- noise_level;
- required_inputs;
- optional_inputs;
- ai_fillable_inputs;
- panel_fields;
- expected_evidence;
- configurable_parameters;
- implementation_status;
- requires_user_implementation;
- requires_confirmation;
- requires_hardware;
- can_run_in_demo;
- can_run_in_dry_run;
- hermes_enabled;
- mistral_assistant;
- evidence_schema;
- version_lock_id.

## Plugin por pip

Ojo de Dios debe preparar un sistema de plugins instalables por pip.

Nombre recomendado de paquetes:

`ojo-plugin-<nombre>`

Ejemplo:

- `ojo-plugin-custom-osint`
- `ojo-plugin-custom-cloud`
- `ojo-plugin-custom-parser`

Entry point recomendado en `pyproject.toml` del plugin:

```toml
[project.entry-points."ojo_de_dios.techniques"]
custom_technique = "ojo_plugin_custom.techniques:register"
```

El core debe poder descubrir plugins con:

```python
importlib.metadata.entry_points()
```

Grupo oficial:

`ojo_de_dios.techniques`

Opcional futuro:

- `ojo_de_dios.parsers`
- `ojo_de_dios.workers`
- `ojo_de_dios.panels`
- `ojo_de_dios.evidence_writers`
- `ojo_de_dios.hermes_skills`

## Contrato de plugin

Un plugin puede aportar:

- técnicas;
- parsers;
- wrappers;
- schemas;
- panel fields;
- workers;
- fixtures;
- docs;
- evidence writers;
- Hermes proposals.

Pero no debe poder:

- modificar core sin aprobación;
- autoactivarse como funcional si requiere lógica privada;
- saltarse registry;
- saltarse permission levels;
- saltarse kill switch;
- saltarse evidence;
- saltarse scope.

## Loader de plugins

Archivos previstos:

- `app/core/plugin_manager.py`
- `app/core/plugin_contract.py`
- `app/core/plugin_registry.py`

`plugin_manager.py` debe:

- descubrir entry points;
- cargar plugins;
- validar contrato;
- registrar técnicas;
- marcar errores como PLUGIN_LOAD_FAILED;
- no romper arranque si un plugin falla;
- registrar evidence/log de carga;
- permitir desactivar plugin desde settings.

## Estados de plugin

- PLUGIN_AVAILABLE
- PLUGIN_ENABLED
- PLUGIN_DISABLED
- PLUGIN_LOAD_FAILED
- PLUGIN_CONTRACT_INVALID
- PLUGIN_MISSING_DEPENDENCY
- PLUGIN_REQUIRES_REVIEW

## VersionLock para plugins

Cada plugin debe quedar registrado en VersionLock:

- package_name;
- version;
- source;
- hash si aplica;
- installed_at;
- enabled;
- status.

## Hermes Agent y plugins

Hermes puede proponer un plugin en sandbox.

Flujo:

sandbox plugin
→ tests estructurales
→ Mistral review
→ diff
→ approval
→ pip install local / editable si el usuario aprueba
→ registry reload
→ evidence

Nunca auto-instalar plugins en producción sin aprobación.
