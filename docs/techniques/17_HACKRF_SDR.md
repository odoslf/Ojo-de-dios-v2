# MÓDULO 17 — LABORATORIO DE RADIOFRECUENCIA (HACKRF ONE)

## Propósito

Gestiona el dispositivo HackRF One para realizar pruebas de seguridad en el espectro radioeléctrico autorizado, desde 1 MHz hasta 6 GHz. El alcance documental incluye análisis de espectro, replicación controlada de señales Sub-GHz, evaluación de sistemas TETRA/TETRAPOL, auditoría de redes móviles GSM/LTE, verificación de sistemas de navegación GPS, pruebas de audio Bluetooth y análisis de señales especiales como TPMS y ADS-B.

## Estado

Este módulo sigue en estado `reserved_future_module`: define intención, conexiones y límites, pero no declara técnicas ejecutables, workers listos ni comandos operativos. Cualquier implementación real debe entrar primero en `modules/laboratory/`, pasar por sandbox, revisión, manifiesto de promoción y aprobación explícita.

## Conexiones

- Comparte superficie de hardware y evidencias RF con el Módulo 10 (Wireless/RF general).
- Envía evidencias normalizadas al Módulo 16 (Gestión de Evidencias y Trazabilidad).
- Colabora con LaIA/Mistral para sugerir parámetros no operativos y preparar informes.
- Ante protocolos desconocidos, solicita a Hermes Agent una investigación y propuestas de analizadores en `modules/laboratory/`.

## Límites de implementación

- No se deben añadir transmisiones, replay ni decodificadores operativos sin control de scope, autorización, Kill Switch, EvidenceStore y AuditLog.
- Las capturas IQ, logs y capturas de pantalla deben registrar hashes y cadena de custodia antes de promoción.
