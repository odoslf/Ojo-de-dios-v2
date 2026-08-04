# Agent Interaction Workspaces — Consolas LaIA, Hermes Agent y asistencia contextual

## 1. Decisión oficial

Ojo de Dios debe tener tres formas de interacción con agentes:

1. LaIA Operator Console.
2. Hermes Builder Console.
3. Contextual Agent Drawer.

Estas zonas pueden implementarse en el futuro como pantallas, pestañas, paneles, chats internos, asistente lateral o cajón contextual. Este documento define el contrato conceptual.

La finalidad es que el usuario pueda hablar con el sistema de forma natural sin tener que conocer todos los módulos, técnicas, números internos, workers, schemas o estados.

El usuario debe poder decir cosas como:

- "Analiza esta web autorizada."
- "Haz auditoría completa dentro del scope."
- "Sigue hasta que no queden rutas útiles."
- "Párate si necesitas confirmación."
- "Estoy en esta pantalla, relléname lo que falta."
- "Explícame qué tengo que poner aquí."
- "Prepara este formulario con la mejor configuración segura."
- "Hermes, incorpórame esta librería al módulo web."
- "Hermes, corrige este fallo del repo."
- "Hermes, crea una propuesta para esta CVE."
- "Hermes, adapta esta lógica mía al contrato."
- "Hermes, prepara esto para meterlo al catálogo activo."

El sistema debe traducir esas órdenes a flujos controlados, explicables y aprobables.

## 2. LaIA Operator Console

LaIA Operator Console es la zona donde el usuario habla con LaIA/Mistral para operar sobre objetivos autorizados.

LaIA/Mistral debe actuar como cerebro operativo.

Puede:

- interpretar la petición del usuario;
- normalizar objetivo;
- pedir o revisar scope;
- consultar Attack Surface Graph;
- proponer plan;
- rellenar parámetros;
- explicar técnicas;
- analizar evidence;
- decidir siguiente paso;
- pedir fallback;
- pedir confirmación humana;
- pedir a X5/OjoRouter validación;
- pedir a Hermes una propuesta si falta una pieza;
- redactar resumen e informe.

No puede:

- ejecutar comandos libres;
- saltarse X5/OjoRouter;
- inventar técnicas;
- inventar resultados;
- declarar SUCCESS sin evidence;
- tocar código;
- instalar librerías;
- modificar el catálogo activo;
- promocionar proposals Hermes.

## 3. Hermes Builder Console

Hermes Builder Console es la zona donde el usuario habla con Hermes para construcción, reparación y evolución del sistema.

Hermes debe actuar como constructor controlado.

Puede:

- investigar documentación técnica;
- verificar si una librería existe;
- verificar versión, origen y compatibilidad;
- crear proposal en sandbox;
- crear wrappers;
- crear parsers;
- crear schemas;
- crear panel_fields;
- crear contracts;
- crear tests estructurales;
- crear documentación;
- adaptar lógica entregada por el usuario;
- preparar promotion_manifest;
- preparar diff;
- pedir revisión Mistral/LaIA;
- pedir validación X5/OjoRouter;
- dejar listo para aprobación del usuario.

No puede:

- operar objetivos reales;
- autoaprobarse;
- promocionar sin usuario;
- tocar producción viva;
- ocultar diffs;
- marcar stubs como funcionales;
- saltarse EvidenceStore;
- saltarse VersionLock;
- saltarse permisos;
- instalar dependencias en producción sin aprobación.

## 4. Contextual Agent Drawer

Contextual Agent Drawer es el asistente lateral/contextual disponible desde cualquier pantalla importante.

No sustituye a LaIA Operator Console ni a Hermes Builder Console. Es una puerta rápida para hablar con LaIA o Hermes usando el contexto de la pantalla actual.

Debe poder abrirse desde:

- Nuevo objetivo;
- Dashboard;
- pantalla de target;
- Attack Surface;
- pantalla de técnica;
- formularios de módulo;
- Evidence;
- Scoring;
- Hermes proposals;
- settings permitidos;
- healthcheck;
- pantallas de error o bloqueo.

El usuario no debe tener que copiar manualmente todos los datos de la pantalla al chat. El sistema debe pasar a la IA un contexto estructurado y mínimo.

## 5. Contrato de contexto de pantalla

Cada pantalla que use Contextual Agent Drawer debe poder entregar un contexto estructurado.

Campos conceptuales mínimos:

- screen_id;
- route;
- module_id si aplica;
- target_id si aplica;
- job_id si aplica;
- technique_id si aplica;
- proposal_id si aplica;
- current_mode;
- scope_summary;
- visible_fields;
- missing_fields;
- current_values;
- validation_errors;
- permissions_required;
- evidence_ids;
- blockers;
- allowed_actions;
- dangerous_actions_require_confirmation;
- user_question.

Este contexto no debe incluir secretos crudos, tokens, contraseñas, cookies sensibles ni .env real.

## 6. Page Fill Assist

Page Fill Assist es la función por la que el usuario puede decir en una pantalla:

- "Relléname esta página."
- "Qué pongo aquí."
- "Completa los campos recomendados."
- "Hazme una configuración segura."
- "Prepara esto en modo dry_run."
- "Explícame qué falta antes de continuar."

LaIA/Mistral puede proponer valores para campos si:

- la pantalla declara visible_fields;
- el input_schema existe;
- el panel_fields existe;
- el contexto no requiere secreto no disponible;
- el modo permite la acción;
- X5/OjoRouter puede validar el resultado.

LaIA/Mistral no debe escribir definitivamente ni lanzar ejecución sin que el usuario vea la propuesta y confirme cuando corresponda.

El flujo correcto es:

1. Usuario abre pantalla.
2. Usuario abre Contextual Agent Drawer.
3. Usuario pide ayuda.
4. LaIA recibe screen_context.
5. LaIA propone field_suggestions en JSON.
6. X5/OjoRouter valida si esos campos afectan ejecución.
7. UI muestra propuesta.
8. Usuario acepta, edita o rechaza.
9. Solo tras aceptación se rellenan campos.
10. Si hay ejecución, se pide confirmación según permiso y modo.

## 7. Ejemplos de Page Fill Assist

### Nuevo objetivo

Usuario:

"Estoy creando un objetivo. Relléname lo que falta para auditar esta web en dry_run."

LaIA debe:

1. leer URL/dominio actual;
2. proponer nombre de objetivo;
3. proponer tipo de target;
4. proponer scope inicial;
5. proponer exclusiones si faltan;
6. proponer modo dry_run;
7. explicar qué campos faltan;
8. pedir confirmación antes de crear.

### Pantalla Attack Surface

Usuario:

"Qué hago ahora con estos servicios."

LaIA debe:

1. leer servicios visibles;
2. separar servicios conocidos/desconocidos;
3. mapear técnicas candidatas;
4. marcar bloqueos;
5. proponer siguiente paso;
6. pedir validación X5/OjoRouter.

### Pantalla de técnica

Usuario:

"Relléname esta técnica con lo recomendado."

LaIA debe:

1. leer technique_id;
2. leer input_schema;
3. leer panel_fields;
4. proponer parámetros;
5. marcar campos no inferibles;
6. indicar permisos;
7. indicar evidence esperada;
8. dejar ejecución pendiente de confirmación.

### Pantalla Hermes proposal

Usuario:

"Hermes, corrige esta proposal y prepara el parche."

Hermes debe:

1. leer proposal_id;
2. leer estado;
3. leer errores;
4. detectar si es Sandbox Mode o Authorized Patch Mode;
5. preparar cambios mínimos;
6. dejar diff;
7. pedir revisión si toca;
8. dejar approval pendiente.

## 8. Action Routing

Contextual Agent Drawer debe enrutar la intención del usuario.

Si la intención es operar un objetivo autorizado, va a:

LaIA Operator Console → X5/OjoRouter → JobRunner/Workers → EvidenceStore.

Si la intención es rellenar una pantalla, va a:

LaIA Page Fill Assist → X5/OjoRouter validation si aplica → UI proposal → usuario acepta.

Si la intención es crear/corregir/adaptar sistema, va a:

Hermes Builder Console → Sandbox Mode o Authorized Patch Mode → diff/evidence/review/approval.

Si la intención mezcla operación y construcción, debe separarse:

- LaIA mantiene la operación;
- Hermes prepara lo que falta;
- X5/OjoRouter impide usarlo hasta promoción;
- usuario aprueba.

## 9. Authorized Patch Mode

Authorized Patch Mode es el modo controlado donde Hermes puede preparar correcciones fuera del sandbox normal.

Este modo existe porque el usuario puede necesitar que Hermes no solo proponga una pieza nueva, sino que corrija documentación, contratos, wiring, schemas, paneles, tests estructurales o integración del repo.

Authorized Patch Mode solo se activa por petición explícita del usuario.

Ejemplos:

- "Hermes, corrige este fallo del repo."
- "Hermes, arregla esta documentación."
- "Hermes, ajusta este contrato."
- "Hermes, adapta este wrapper."
- "Hermes, incorpora esta lógica en el punto exacto."
- "Hermes, prepara el parche para meter esto al catálogo activo."

Authorized Patch Mode permite a Hermes preparar cambios en:

- documentación;
- contracts;
- schemas;
- panel definitions;
- wrappers;
- parsers;
- tests estructurales;
- manifests;
- registry entries;
- adapters;
- wiring no sensible;
- promotion manifests.

Authorized Patch Mode no permite:

- tocar producción viva;
- operar objetivos reales;
- instalar dependencias sin aprobación;
- cambiar secretos;
- modificar .env real;
- borrar evidence;
- borrar VersionLock;
- saltarse approvals;
- activar lógica sensible sin aprobación;
- marcar IMPLEMENTACION_USUARIO_REQUERIDA como funcional;
- auto-promocionar.

## 10. Diferencia entre Sandbox Mode y Authorized Patch Mode

### Sandbox Mode

- ruta de laboratorio;
- proposal aislada;
- no toca catálogo activo;
- no toca código productivo;
- sirve para crear y probar estructura.

### Authorized Patch Mode

- se activa solo por orden explícita del usuario;
- puede preparar cambios fuera de sandbox;
- debe producir diff;
- debe producir rollback;
- debe registrar evidence de cambio;
- debe pasar revisión Mistral/LaIA si afecta arquitectura;
- debe pasar validación X5/OjoRouter si afecta registry, técnicas, workers o ejecución;
- requiere aprobación antes de considerarse incorporado.

## 11. Flujo para “corrige el repo”

Cuando el usuario pida a Hermes corregir algo del repo:

1. Hermes clasifica la petición.
2. Hermes detecta si es documentación, contrato, schema, registry, worker, panel, test o lógica privada.
3. Hermes comprueba si puede actuar en Sandbox Mode o Authorized Patch Mode.
4. Hermes prepara cambios mínimos.
5. Hermes no reescribe arquitectura completa.
6. Hermes genera diff.
7. Hermes explica archivos tocados.
8. Hermes indica riesgos.
9. Hermes indica rollback.
10. Hermes ejecuta solo comandos permitidos por la ronda.
11. Hermes deja evidencia de validación.
12. Hermes pide aprobación si el cambio afecta catálogo activo, ejecución, registry, permisos o dependencias.

## 12. Flujo para “prueba todo este objetivo”

Cuando el usuario pida probar un objetivo autorizado:

1. La petición entra por LaIA Operator Console o Contextual Agent Drawer.
2. LaIA interpreta intención.
3. LaIA pide scope/modo si falta.
4. TargetFingerprint normaliza.
5. Attack Surface Graph representa superficie.
6. LaIA genera plan JSON.
7. X5/OjoRouter valida.
8. AutonomousTargetAuditLoop mantiene el ciclo.
9. JobRunner ejecuta jobs permitidos.
10. Workers ejecutan técnicas registradas.
11. EvidenceStore guarda resultados.
12. ScoringEngine prioriza.
13. LaIA analiza evidence.
14. X5 decide siguiente paso.
15. Hermes entra solo si falta una pieza.
16. El usuario aprueba lo sensible.
17. El bucle termina con stop_reason.

## 13. Qué debe ver el usuario

El usuario debe tener mensajes claros, no solo códigos internos.

Ejemplos:

- "Puedo continuar con estas rutas."
- "Necesito confirmación para seguir."
- "Falta herramienta."
- "Falta lógica privada."
- "Esta parte requiere Hermes."
- "Hermes puede preparar una propuesta."
- "No quedan técnicas aplicables."
- "El bucle terminó por límite de tiempo."
- "La evidence no permite declarar éxito."
- "Esto está en dry_run, no es ejecución real."
- "Esto queda pendiente de aprobación."
- "Puedo rellenar estos campos, pero necesitas confirmar antes de ejecutar."
- "No puedo inferir este dato sin que lo escribas tú."

## 14. Estados mínimos de conversación

LaIA Operator Console debe poder mostrar:

- ID del objetivo;
- scope;
- modo;
- plan actual;
- técnica actual;
- evidence reciente;
- siguiente paso;
- bloqueos;
- stop_reason;
- confirmaciones pendientes.

Hermes Builder Console debe poder mostrar:

- proposal_id;
- modo: sandbox o authorized_patch;
- archivos propuestos;
- diff;
- tests estructurales;
- evidence;
- revisión Mistral/LaIA;
- validación X5/OjoRouter;
- approval_status;
- rollback.

Contextual Agent Drawer debe poder mostrar:

- pantalla actual;
- campos visibles;
- campos faltantes;
- errores de validación;
- acciones permitidas;
- sugerencias de LaIA;
- propuesta de relleno;
- bloqueo si falta permiso;
- botón aceptar;
- botón editar;
- botón rechazar;
- botón pedir a Hermes.

## 15. Reglas de seguridad y aprobación

Contextual Agent Drawer puede sugerir y preparar, pero no debe ejecutar acciones sensibles sin confirmación.

Reglas:

- rellenar campos no equivale a ejecutar;
- sugerir parámetros no equivale a aprobar;
- crear una proposal Hermes no equivale a promocionar;
- aceptar valores de un formulario no elimina validación X5/OjoRouter;
- si hay secreto, el usuario lo introduce localmente y no se envía a IA externa;
- si falta permiso, se muestra bloqueo claro;
- si falta lógica privada, se muestra IMPLEMENTACION_USUARIO_REQUERIDA;
- si falta herramienta, se muestra MISSING_TOOL;
- si falta hardware, se muestra HARDWARE_REQUIRED;
- si la acción requiere modo superior, se pide confirmación y validación.

## 16. Frase oficial

LaIA Operator Console es donde el usuario pide qué quiere lograr sobre un objetivo autorizado. Hermes Builder Console es donde el usuario pide qué quiere crear, corregir o incorporar al sistema. Contextual Agent Drawer es el asistente lateral que entiende la pantalla actual y ayuda a rellenar, explicar, continuar o derivar a Hermes sin que el usuario tenga que conocer campos internos. LaIA piensa, X5 valida, JobRunner ejecuta, EvidenceStore prueba, ScoringEngine prioriza, Hermes construye o corrige bajo control, y el usuario gobierna.

## 17. Criterio de aceptación

El documento queda aceptado si:

- define LaIA Operator Console;
- define Hermes Builder Console;
- define Contextual Agent Drawer;
- define Page Fill Assist;
- define screen_context mínimo;
- explica qué pide el usuario en cada zona;
- deja claro que LaIA opera objetivos autorizados;
- deja claro que Hermes construye/corrige sistema;
- deja claro que la ayuda contextual puede rellenar páginas con aprobación;
- define Authorized Patch Mode;
- diferencia Sandbox Mode y Authorized Patch Mode;
- permite que Hermes corrija fuera de sandbox solo bajo orden explícita;
- impide que Hermes toque producción viva;
- impide autoaprobación;
- impide ejecución real desde Hermes;
- conecta “prueba todo este objetivo” con AutonomousTargetAuditLoop;
- mantiene X5/OjoRouter como validador;
- mantiene EvidenceStore como verdad;
- mantiene ScoringEngine como priorización;
- mantiene el usuario como aprobador final;
- no crea código;
- no crea tests;
- no toca app/;
- no crea módulo nuevo;
- no cambia Módulo 9;
- no crea DNS independiente.
