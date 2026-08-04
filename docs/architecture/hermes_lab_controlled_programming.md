# Hermes Agent Lab con lápiz controlado y canales LaIA/Hermes Agent

## 1. Decisión oficial

Hermes Agent Lab / Evolution Engine queda definido como la capa transversal de laboratorio, creación y evolución controlada de Ojo de Dios. Hermes no es decorativo. Hermes tiene lápiz controlado: puede investigar, generar, adaptar y preparar código real en laboratorio cuando el usuario se lo ordene o cuando el sistema detecte una necesidad técnica, como una CVE nueva, una dependencia faltante, un parser inexistente, un wrapper necesario, una mejora de panel, un schema de evidencia o una capacidad que todavía no exista en el catálogo activo.

Hermes nunca promociona por sí solo nada al catálogo activo. Toda propuesta debe pasar por sandbox, contratos, evidencia, tests estructurales, revisión Mistral/LaIA, validación X5/OjoRouter y aprobación explícita del usuario.

Hermes no sustituye a X5/OjoRouter. Hermes no sustituye a Mistral/LaIA. Hermes crea y evoluciona en laboratorio. Mistral/LaIA razona, planifica y revisa. X5/OjoRouter valida y ejecuta lo permitido. El usuario aprueba.

## 2. Roles oficiales

| Componente | Rol | Puede hacer | No puede hacer |
|---|---|---|---|
| Usuario | Propietario y aprobador final. | Pedir creación, pedir incorporación de lógica, aprobar promoción, rechazar propuestas, activar modos y decidir qué entra al catálogo activo. | No aplica como restricción interna del sistema, pero el sistema debe exigir scope, permisos, confirmaciones y trazabilidad. |
| Mistral/LaIA | Cerebro operativo. | Interpretar intención, planificar cadenas, rellenar parámetros, analizar evidencia, explicar resultados, revisar propuestas Hermes Agent y generar informes. | Programar técnicas nuevas directamente, tocar producción, ejecutar comandos libres, inventar resultados o saltarse X5/OjoRouter. |
| Hermes Agent Lab | Laboratorio de creación y evolución. | Investigar, verificar dependencias, generar propuestas, crear código en sandbox, adaptar lógica entregada por el usuario, preparar wrappers, parsers, schemas, paneles, tests y documentación. | Operar objetivos reales, autopromocionar capacidades, tocar catálogo activo sin aprobación o fingir lógica sensible. |
| X5/OjoRouter | Motor de decisión, validación y ejecución controlada. | Validar registry, permisos, scope, modo, contratos, estado, evidence y ejecución permitida. | Inventar técnicas, saltarse approval, ejecutar fuera de scope o aceptar JSON inválido. |
| TechniqueRegistry | Fuente oficial de capacidades. | Registrar técnicas, permisos, inputs, evidence contract, worker y estado. | Marcar como funcional una técnica IMPLEMENTACION_USUARIO_REQUERIDA o aceptar duplicados sin control. |
| EvidenceStore | Verdad operativa de resultados. | Guardar evidencia, hashes, timestamps, modo, origen y resultado. | Aceptar éxito sin evidencia útil o convertir demo/dry_run en ejecución real. |
| ScoringEngine | Aprendizaje controlado por resultados. | Ajustar puntuación según evidence real, modo y resultado. | Fingir aprendizaje, subir score por SUCCESS vacío o puntuar demo como ejecución real. |
| JobRunner | Ejecución orquestada de trabajos aprobados. | Lanzar workers autorizados, respetar kill switch y registrar eventos. | Ejecutar propuestas Hermes no promocionadas o saltarse permisos. |
| DeepSeek Assist | Apoyo de investigación/generación para Hermes. | Ayudar a investigar documentación, librerías, APIs, estructura, código de laboratorio y alternativas. | Ejecutar en producción, aprobarse, saltarse Hermes, saltarse Mistral/LaIA o saltarse X5/OjoRouter. |

## 3. Dos chats separados

Ojo de Dios debe distinguir dos canales conversacionales internos.

### Chat LaIA/Mistral

Canal operativo.

Sirve para:

- analizar un objetivo autorizado;
- entender una petición del usuario;
- rellenar parámetros;
- planificar cadena de técnicas registradas;
- interpretar evidencia;
- explicar bloqueos;
- recomendar siguiente paso;
- revisar propuestas Hermes antes de promoción;
- generar informes.

Ejemplos de mensajes del usuario:

- "Analiza este dominio autorizado."
- "Planifica la siguiente cadena dentro del scope."
- "Rellena los parámetros de esta técnica."
- "Explícame esta evidencia."
- "Revisa esta propuesta de Hermes."
- "¿Qué falta para poder ejecutar esto?"

LaIA/Mistral debe responder con JSON estructurado validable cuando la respuesta vaya a alimentar X5/OjoRouter. Si el JSON no valida, X5/OjoRouter no ejecuta.

### Chat Hermes

Canal de laboratorio.

Sirve para:

- crear propuestas de técnicas;
- investigar CVEs o capacidades nuevas;
- verificar librerías y dependencias;
- generar wrappers, parsers, schemas, paneles, tests y documentación en sandbox;
- adaptar lógica entregada por el usuario;
- preparar promotion_manifest;
- pedir revisión Mistral/LaIA;
- dejar una propuesta en review_required;
- preparar incorporación al catálogo activo cuando el usuario lo apruebe.

Ejemplos de mensajes del usuario:

- "Hermes, crea una propuesta para esta CVE."
- "Hermes, verifica esta librería y prepara wrapper."
- "Hermes, incorpora esta lógica mía en el punto exacto."
- "Hermes, prepara esta capacidad para el catálogo activo."
- "Hermes, genera tests estructurales y manifiesto."
- "Hermes, pásalo a revisión."

Hermes no debe operar objetivos reales. Hermes crea en laboratorio.

## 4. Qué significa "Hermes tiene lápiz"

"Hermes tiene lápiz" significa que Hermes puede escribir código real, documentación real, contratos reales, schemas reales, tests reales y propuestas reales dentro de un espacio de laboratorio controlado.

No significa que Hermes pueda modificar producción sin permiso.

Hermes puede crear o modificar únicamente dentro de rutas futuras de laboratorio, por ejemplo:

```text
app/lab/hermes/proposals/<proposal_id>/
app/lab/hermes/sandbox/<proposal_id>/
storage/hermes_lab/<proposal_id>/
```

Estas rutas se documentan como diseño objetivo. Este documento no las crea todavía.

Una propuesta Hermes futura podrá contener:

```text
technique.py
schema.py
worker_adapter.py
evidence_contract.py
panel_fields.json
requirements.lock.json
README.md
promotion_manifest.json
tests/
diff_summary.md
mistral_review.json
x5_validation.json
approval_record.json
```

## 5. Estados oficiales Hermes

Estados oficiales:

- draft
- designed
- generated
- tested
- review_required
- approved_by_user
- promoted
- rejected
- archived

Definiciones:

- draft: idea inicial sin diseño cerrado.
- designed: la propuesta tiene contrato, alcance, permisos, inputs, outputs y evidence esperada definidos.
- generated: Hermes ha generado archivos en sandbox/lab.
- tested: se han ejecutado pruebas estructurales permitidas sobre la propuesta.
- review_required: la propuesta espera revisión Mistral/LaIA y revisión humana.
- approved_by_user: el usuario ha aprobado explícitamente la promoción.
- promoted: la propuesta ha sido incorporada al catálogo activo por flujo controlado.
- rejected: la propuesta ha sido rechazada y no puede ejecutarse.
- archived: la propuesta queda guardada como histórico, sin ejecución ni promoción.

Regla obligatoria:

Solo approved_by_user puede pasar a promoted.

## 6. Incorporación de lógica bajo pedido del usuario

Hermes puede incorporar lógica al catálogo activo cuando el usuario se lo pida explícitamente, pero nunca directamente en producción.

Flujo obligatorio:

1. El usuario entrega o describe la lógica.
2. Hermes crea una proposal en sandbox.
3. Hermes identifica el punto exacto de conexión.
4. Hermes adapta imports, clase, contrato, schema, worker_adapter y evidence_contract.
5. Hermes verifica dependencias sin instalar nada fuera del entorno permitido.
6. Hermes genera tests estructurales.
7. Hermes ejecuta solo pruebas permitidas de contrato, demo o dry_run.
8. Hermes deja promotion_manifest.
9. Mistral/LaIA revisa la propuesta.
10. X5/OjoRouter valida registry, permisos, scope, modo y contratos.
11. El usuario aprueba o rechaza.
12. Solo tras aprobación explícita se puede promocionar al catálogo activo.

Si la lógica es sensible, privada o no implementable por el asistente, Hermes debe dejar el punto exacto con IMPLEMENTACION_USUARIO_REQUERIDA. Si el usuario entrega esa lógica privada y ordena incorporarla, Hermes puede adaptarla al contrato en laboratorio, pero no puede operar con ella fuera del flujo aprobado ni promocionarla sin aprobación.

## 7. Detección automática de CVE o necesidad técnica

Cuando Ojo de Dios detecte una CVE, una tecnología, un servicio, una librería, un parser faltante o una técnica inexistente en el catálogo activo, Hermes puede iniciar una propuesta de laboratorio si el modo y permisos lo permiten.

Hermes puede:

- recopilar información técnica;
- consultar fuentes configuradas;
- verificar si existen librerías reales;
- crear diseño de técnica;
- preparar wrapper;
- preparar schema;
- preparar panel fields;
- preparar evidence contract;
- preparar tests estructurales;
- generar documentación;
- dejar proposal en review_required.

Hermes no puede:

- ejecutar automáticamente una capacidad recién detectada;
- operar fuera del scope definido;
- ejecutar pruebas reales fuera de los modos aprobados;
- promocionar la técnica sin usuario;
- marcar éxito sin evidence;
- saltarse Mistral/LaIA;
- saltarse X5/OjoRouter.

Detectar una CVE no equivale a autorizar ejecución. Detectar una CVE solo puede abrir una propuesta Hermes de laboratorio. La ejecución real depende de scope, permisos, modo, registry, X5/OjoRouter, evidence y aprobación del usuario.

## 8. Frase oficial de arquitectura

Mistral/LaIA piensa y revisa. X5/OjoRouter valida y ejecuta. Hermes crea y evoluciona en laboratorio. EvidenceStore prueba lo ocurrido. ScoringEngine aprende de resultados reales. El usuario aprueba lo que entra al catálogo activo.

## 9. Flujo completo de promoción al catálogo activo

Una capacidad creada por Hermes solo puede entrar al catálogo activo mediante este flujo:

1. Necesidad detectada:
   - petición directa del usuario;
   - CVE detectada;
   - servicio desconocido;
   - parser faltante;
   - wrapper faltante;
   - librería necesaria;
   - error repetido;
   - evidencia incompleta;
   - propuesta de mejora;
   - técnica privada entregada por el usuario.

2. Creación de proposal:
   - Hermes crea una propuesta en laboratorio;
   - asigna proposal_id;
   - define módulo destino;
   - define technique_id candidato;
   - define permiso necesario;
   - define inputs;
   - define outputs;
   - define evidence esperada;
   - define worker previsto;
   - define dependencias;
   - define estado inicial.

3. Diseño:
   - Hermes comprueba si la técnica ya existe;
   - comprueba si hay duplicados;
   - comprueba si encaja en el índice oficial de 16 módulos;
   - comprueba si es Hermes, Mistral, X5, Evidence, Scoring o módulo especializado;
   - no crea módulo nuevo si ya existe uno oficial;
   - no crea DNS independiente;
   - no altera Módulo 9.

4. Generación en laboratorio:
   - Hermes genera archivos solo en sandbox/lab;
   - si la lógica es permitida, puede generar código real;
   - si la lógica es sensible, deja IMPLEMENTACION_USUARIO_REQUERIDA;
   - si el usuario entrega lógica privada, Hermes puede adaptarla al contrato en laboratorio;
   - nunca opera objetivos reales desde laboratorio.

5. Verificación de dependencias:
   - Hermes identifica librerías necesarias;
   - verifica nombre real;
   - verifica versión;
   - verifica licencia cuando sea relevante;
   - verifica compatibilidad con Python, Windows y Linux si aplica;
   - registra origen;
   - no instala en producción;
   - no añade requirements sin promoción aprobada.

6. Tests estructurales:
   - imports del sandbox si aplica;
   - contrato de technique;
   - contrato de schema;
   - contrato de evidence;
   - contrato de panel_fields;
   - contrato de promotion_manifest;
   - validación de que no hay autopromoción;
   - validación de que no hay ejecución real;
   - validación de que IMPLEMENTACION_USUARIO_REQUERIDA no se marca como funcional.

7. Revisión Mistral/LaIA:
   - analiza coherencia;
   - revisa inputs/outputs;
   - revisa evidence esperada;
   - revisa permisos;
   - revisa bloqueos;
   - revisa riesgos técnicos;
   - no aprueba por sí sola;
   - emite recomendación.

8. Validación X5/OjoRouter:
   - valida registry;
   - valida scope;
   - valida modo;
   - valida permisos;
   - valida confirmación;
   - valida evidence contract;
   - valida que la propuesta no rompe contratos;
   - no ejecuta proposals no promocionadas.

9. Decisión del usuario:
   - aprobar;
   - pedir cambios;
   - rechazar;
   - archivar;
   - mantener en laboratorio.

10. Promoción:
    - solo si estado approved_by_user;
    - se copia o incorpora al catálogo activo;
    - se registra approval;
    - se genera evidence de promoción;
    - se actualiza VersionLock;
    - se conserva trazabilidad;
    - queda en estado promoted.

Ninguna propuesta Hermes puede saltar de generated, tested o review_required a promoted. El único camino válido es review_required -> approved_by_user -> promoted.

## 10. Modos de interacción del usuario

El usuario puede interactuar con LaIA/Mistral y Hermes Agent de forma separada.

### Interacción con LaIA/Mistral

LaIA/Mistral debe actuar como cerebro operativo.

Ejemplo:

Usuario: "Analiza este dominio autorizado dentro del scope."

LaIA/Mistral debe:

- interpretar el objetivo;
- comprobar scope;
- consultar Attack Surface Graph;
- seleccionar técnicas registradas;
- rellenar parámetros;
- pedir confirmación si corresponde;
- enviar plan validable a X5/OjoRouter;
- analizar evidence;
- recomendar siguiente paso.

LaIA/Mistral no debe:

- crear técnica nueva directamente;
- modificar código;
- instalar librerías;
- tocar catálogo activo;
- saltarse Hermes;
- saltarse X5/OjoRouter;
- inventar éxito.

### Interacción con Hermes

Hermes debe actuar como laboratorio.

Ejemplo:

Usuario: "Hermes, incorpórame esta librería al módulo tal."

Hermes debe:

- verificar si la librería existe;
- documentar versión y origen;
- crear propuesta en sandbox;
- preparar wrapper o adapter si procede;
- preparar requirements candidate;
- preparar tests estructurales;
- preparar promotion_manifest;
- dejar estado review_required.

Ejemplo:

Usuario: "Hermes, incorpora esta lógica al catálogo activo."

Hermes debe:

- no tocar producción;
- crear proposal;
- localizar punto exacto de conexión;
- adaptar la lógica al contrato;
- marcar dependencias;
- generar tests estructurales;
- pedir revisión Mistral/LaIA;
- dejar listo para aprobación del usuario.

Ejemplo:

Usuario: "Hermes, crea capacidad para esta CVE."

Hermes debe:

- crear propuesta de laboratorio;
- recopilar información;
- mapear CVE a módulo o técnica candidata;
- definir permisos;
- definir evidence esperada;
- dejar IMPLEMENTACION_USUARIO_REQUERIDA si la lógica es sensible;
- no ejecutar nada automáticamente;
- no operar objetivos reales desde laboratorio;
- dejar review_required.

## 11. Errores específicos y bloqueos

Los errores deben ser claros, accionables y no moralizantes.

Lista oficial de errores Hermes:

- HERMES_PROPOSAL_NOT_FOUND: no existe la propuesta solicitada.
- HERMES_INVALID_STATE_TRANSITION: la propuesta intenta saltar un estado no permitido.
- HERMES_REQUIRES_USER_APPROVAL: la acción requiere aprobación explícita del usuario.
- HERMES_PRODUCTION_WRITE_BLOCKED: Hermes intentó escribir fuera de laboratorio o sandbox.
- HERMES_AUTOPROMOTION_BLOCKED: Hermes intentó promocionar una propuesta sin aprobación.
- HERMES_REAL_EXECUTION_BLOCKED: Hermes intentó ejecutar una acción operativa real desde laboratorio.
- HERMES_SENSITIVE_LOGIC_REQUIRED: la capacidad requiere lógica privada del usuario.
- HERMES_USER_LOGIC_ADAPTATION_REQUIRED: la lógica entregada por el usuario debe adaptarse al contrato antes de revisión.
- HERMES_DEPENDENCY_NOT_VERIFIED: no se pudo verificar una dependencia.
- HERMES_DEPENDENCY_VERSION_UNPINNED: la dependencia no tiene versión fijada o verificable.
- HERMES_DEPENDENCY_LICENSE_UNKNOWN: no se pudo determinar la licencia de una dependencia cuando era relevante.
- HERMES_DUPLICATE_TECHNIQUE: la técnica propuesta ya existe o colisiona con una técnica registrada.
- HERMES_UNKNOWN_MODULE: la propuesta apunta a un módulo inexistente.
- HERMES_FORBIDDEN_MODULE_CREATION: la propuesta intenta crear un módulo nuevo no autorizado.
- HERMES_DNS_MODULE_FORBIDDEN: la propuesta intenta crear DNS como módulo independiente.
- HERMES_MODULE9_SCOPE_VIOLATION: la propuesta altera el alcance oficial del Módulo 9.
- HERMES_MISTRAL_REVIEW_REQUIRED: la propuesta necesita revisión Mistral/LaIA antes de aprobación.
- HERMES_X5_VALIDATION_REQUIRED: la propuesta necesita validación X5/OjoRouter.
- HERMES_EVIDENCE_CONTRACT_MISSING: falta contrato de evidencia.
- HERMES_PANEL_CONTRACT_MISSING: falta contrato de panel o campos UI.
- HERMES_TESTS_REQUIRED: faltan tests estructurales.
- HERMES_STUB_MARKED_FUNCTIONAL: una lógica IMPLEMENTACION_USUARIO_REQUERIDA fue marcada como funcional.
- HERMES_SCOPE_REQUIRED: falta scope autorizado.
- HERMES_PERMISSION_REQUIRED: falta permiso requerido por la técnica.
- HERMES_MODE_NOT_ALLOWED: el modo actual no permite la acción.
- HERMES_VERSIONLOCK_REQUIRED: la promoción requiere VersionLock.
- HERMES_APPROVAL_RECORD_MISSING: falta registro de aprobación del usuario.
- HERMES_PROMOTION_MANIFEST_INVALID: el promotion_manifest es inválido o incompleto.

## 12. Campos mínimos de promotion_manifest futuro

Cuando se implemente en futuras rondas, todo promotion_manifest deberá incluir como mínimo:

```text
proposal_id
title
description
created_at
created_by
requested_by_user
source_trigger
target_module
technique_id
permission_level
requires_confirmation
requires_user_logic
user_logic_status
can_run_in_demo
can_run_in_dry_run
can_run_in_controlled
can_run_in_expert
files_created
files_modified
dependencies
dependency_verification
evidence_contract
panel_contract
worker_contract
tests_run
test_results
mistral_review_status
x5_validation_status
approval_status
approved_by
approved_at
promotion_status
version_lock_id
rollback_notes
```

Definiciones obligatorias:

- requested_by_user: true si el usuario pidió explícitamente crear, adaptar o incorporar la lógica.
- source_trigger: manual_user_request, cve_detected, missing_parser, missing_wrapper, dependency_request, repeated_failure, service_unknown, evidence_gap, improvement_request.
- requires_user_logic: true si hay IMPLEMENTACION_USUARIO_REQUERIDA o lógica privada pendiente.
- user_logic_status: not_required, required_missing, provided_pending_adaptation, adapted_in_lab, approved_by_user.
- approval_status: not_requested, pending_user, approved, rejected.
- promotion_status: not_promoted, ready_for_review, approved_pending_promotion, promoted, rejected, archived.

## 13. Límites de seguridad operativa

Hermes no puede operar objetivos reales desde laboratorio. Hermes solo puede crear, adaptar y probar estructura en laboratorio.

La ejecución real pertenece a JobRunner y workers autorizados, siempre pasando por X5/OjoRouter, scope, permisos, modo, confirmaciones, kill switch y EvidenceStore.

Hermes puede crear código real solo cuando:

- esté dentro de sandbox/lab;
- no se promocione automáticamente;
- tenga contrato;
- tenga evidence esperada;
- tenga tests estructurales;
- no marque stubs como funcionales;
- quede trazabilidad;
- quede revisión pendiente;
- el usuario tenga la decisión final.

## 14. Regla sobre librerías y dependencias

Hermes debe poder investigar y preparar dependencias, pero con trazabilidad.

Cuando el usuario diga: "Hermes, incorpórame esta librería al módulo tal", Hermes debe:

1. verificar nombre real;
2. verificar paquete;
3. verificar versión;
4. verificar origen;
5. verificar compatibilidad;
6. documentar instalación futura;
7. preparar requirements candidate en laboratorio;
8. no tocar requirements.txt activo sin promoción aprobada;
9. registrar riesgos técnicos;
10. proponer tests estructurales.

Hermes no debe inventar librerías. Si una librería no existe o no se puede verificar, debe bloquear con:

```text
HERMES_DEPENDENCY_NOT_VERIFIED
```

## 15. Referencias de diseño no vinculantes

Este documento sigue las decisiones internas de Ojo de Dios. Como referencias externas de diseño general se tienen en cuenta estos criterios:

- OWASP DevSecOps Guideline: seguridad integrada en el pipeline, detección temprana, SAST, SCA, DAST, IaC scanning, infraestructura y compliance.
- NVD/NIST: repositorio público de datos de vulnerabilidades, CVE enrichment, CVSS, CWE y CPE; NVD no realiza pruebas activas de vulnerabilidad y sus datos pueden cambiar cuando aparece más información.
- OpenSSF Scorecard: evaluación automatizada de riesgos de proyectos open source, dependencias, mantenimiento, testing, binarios, branch protection y supply chain.
- SLSA provenance: trazabilidad de artefactos, origen, builder, parámetros y materiales usados para producir un resultado.

Estas referencias justifican que Hermes tenga trazabilidad, dependencias verificadas, evidence, promotion_manifest, revisión y aprobación humana antes de incorporar capacidades al catálogo activo.

## 16. Criterio de aceptación final

Esta documentación queda aceptada si:

- Hermes queda definido como laboratorio con lápiz controlado.
- Queda claro que Hermes puede programar en laboratorio.
- Queda claro que Hermes puede incorporar lógica si el usuario lo pide.
- Queda claro que incorporar no significa promocionar automáticamente.
- Queda claro que la promoción exige aprobación explícita.
- Quedan separados Chat LaIA/Mistral y Chat Hermes.
- Queda claro que Mistral/LaIA es cerebro operativo.
- Queda claro que Hermes es laboratorio de creación.
- Queda claro que X5/OjoRouter valida y ejecuta.
- Queda claro que CVE detectada solo abre proposal de laboratorio.
- Quedan documentados errores específicos.
- Queda documentado promotion_manifest futuro.
- No se ha tocado app/.
- No se ha creado código ejecutable.
- No se han creado tests bloqueantes.
- No se ha creado módulo 17.
- No se ha creado DNS independiente.
- No se ha alterado Módulo 9.
