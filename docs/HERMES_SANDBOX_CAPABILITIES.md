# HERMES SANDBOX CAPABILITIES — OJO DE DIOS

## Principio

Hermes puede crear piezas nuevas en laboratorio, pero no debe confundirse con ejecución real ni producción.

Hermes puede trabajar sobre capacidades sensibles solo como:

- propuesta;
- diseño;
- contrato;
- wrapper;
- parser;
- panel;
- worker stub;
- evidence writer;
- fixture;
- documentación;
- hook IMPLEMENTACION_USUARIO_REQUERIDA.

Hermes no debe activar lógica real sin aprobación y promoción controlada.

## Capacidades que Hermes puede proponer en sandbox

Hermes puede proponer:

- payload profiles;
- wrappers de herramientas;
- parsers de salida;
- conectores;
- panel fields;
- schemas;
- evidence writers;
- fixtures demo;
- mejoras de scoring;
- variantes de técnica;
- plantillas;
- módulos de laboratorio;
- plugins pip;
- skills.

También puede proponer estructuras para capacidades como:

- payloads;
- C2;
- phishing;
- credenciales;
- evasión;
- RF TX;
- cloud mutation;
- persistencia;
- post-explotación.

Pero solo como estructura de laboratorio y con:

IMPLEMENTACION_USUARIO_REQUERIDA

## Flujo obligatorio

1. LaIA/X5 detecta necesidad.
2. Hermes crea propuesta.
3. Hermes genera solo en sandbox.
4. Mistral revisa.
5. Tests estructurales validan imports/schemas/registry/evidence.
6. Panel muestra diff.
7. Admin aprueba o rechaza.
8. Solo si se aprueba, se promociona.
9. X5 puede usarlo si el modo/permisos lo permiten.

## Carpetas

```text
storage/hermes_lab/
├─ proposals/
├─ sandbox/
├─ evidence/
├─ diffs/
├─ logs/
├─ approvals/
├─ rejected/
└─ promoted/
```

## Estados

- draft
- designed
- generated
- tested
- review_required
- approved_by_user
- promoted
- rejected
- archived

## Permisos peligrosos bloqueados por defecto

- write_production
- modify_x5_core
- execute_live_target
- network_active_scan
- credential_testing
- rf_transmit
- android_device_action
- phishing_delivery
- cloud_mutation
- persistence_action

## Regla clave

Hermes puede diseñar el sitio exacto donde va la lógica.
Hermes no debe rellenar la lógica sensible dentro del chasis base.
El usuario conecta esa lógica en IMPLEMENTACION_USUARIO_REQUERIDA.
