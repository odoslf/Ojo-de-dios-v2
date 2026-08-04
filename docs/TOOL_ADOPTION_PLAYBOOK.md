# TOOL ADOPTION PLAYBOOK — OJO DE DIOS

## Objetivo

Definir cómo adoptar una nueva herramienta sin romper el proyecto.

## Pasos para adoptar herramienta nueva

1. Identificar módulo.

2. Definir técnica o wrapper.

3. Definir herramienta y versión.

4. Definir runtime:

   - Windows;
   - WSL;
   - Docker;
   - Hardware;
   - Cloud;
   - Android;
   - Hermes sandbox.

5. Definir permisos.

6. Definir inputs.

7. Definir outputs.

8. Definir evidence.

9. Definir parser.

10. Definir panel_fields.

11. Definir demo/dry_run behavior.

12. Registrar VersionLock.

13. Documentar en inventario.

## No sustituir silenciosamente

Una herramienta nueva no elimina otra herramienta oficial salvo aprobación.

Puede coexistir como:

- alternativa;
- fallback;
- variante;
- wrapper nuevo;
- parser nuevo;
- técnica nueva.

## Obsolescencia

Si una herramienta queda obsoleta:

- marcar DEPRECATED;
- mantener técnica visible;
- añadir recomendación;
- no borrar hasta migración aprobada;
- documentar reemplazo.

## Herramienta privada

Si el usuario aporta herramienta privada:

- registrar como local_tool;
- no subir binarios si no procede;
- documentar ruta configurable;
- guardar en VersionLock si aplica;
- evidence debe indicar tool_id.
