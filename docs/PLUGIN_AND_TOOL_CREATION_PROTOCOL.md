# PLUGIN AND TOOL CREATION PROTOCOL — OJO DE DIOS

## Objetivo

Ojo de Dios debe poder añadir técnicas, herramientas y plugins sin romper arquitectura y sin tocar manualmente 20 archivos.

El crecimiento debe mantener contratos, registry, VersionLock, permisos, evidence y visibilidad de IMPLEMENTACION_USUARIO_REQUERIDA.

## Añadir una técnica interna

Una técnica interna debe definir:

- módulo asignado;
- archivo propio;
- clase propia;
- technique_id estable;
- input_schema;
- panel_fields;
- ai_fillable_inputs;
- worker_binding;
- permission_level;
- risk_level;
- evidence_contract;
- demo_behavior;
- dry_run_behavior;
- implementation_status;
- user_logic_hook si falta lógica privada.

## Añadir una herramienta oficial

Una herramienta nueva se acepta si:

- tiene motivo técnico documentado;
- no sustituye silenciosamente una herramienta oficial existente;
- tiene módulo y técnica asociados;
- tiene runtime definido;
- tiene VersionLock;
- tiene healthcheck o tool_health si aplica;
- tiene parser o contrato de salida;
- tiene evidence_contract;
- respeta permisos, modo y kill switch.

## Añadir plugin pip

Nombre recomendado:

`ojo-plugin-<nombre>`

Entry point oficial:

```toml
[project.entry-points."ojo_de_dios.techniques"]
custom_technique = "ojo_plugin_custom.techniques:register"
```

Grupo oficial:

`ojo_de_dios.techniques`

Grupos opcionales futuros:

- `ojo_de_dios.parsers`
- `ojo_de_dios.workers`
- `ojo_de_dios.panels`
- `ojo_de_dios.evidence_writers`
- `ojo_de_dios.hermes_skills`

## Revisión de plugin

Todo plugin debe pasar por:

1. discovery;
2. contract validation;
3. dependency check;
4. permissions review;
5. VersionLock;
6. registry registration;
7. evidence/log de carga;
8. estado visible en panel;
9. opción de desactivar.

Si falla, no rompe arranque: queda como PLUGIN_LOAD_FAILED, PLUGIN_CONTRACT_INVALID, PLUGIN_MISSING_DEPENDENCY o PLUGIN_REQUIRES_REVIEW.

## Hermes Agent y creación

Hermes puede preparar plugins y herramientas en sandbox.

No puede instalar, activar o promocionar producción sin aprobación explícita.

## No confundir wrapper con funcionalidad

Un wrapper solo es funcional si ejecuta una herramienta real, captura salida, la normaliza, cumple evidence_contract y respeta X5/PolicyEngine/Kill Switch.

Si falta herramienta, estado MISSING_TOOL.
Si falta hardware, estado HARDWARE_REQUIRED.
Si falta lógica privada, estado IMPLEMENTACION_USUARIO_REQUERIDA.
