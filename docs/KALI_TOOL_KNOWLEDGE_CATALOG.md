# KALI TOOL KNOWLEDGE CATALOG — OJO DE DIOS

## Propósito

Ojo de Dios debe tratar Kali y herramientas externas como catálogo de capacidades versionadas, no como cerebro del sistema.

LaIA consulta fichas.
X5 decide.
Workers ejecutan solo si procede.
EvidenceStore guarda la verdad.

Este documento no instala ni ejecuta herramientas. Define cómo documentarlas para que futuras rondas implementen ingesta, ToolHealth, VersionLock, parsers y workers sin improvisar.

## docs/tools/

Cada herramienta debe tener ficha local en docs/tools/.

Ejemplos:

- docs/tools/nmap.md
- docs/tools/nuclei.md
- docs/tools/metasploit.md
- docs/tools/hydra.md
- docs/tools/sqlmap.md
- docs/tools/hashcat.md
- docs/tools/john.md
- docs/tools/impacket.md
- docs/tools/netexec.md
- docs/tools/testssl.md
- docs/tools/hackrf.md
- docs/tools/ollama_mistral.md
- docs/tools/x4_connector.md
- docs/tools/x5_ojrouter.md
- docs/tools/hermes_agent.md

No es obligatorio crear todas las fichas en esta ronda. Este documento define el contrato documental.

## Campos obligatorios de cada ficha

- tool_id
- name
- category
- module_ids
- technique_ids
- official_url
- documentation_url
- kali_package_name
- recommended_version
- installed_version
- version_lock_id
- runtime
- platform
- requires_wsl
- requires_docker
- requires_hardware
- requires_network
- requires_credentials
- permission_level
- default_mode
- can_run_in_demo
- can_run_in_dry_run
- input_formats
- output_formats
- safe_output_mode
- parser
- evidence_contract
- known_errors
- healthcheck_method
- update_policy
- notes_for_laia
- notes_for_x5
- notes_for_hermes
- requires_user_implementation

## Diferencia entre herramienta instalada y técnica disponible

Una herramienta puede estar instalada pero una técnica seguir como IMPLEMENTACION_USUARIO_REQUERIDA.

LaIA debe diferenciar:

- tool_available;
- technique_registered;
- worker_available;
- parser_available;
- evidence_contract_available;
- permission_allowed;
- execution_allowed;
- user_logic_required.

Ejemplo: que `nmap` exista en una máquina no significa que Ojo de Dios tenga técnica registrada, worker validado, parser, evidence contract y permiso para usarlo contra un target concreto.

## VersionLock

Toda herramienta oficial debe acabar con VersionLock:

- tool_id;
- name;
- resolved_version;
- source_url;
- runtime;
- binary_hash si aplica;
- locked_at;
- status.

VersionLock evita que LaIA invente versiones y permite saber qué salida puede esperar un parser.

## ToolHealth

Cada herramienta debe tener healthcheck cuando se implemente:

- OK;
- WARNING;
- MISSING_OPTIONAL;
- MISSING_REQUIRED;
- FAILED.

Herramientas opcionales ausentes no deben romper arranque.

ToolHealth no sustituye permisos, scope ni registry. Solo informa disponibilidad.

## LaIA y herramientas

LaIA puede explicar:

- para qué sirve una herramienta;
- qué módulo la usa;
- qué inputs necesita;
- qué evidence produce;
- qué errores frecuentes tiene;
- si falta instalación;
- si requiere WSL/Docker/hardware;
- si X5 puede usarla.

LaIA no puede:

- inventar comandos;
- inventar rutas;
- inventar versión instalada;
- ejecutar directamente;
- recomendar uso fuera de scope;
- saltarse registry.

## Hermes Agent y herramientas

Hermes puede proponer:

- ficha docs/tools nueva;
- wrapper;
- parser;
- fixture;
- healthcheck;
- panel fields;
- evidence writer;
- test estructural;
- connector de laboratorio.

Hermes debe dejar IMPLEMENTACION_USUARIO_REQUERIDA cuando la lógica sea privada o sensible.

Hermes no puede promocionar una herramienta como funcional sin approval, VersionLock, ToolHealth, evidence contract, tests y registry válido.

## Catálogo futuro por módulos

Cada módulo oficial debe acabar con herramientas asociadas, pero sin crear aquí todas las fichas todavía.

La relación esperada será:

- módulo oficial;
- capacidades del módulo;
- herramientas candidatas;
- técnicas registradas;
- workers disponibles;
- parsers;
- evidence contracts;
- permiso mínimo;
- modo demo/dry_run/controlled/expert;
- límites de scope.

## Regla anti-invención

Si una ficha no existe, LaIA debe responder MISSING_DOC o UNKNOWN para detalles específicos de esa herramienta. Si una herramienta no tiene ToolHealth o VersionLock real, LaIA no debe afirmar versión instalada ni disponibilidad operativa.
