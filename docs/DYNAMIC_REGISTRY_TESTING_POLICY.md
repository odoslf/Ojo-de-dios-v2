# Dynamic Registry Testing Policy — Ojo de Dios

## Propósito

Esta política corrige y bloquea un error de diseño que no debe repetirse en Ojo de Dios: tests demasiado rígidos que fallan por cambios legítimos de estructura, conteos o ampliaciones.

Ojo de Dios debe ser una plataforma ampliable. Si el usuario añade 1, 5, 20 o 100 técnicas nuevas, los tests no deben fallar por el simple hecho de que el número total cambió.

## Regla definitiva

El registry de Ojo de Dios es dinámico. El número total de técnicas es una métrica informativa, no una condición bloqueante. Los tests validan invariantes y contratos de cada técnica registrada, no un conteo fijo.

Quedan prohibidos los tests bloqueantes basados en conteo exacto fijo de técnicas, módulos, capabilities o wrappers, salvo que el test esté comprobando una migración concreta y temporal documentada.

## Prohibido

No se permite introducir tests o checks que bloqueen crecimiento legítimo con patrones como:

- `assert len(techniques) == 240`
- `assert len(techniques) == 242`
- `assert total_modules == 16` como bloqueo absoluto de futuro
- tests que fallen porque aparece una técnica nueva
- tests que fallen porque aparece un módulo experimental aprobado
- tests que fallen porque Hermes ha creado una proposal nueva
- tests que fallen por nombres/categorías/palabras
- tests que bloqueen por juicios externos no funcionales
- tests que obliguen a borrar técnicas nuevas legítimas
- tests que conviertan la arquitectura en rígida

## Permitido

Sí se permite y se recomienda:

- Registrar el número actual como métrica informativa.
- Mostrar `total de técnicas detectadas: X`.
- Comparar contra mínimo esperado cuando tenga sentido.
- Validar que no desaparecen técnicas base sin explicación.
- Validar que toda técnica nueva cumple contrato.
- Validar que toda técnica nueva tiene estado honesto.
- Validar que toda técnica nueva tiene permisos.
- Validar que toda técnica nueva tiene panel/evidence/worker contract si corresponde.
- Validar que los stubs sensibles usan `IMPLEMENTACION_USUARIO_REQUERIDA`.
- Validar que no se marca como funcional algo que no ejecuta lógica real.
- Validar que no hay duplicados de `technique_id`.
- Validar que los IDs siguen formato.
- Validar que X5/OjoRouter puede leer y decidir sobre todas las técnicas.

## Regla correcta de conteo

El conteo total de técnicas debe ser dinámico y auditado en tiempo de ejecución.

Ejemplo conceptual correcto:

1. Leer registry real.
2. Calcular total actual.
3. Mostrar total en informe.
4. Validar invariantes de cada técnica.
5. No fallar por total distinto si todas las técnicas cumplen contrato.

Ejemplo conceptual incorrecto:

1. Fijar total en un test.
2. Bloquear si el total cambia.
3. Obligar a modificar tests cada vez que se añade una técnica.

## Tests obligatorios correctos para registry

Los tests de registry deben proteger contratos, no conteos rígidos.

1. Todas las técnicas tienen `technique_id` único.
2. Todas las técnicas tienen `module_id` válido o `module_ref` válido.
3. Todas las técnicas tienen `name`, `description`, `status`, `permission_level`.
4. Todo `status` pertenece a la lista oficial.
5. Todo `permission_level` pertenece a la lista oficial.
6. Toda técnica sensible tiene `requires_confirmation=true`.
7. Toda técnica sensible sin lógica implementada tiene `requires_user_implementation=true`.
8. Toda técnica sensible sin lógica implementada usa `IMPLEMENTACION_USUARIO_REQUERIDA`.
9. Ningún stub se marca como `READY_CONTROLLED` si no tiene worker/contract/evidence real.
10. Toda técnica con panel visible tiene `panel_schema`.
11. Toda técnica con ejecución tiene `worker_contract`.
12. Toda técnica con resultado tiene `evidence_contract`.
13. Toda técnica con IA tiene `ai_contract` o contexto válido.
14. Toda técnica con riesgo alto requiere aprobación o modo controlado.
15. X5/OjoRouter puede cargar todas las técnicas sin romper.
16. El panel puede listar todas las técnicas sin depender de conteo fijo.
17. Los exports JSON/YAML se generan desde el registry real.
18. No hay API keys, secretos ni credenciales en metadata.
19. No hay rutas de producción escritas por proposals Hermes sin aprobación.
20. Las proposals Hermes no cuentan como técnicas productivas hasta promoción.

## Tests para módulos

No bloquear por número exacto absoluto de módulos.

Los 16 módulos oficiales son base obligatoria, pero pueden existir módulos futuros aprobados.

Correcto:

- Validar que los 16 módulos oficiales existen.
- Validar que todo módulo adicional tiene `module_manifest`.
- Validar que todo módulo adicional tiene aprobación/documentación.
- Validar que todo módulo adicional no rompe rutas, panel, registry ni workers.

Incorrecto:

- Fallar porque hay 17 módulos.
- Fallar porque Hermes creó un módulo experimental en sandbox.
- Fallar porque existe una capability transversal nueva.

## Tests para Hermes

Hermes debe poder crear propuestas sin romper producción.

Reglas:

- Una proposal puede existir sin ser producción.
- Una proposal no debe romper tests productivos.
- Las proposals se validan con tests propios de sandbox.
- Producción solo valida proposals promocionadas.
- Las carpetas `storage/hermes_lab/proposals/` no deben tratarse como módulos productivos.
- Los tests deben distinguir `proposal`, `sandbox`, `promoted` y `production`.

## Tests para Ransomware Resilience

No bloquear por añadir técnicas nuevas `ops.ransomware.*`.

Sí validar:

- Que toda técnica `ops.ransomware.*` tenga permisos correctos.
- Que las técnicas sensibles estén en `IMPLEMENTACION_USUARIO_REQUERIDA`.
- Que ninguna técnica sensible se marque como funcional si solo es conexión.
- Que el panel no prometa descifrado universal.
- Que `lab_encryption_with_escrow` y similares queden bloqueadas fuera de laboratorio.
- Que haya límites de `storage/ransomware_lab`.
- Que X5/OjoRouter pueda bloquear ejecución fuera de scope.
- Que kill switch y evidence sean obligatorios cuando corresponda.

## Aplicación obligatoria

Esta regla aplica a:

- TechniqueRegistry
- CapabilityRegistry
- ModuleRegistry
- Hermes proposals
- Tool Adoption Pipeline
- CVE-to-Technique Pipeline
- Ransomware Resilience Lab
- Export JSON/YAML
- Paneles
- Workers
- EvidenceStore
- X5/OjoRouter

## Principio definitivo

Los tests deben proteger funcionalidad, contratos, seguridad de ejecución, permisos, evidencia, estados honestos y ampliabilidad.

Los tests no deben proteger números rígidos ni impedir crecimiento legítimo.
