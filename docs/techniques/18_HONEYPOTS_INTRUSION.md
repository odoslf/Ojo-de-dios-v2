# MÓDULO 18 — SISTEMA DE SEÑUELOS Y ANÁLISIS DE INTRUSIONES

## Propósito

Despliega servicios simulados y entornos señuelo para estudiar el comportamiento de actores maliciosos dentro de un alcance autorizado. Cuando un actor interactúa con el señuelo, el sistema perfila actividad de forma pasiva, analiza técnicas observadas, extrae indicadores de compromiso y prepara evidencias para revisión.

## Estado

Este módulo sigue en estado `reserved_future_module`: documenta el objetivo y las conexiones, pero no habilita contramedidas ni servicios activos por defecto. Toda lógica debe nacer como propuesta de laboratorio en `modules/laboratory/` y requerir aprobación antes de promoción.

## Conexiones

- Genera evidencias para el Módulo 16.
- Utiliza X5 únicamente para planificar o ejecutar respuestas predefinidas y aprobadas por política.
- Colabora con Mistral para análisis táctico, resumen de patrones e informes.
- Ante herramientas desconocidas, Hermes Agent puede capturarlas y estudiarlas en sandbox para proponer normalizadores o analizadores.

## Límites de implementación

- Las contramedidas como interrupción controlada o saturación de canales requieren autorización explícita, scope, Kill Switch y registro de auditoría.
- No se deben publicar servicios señuelo reales sin perfiles de aislamiento, retención de logs y redacción de secretos.
