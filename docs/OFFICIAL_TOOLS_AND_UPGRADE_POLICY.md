# OFFICIAL TOOLS AND UPGRADE POLICY — OJO DE DIOS

## Principio

Las herramientas listadas en la hoja de ruta son herramientas oficiales del proyecto.

No están bloqueadas para el usuario.
Están protegidas contra sustitución silenciosa.

## No sustitución silenciosa

No se puede:

- eliminar una herramienta oficial;
- sustituirla por una más suave;
- rebajar su capacidad;
- renombrar technique_id sin migración;
- cambiar herramienta porque no esté instalada;
- cambiar herramienta por comodidad;
- convertir técnica activa en simple check pasivo;
- ocultar que falta implementación.

## Cambios permitidos

Una herramienta puede cambiar si:

1. Hay versión superior compatible.
2. Está obsoleta oficialmente.
3. El repositorio cambió de nombre.
4. La herramienta ya no existe.
5. Hay alternativa técnicamente superior documentada.
6. El usuario aprueba el cambio.

## Versiones

Usar:

- versión exacta cuando esté fijada;
- latest-release-lock cuando cambie mucho;
- VersionLock para registrar resolved_version, source, hash, runtime y fecha.

## Si falta herramienta

Marcar:

MISSING_TOOL

No borrar técnica.

## Si falta hardware

Marcar:

HARDWARE_REQUIRED

No borrar técnica.

## Si falta lógica privada

Marcar:

IMPLEMENTACION_USUARIO_REQUERIDA

No fingir funcionalidad.

## Añadir nuevas herramientas

Se pueden añadir herramientas nuevas si:

- tienen módulo asignado;
- tienen técnica o wrapper;
- tienen panel_fields;
- tienen worker;
- tienen evidence_contract;
- tienen permission_level;
- pasan registry validation;
- quedan en VersionLock.
