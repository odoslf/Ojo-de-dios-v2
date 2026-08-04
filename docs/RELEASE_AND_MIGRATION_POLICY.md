# RELEASE AND MIGRATION POLICY — OJO DE DIOS

## Versionado

Usar SemVer:

MAJOR.MINOR.PATCH

Ejemplo:

- 0.1.0 Lab Core
- 0.2.0 Nuevos módulos conectados
- 0.2.1 Fix de panel
- 1.0.0 Primera versión estable

## Reglas

PATCH:

- correcciones;
- docs;
- fixtures;
- pequeños bugs;
- no rompe contratos.

MINOR:

- nuevas técnicas;
- nuevos plugins;
- nuevos paneles;
- nuevos parsers;
- nuevas capacidades compatibles.

MAJOR:

- rompe API;
- cambia contratos;
- cambia DB de forma incompatible;
- cambia plugin API.

## Migraciones DB

Toda modificación de tablas debe ir con migración.

Regla:

- no modificar DB a mano;
- crear migration;
- documentar upgrade;
- documentar rollback si aplica;
- proteger datos existentes.

## Release manifest

Cada release debe tener:

- release_id
- version
- date
- commit
- changed_files
- new_modules
- new_techniques
- new_plugins
- db_migrations
- version_locks
- known_issues
- rollback_notes

## Rollback

Cada cambio promocionado por Hermes o release debe tener rollback plan.
