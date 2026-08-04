# DEFINITION OF DONE — OJO DE DIOS v0.1 LAB CORE

## Qué significa “acabado”

Ojo de Dios v0.1 Lab Core se considera acabado cuando:

- arranca en Windows;
- crea usuario Admin;
- muestra pantalla Nuevo objetivo;
- muestra Dashboard;
- carga los 16 módulos oficiales;
- carga todas las técnicas registradas;
- cada técnica tiene archivo propio;
- cada técnica tiene clase propia;
- cada técnica tiene campos propios;
- cada técnica tiene input_schema;
- cada técnica tiene panel_fields;
- cada técnica tiene worker asignado;
- cada técnica tiene permission_level;
- cada técnica tiene evidence_contract;
- cada técnica tiene demo_behavior;
- cada técnica tiene dry_run_behavior;
- cada técnica muestra su estado real;
- X5/OjoRouter puede planificar y lanzar jobs;
- LaIA/Mistral puede interpretar objetivo, proponer plan, rellenar parámetros y analizar evidence;
- Hermes puede crear propuestas reales en sandbox;
- EvidenceStore guarda resultados;
- ScoringEngine actualiza eficacia;
- VersionLock registra herramientas;
- Kill Switch para todo;
- Demo mode permite probar sin ejecución real;
- Attack Surface Graph relaciona target, host, puerto, servicio, producto, versión, CVE, técnica, worker y evidence;
- UI muestra dónde conectar lógica privada;
- README y documentos raíz explican el proyecto.

## Qué NO significa acabado

No significa que toda lógica privada esté implementada.

Las técnicas pendientes pueden estar correctamente como:

IMPLEMENTACION_USUARIO_REQUERIDA

Eso no es fallo si:

- tienen panel;
- tienen inputs;
- tienen worker;
- tienen evidence contract;
- tienen hook exacto;
- están registradas;
- aparecen en el panel;
- LaIA sabe explicarlas;
- X5 sabe tratarlas como MANUAL_REQUIRED;
- Hermes puede proponer mejoras en sandbox.

## Criterio de funcionalidad real

Una técnica solo puede marcarse funcional si:

- ejecuta algo real o demo real;
- devuelve evidence contract válido;
- no devuelve SUCCESS falso;
- no usa placeholder como resultado;
- no oculta errores;
- no ignora permisos;
- no ignora kill switch;
- no inventa evidence;
- no marca como hecho lo que está pendiente.

## Real no significa ficticio

Todo lo que el sistema diga que existe debe existir como archivo, clase, schema, panel, worker, evidence o configuración real.

No se permiten claims falsos.

Si algo no está implementado, debe decir claramente:

- IMPLEMENTACION_USUARIO_REQUERIDA
- MISSING_TOOL
- HARDWARE_REQUIRED
- MANUAL_REQUIRED
- DISABLED
- DRY_RUN_ONLY
- DEMO_ONLY


## Definición de acabado v1 — Knowledge Bootstrap IA/Hermes Agent

Ojo de Dios v1 no está acabado si falta:

- Knowledge Bootstrap definido e implementable;
- First Run Knowledge Load definido;
- Knowledge Refresh definido;
- AI status panel definido;
- Hermes initial knowledge definido;
- RAG vs fine-tuning decidido;
- context packs enlazados;
- JSON schema checks definidos;
- no secrets indexing definido;
- estados READY/STALE/FAILED definidos.

La documentación aspiracional debe seguir separada de runtime real. Nada se marca funcional sin evidence real y validación X5.
