# IMPLEMENTACION_USUARIO_REQUERIDA

## Principio

Toda lógica privada o sensible debe quedar como:

IMPLEMENTACION_USUARIO_REQUERIDA

No se debe fingir funcionalidad.

## Patrón obligatorio

```python
from app.contracts.manual_required import ManualImplementationRequired

def execute(self, context):
    raise ManualImplementationRequired(
        "IMPLEMENTACION_USUARIO_REQUERIDA: conecta aquí tu lógica privada."
    )
```

Este patrón documenta el punto exacto de conexión para lógica privada o sensible. No debe presentarse como funcionalidad completa ni como ejecución exitosa.

## Debe aparecer en

- registry;
- panel;
- evidence;
- healthcheck;
- docs;
- technique detail.

## Cada técnica debe indicar

- archivo;
- clase;
- método;
- inputs;
- outputs;
- expected evidence;
- worker;
- dónde conectar la lógica privada.

## Reglas de visibilidad

- IMPLEMENTACION_USUARIO_REQUERIDA no se oculta.
- IMPLEMENTACION_USUARIO_REQUERIDA no se transforma en SUCCESS.
- IMPLEMENTACION_USUARIO_REQUERIDA no se marca como READY_CONTROLLED.
- IMPLEMENTACION_USUARIO_REQUERIDA debe bloquear ejecución real hasta que el usuario conecte lógica propia y revise permisos.
- IMPLEMENTACION_USUARIO_REQUERIDA debe quedar visible para LaIA, X5, Hermes, paneles, healthcheck y documentación.

## Relación con EvidenceStore

Cuando una técnica encuentre este estado, EvidenceStore debe registrar que la ejecución no ocurrió por falta de implementación privada conectada. Esa evidence no representa éxito técnico; representa trazabilidad del bloqueo correcto.

## Relación con LaIA/Mistral

LaIA debe reconocer este estado como una condición de parada o de solicitud de intervención del usuario. LaIA no debe inventar resultados ni sugerir que la técnica se completó.

## Relación con Hermes

Hermes puede proponer wrappers, parsers, schemas, paneles o tests estructurales alrededor de este estado, pero no puede sustituir la lógica privada del usuario ni promocionar una implementación sensible sin aprobación explícita.
