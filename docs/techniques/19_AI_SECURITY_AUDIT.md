# MÓDULO 19 — AUDITORÍA DE SEGURIDAD EN SISTEMAS DE IA

## Propósito

Evalúa la seguridad de sistemas de inteligencia artificial en tres niveles: infraestructura de servidores y APIs, modelos frente a extracción o manipulación de datos, y aplicaciones que integran IA mediante controles de contenido, identidad y autorización.

## Estado

Este módulo sigue en estado `reserved_future_module`: aporta una definición normalizada para futuras pruebas, sin técnicas ejecutables ni explotación activa. Los casos de prueba deben ser generados, revisados y ejecutados bajo autorización, con evidencias trazables.

## Conexiones

- Mistral genera casos de prueba seguros y analiza respuestas dentro del scope.
- Hermes Agent investiga nuevos mecanismos de defensa y propone módulos de prueba en `modules/laboratory/`.
- Los tokens, claves o secretos detectados se derivan al Módulo 5 (Credenciales) con redacción y clasificación.
- Las evidencias se almacenan en el Módulo 16.

## Límites de implementación

- No se deben registrar prompts, respuestas ni secretos sin redacción adecuada.
- Las pruebas de extracción, bypass o suplantación deben permanecer en modo autorizado, reproducible y auditable.
