# BACKWARD COMPATIBILITY POLICY — OJO DE DIOS

## Contratos que no deben romperse sin versión mayor

- BaseTechnique;
- TechniqueRegistry;
- EvidenceContract;
- JobContract;
- AI JSON schemas;
- Plugin API;
- Panel schema;
- Worker interface;
- Hermes proposal manifest;
- VersionLock schema.

## Si hay cambio incompatible

Debe:

- subir MAJOR;
- documentar migración;
- mantener adapter si es posible;
- avisar en release notes;
- no romper plugins sin explicación.

## Deprecation policy

Antes de eliminar:

1. marcar deprecated;
2. documentar reemplazo;
3. mantener compatibilidad;
4. migrar datos;
5. eliminar solo con aprobación.
