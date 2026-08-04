# Workspace Angel/Hermes — modules/laboratory/

## Proposito

`modules/laboratory/` es el espacio aislado donde Angel/Hermes prepara propuestas
experimentales antes de cualquier promocion al producto. Nada dentro de esta
carpeta se considera produccion hasta que exista aprobacion del operador,
revision y manifest de promocion.

## Estados

- `experimental`: idea o prototipo inicial sin validacion completa.
- `lab_ready`: artefacto preparado para pruebas en sandbox.
- `review_required`: requiere revision tecnica o humana antes de continuar.
- `approved_by_user`: el operador aprobo explicitamente la propuesta.
- `promoted`: la propuesta fue promocionada mediante flujo controlado.
- `rejected`: la propuesta fue descartada, bloqueada o archivada.

## Estructura esperada por tecnica

Cada tecnica o modulo experimental debe vivir en su propia carpeta dentro del
workspace, por ejemplo:

```text
modules/laboratory/_sandbox/nombre_tecnica/
  technique.json
  worker.py
  parser/
  evidence_schema.json
  requirements.generated.txt
  README.md
  PROMOTION_MANIFEST.json
```

Archivos esperados:

- `technique.json`: descripcion declarativa, parametros y estado.
- `worker.py`: codigo experimental de laboratorio, si aplica.
- `parser/`: parsers o normalizadores asociados.
- `evidence_schema.json`: esquema de evidencias generado o propuesto.
- `requirements.generated.txt`: dependencias necesarias, no instaladas sin confirmacion.
- `README.md`: uso, limites, riesgos y pruebas sugeridas.
- `PROMOTION_MANIFEST.json`: manifest de promocion, rollback y aprobacion.

## Reglas de promocion

- Angel/Hermes no promociona sin aprobacion del operador.
- Toda promocion requiere `PROMOTION_MANIFEST.json`.
- Toda dependencia nueva requiere confirmacion previa.
- Toda propuesta debe indicar riesgos, pruebas sugeridas y plan de rollback.
- El estado debe pasar por `review_required` antes de `approved_by_user`.
- Solo las propuestas `approved_by_user` pueden aspirar a `promoted`.

## Rollback

Cada manifest de promocion debe incluir:

- archivos creados o modificados;
- dependencias añadidas;
- comandos de verificacion;
- evidencias generadas;
- pasos para revertir cambios;
- estado recomendado si falla la promocion.
