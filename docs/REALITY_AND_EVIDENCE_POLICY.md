# REALITY AND EVIDENCE POLICY — OJO DE DIOS

## Principio

Ojo de Dios no debe fingir funcionalidad.

Todo resultado operativo debe estar respaldado por evidence verificable, estado explícito y contrato cumplido. Un texto generado por IA, un placeholder, una promesa futura o un mensaje de consola no equivalen a ejecución real.

## Qué significa real

Una capacidad es real cuando:

- existe archivo o componente declarado;
- existe contrato asociado;
- existe schema o validación de entradas cuando aplique;
- existe worker o binding declarado;
- respeta permisos, modo y kill switch;
- produce evidence contract válido;
- informa errores y bloqueos;
- puede distinguir demo, dry_run, ejecución controlada y manual_required.

## Estados que no son éxito

No son éxito:

- IMPLEMENTACION_USUARIO_REQUERIDA;
- MISSING_TOOL;
- HARDWARE_REQUIRED;
- MANUAL_REQUIRED;
- DISABLED;
- DRY_RUN_ONLY;
- DEMO_ONLY;
- FAILED;
- PARTIAL sin success_markers suficientes.

Estos estados pueden ser correctos y valiosos, pero no deben presentarse como SUCCESS.

## Evidence mínima

Cada ejecución o intento debe registrar, según aplique:

- job_id;
- run_id;
- target_id;
- module_id;
- technique_id;
- estado real;
- modo;
- permisos usados;
- summary;
- timestamps;
- archivos generados;
- hashes;
- salida normalizada;
- errores;
- stop_reason;
- manual_required si aplica.

## Prohibiciones

No se permite:

- devolver SUCCESS falso;
- inventar evidence;
- usar placeholders como findings;
- ocultar MISSING_TOOL;
- ocultar HARDWARE_REQUIRED;
- ocultar IMPLEMENTACION_USUARIO_REQUERIDA;
- convertir dry_run en ejecución real;
- convertir demo_fixture en resultado real;
- ejecutar fuera de registry;
- saltarse permission_level;
- saltarse kill switch.

## IA y realidad

LaIA/Mistral puede explicar, resumir y proponer planes, pero no puede declarar éxito operativo si EvidenceStore no contiene evidence válida.

Si el JSON de LaIA no valida, X5 no ejecuta.

## Hermes Agent y realidad

Hermes puede crear propuestas y piezas en sandbox, pero una proposal no es funcionalidad de producción.

Solo se considera promovida cuando existe aprobación, diff revisado, evidence demo o estructural, registro en VersionLock y reload controlado del registry.
