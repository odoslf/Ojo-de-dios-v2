# TOOLS AND MODULES IMPLEMENTATION MAP — OJO DE DIOS

## Principio

Ojo de Dios debe tener todas las conexiones preparadas, pero sin fingir funcionalidad.

Cada técnica debe tener:

- archivo propio;
- clase propia;
- panel_fields propios;
- input_schema propio;
- ai_fillable_inputs;
- worker_binding;
- permission_level;
- evidence_contract;
- dry_run_behavior;
- demo_behavior;
- user_logic_hook;
- implementation_status.

Si una técnica requiere lógica privada, debe quedar como:

IMPLEMENTACION_USUARIO_REQUERIDA

No se permite registrar técnicas genéricas sin campos concretos.

## Módulos oficiales

1. OSINT
2. Vulnerabilidades
3. Explotación servicios de red
4. Intrusión web avanzada
5. Credenciales
6. MITM / Red
7. Post-explotación
8. DoS / Resiliencia
9. Scraping Inteligente X4 + X5 + IA
10. Wireless / RF general
11. IoT / físicos
12. Orquestación X5 + IA + Hermes Agent Lab
13. Android
14. Phishing
15. Cloud / Containers / Kubernetes
16. Excelencia operativa / Evidence / Calidad / Mantenimiento

DNS no es módulo independiente.

DNS se integra en:

- OSINT;
- Vulnerabilidades;
- MITM / Red.

## Responsabilidad por capa

### Panel

Debe mostrar:

- técnica;
- estado;
- campos;
- permisos;
- worker;
- evidence esperada;
- explicación LaIA;
- botón demo;
- botón dry_run;
- botón ejecutar si aplica;
- aviso IMPLEMENTACION_USUARIO_REQUERIDA si aplica.

### LaIA / Mistral

Debe:

- interpretar objetivo;
- entender Attack Surface Graph;
- planificar técnicas registradas;
- rellenar parámetros;
- explicar campos;
- analizar evidence;
- decidir fallback;
- pedir mejora a Hermes;
- devolver JSON validado.

No debe:

- ejecutar comandos libres;
- inventar técnicas;
- saltarse registry;
- marcar stubs como funcionales.

### X5 / OjoRouter

Debe:

- validar plan;
- validar permisos;
- validar modo;
- validar scope;
- seleccionar worker;
- crear job;
- ejecutar mediante worker;
- guardar evidence;
- actualizar scoring;
- decidir siguiente paso.

### Hermes Agent Lab

Debe:

- crear propuestas;
- crear wrappers;
- crear parsers;
- crear schemas;
- crear paneles de laboratorio;
- crear workers de laboratorio;
- crear fixtures;
- crear tests estructurales;
- crear documentación;
- preparar variantes en sandbox.

No debe:

- ejecutar producción;
- autoaprobarse;
- tocar producción sin aprobación;
- activar lógica sensible;
- marcar stubs como funcionales.

### Usuario

Conecta la lógica privada dentro de:

IMPLEMENTACION_USUARIO_REQUERIDA

El chasis debe dejarle claro:

- archivo;
- clase;
- método;
- inputs;
- outputs;
- evidence esperada;
- worker;
- cómo probar en demo/dry_run.

## Estado real implementado hasta Ronda 29

El dashboard y los manifests de los módulos trabajados ya no dependen solo de `readiness=documented`. El estado real se calcula desde `app.core.module_dashboard_status` cruzando registry, documentación, tools y workspace. Los módulos con implementación real registrada son:

- `m01_osint`: 47 técnicas registradas `READY_CONTROLLED`.
- `m03_network_services`: 3 técnicas pasivas/read-only `READY_CONTROLLED`.
- `m09_scraping_intelligence`: 9 técnicas registradas, 7 base `READY_CONTROLLED` y 2 `READY_LOCAL_AI`.
- `m12_orchestration`: 1 técnica de planificación/orquestación `READY_CONTROLLED`.
- `m15_cloud`: 4 auditorías cloud/container/Kubernetes read-only `READY_CONTROLLED`.
- `m16_ops_quality`: checks reales de readiness/evidence/version-lock/runtime/export/Hermes, sin técnicas registry propias.
- `m18_honeypots_deception`: 3 técnicas defensivas `READY_CONTROLLED`, manteniendo su ciclo de vida reservado en catálogo.

Los módulos no listados siguen siendo manifest/documentación o lógica existente previa; no deben marcarse como completos por arrastre.
