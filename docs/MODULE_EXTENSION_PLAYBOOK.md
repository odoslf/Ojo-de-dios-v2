# MODULE EXTENSION PLAYBOOK — OJO DE DIOS

## Cómo añadir una técnica a un módulo existente

Pasos:

1. Elegir módulo oficial.

2. Crear archivo:
   `app/modules/<module>/<technique_id>.py`

3. Crear clase:
   `<TechniqueName>Technique(BaseTechnique)`

4. Declarar:

   - technique_id;
   - module_id;
   - display_name;
   - tool_name;
   - version;
   - runtime;
   - worker;
   - permission_level;
   - panel_fields;
   - input_schema;
   - ai_fillable_inputs;
   - evidence_contract;
   - demo_behavior;
   - dry_run_behavior;
   - implementation_status.

5. Añadir fixture demo si aplica.

6. Añadir parser si aplica.

7. Añadir wrapper si usa herramienta externa.

8. Ejecutar registry validation.

9. Verificar panel.

10. Verificar LaIA explanation.

11. Verificar X5 plan.

12. Verificar evidence contract.

## Ejemplo OSINT

Nueva fuente OSINT:

- va en Módulo 1;
- crea connector;
- define API key en settings;
- no rompe OSINT existente;
- evidence normalizada.

## Ejemplo HackRF

Nueva técnica RF:

- va en Módulo 10;
- declara hardware;
- declara modo RX/TX;
- TX requiere confirmación;
- evidence incluye parámetros RF;
- transmisión sensible queda en IMPLEMENTACION_USUARIO_REQUERIDA si no está conectada.

## Ejemplo Android

Nueva técnica Android:

- va en Módulo 13;
- declara APK/perfil/output;
- LaIA puede rellenar campos;
- worker Android/WSL;
- evidence de build/artefacto;
- lógica privada en hook.

## Ejemplo Hermes

Nueva herramienta creada por Hermes:

- vive primero en `storage/hermes_lab/sandbox`;
- no entra en `app/` hasta aprobación;
- debe tener manifest;
- debe tener evidence;
- debe tener review;
- debe tener rollback.
