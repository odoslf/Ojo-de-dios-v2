# AutonomousTargetAuditLoop — Bucle autónomo controlado de objetivo

## 1. Decisión oficial

AutonomousTargetAuditLoop es la capa transversal que mantiene una auditoría continua, asistida o autónoma controlada sobre un objetivo autorizado dentro de Ojo de Dios.

No es un módulo nuevo.

AutonomousTargetAuditLoop pertenece funcionalmente al Módulo 12 Orquestación X5 + IA + Hermes Agent Lab y se apoya en el Módulo 16 Ops / Evidence / Calidad / Mantenimiento para evidence, scoring, estado, stop reasons, healthcheck, auditoría y trazabilidad.

Su función es convertir una orden del usuario como "analiza esta web autorizada entera", "revisa todas las rutas permitidas" o "sigue hasta agotar opciones útiles" en un ciclo controlado:

objetivo autorizado → fingerprint → attack surface → plan LaIA → validación X5 → job → worker → evidence → análisis LaIA → scoring → siguiente paso → parada, fallback o propuesta Hermes.

AutonomousTargetAuditLoop no ejecuta por sí mismo técnicas. No sustituye a LaIA/Mistral, X5/OjoRouter, JobRunner, Workers, EvidenceStore, ScoringEngine ni Hermes.

AutonomousTargetAuditLoop mantiene el ciclo. X5/OjoRouter valida. JobRunner ejecuta. Workers hacen el trabajo real permitido. EvidenceStore demuestra. LaIA/Mistral razona. ScoringEngine prioriza. Hermes crea lo que falta en laboratorio. El usuario gobierna.

## 2. Qué problema resuelve

Ojo de Dios necesita una capa explícita para el caso de uso donde el usuario no quiere elegir técnica por técnica, sino dar un objetivo autorizado y pedir que el sistema avance de forma inteligente, controlada y trazable hasta que no queden rutas útiles o hasta que se alcance una condición de parada.

AutonomousTargetAuditLoop define:

- quién decide el siguiente paso;
- quién valida;
- quién ejecuta;
- cuándo se guarda evidence;
- cuándo se actualiza scoring;
- cuándo entra Hermes;
- cuándo se pide aprobación al usuario;
- cuándo se para;
- cómo se evita repetir acciones inútiles;
- cómo se evita fingir éxito;
- cómo se evita que una propuesta Hermes se trate como capacidad disponible antes de promoción.

## 3. Ubicación arquitectónica

AutonomousTargetAuditLoop se ubica en:

Módulo 12 — Orquestación X5 + IA + Hermes Agent Lab

Se apoya en:

Módulo 16 — Excelencia operativa / Evidence / Calidad / Mantenimiento

No debe aparecer como:

- Módulo 17;
- módulo DNS;
- módulo de ejecución independiente;
- módulo Hermes independiente;
- sustituto de JobRunner;
- sustituto de X5/OjoRouter;
- sustituto de LaIA/Mistral;
- sustituto de Attack Surface Graph.

## 4. Responsabilidad exacta

AutonomousTargetAuditLoop debe:

1. recibir un target_id autorizado;
2. recibir modo de ejecución;
3. recibir scope;
4. recibir límites;
5. consultar TargetFingerprint;
6. consultar Attack Surface Graph;
7. pedir a LaIA/Mistral un plan JSON validado;
8. entregar el plan a X5/OjoRouter;
9. aceptar solo acciones validadas por X5/OjoRouter;
10. crear jobs mediante JobRunner;
11. esperar evidence;
12. pasar evidence a LaIA/Mistral para análisis;
13. actualizar o pedir actualización de ScoringEngine;
14. pedir a X5/OjoRouter siguiente paso;
15. evitar repeticiones inútiles;
16. controlar condiciones de parada;
17. pedir confirmación humana cuando toque;
18. derivar a Hermes cuando falte una pieza;
19. registrar stop_reason;
20. dejar trazabilidad completa.

AutonomousTargetAuditLoop no debe:

- ejecutar comandos libres;
- ejecutar técnicas no registradas;
- saltarse scope;
- saltarse permisos;
- saltarse modo;
- saltarse Kill Switch;
- convertir demo en real;
- convertir dry_run en ejecución real;
- marcar MANUAL_REQUIRED como SUCCESS;
- marcar IMPLEMENTACION_USUARIO_REQUERIDA como funcional;
- ejecutar proposals Hermes no promocionadas;
- tocar production desde Hermes;
- instalar herramientas;
- inventar evidence;
- ignorar ToolHealth;
- ignorar VersionLock;
- ignorar Knowledge Status;
- repetir infinitamente sin límite.

## 5. Flujo principal

El flujo principal es:

1. Usuario crea objetivo en /targets/new.
2. Usuario define dominio, IP, rango, URL, API, cloud, Android, RF u otro objetivo soportado.
3. Usuario define o confirma scope.
4. Usuario define modo: demo, dry_run, controlled o expert.
5. TargetFingerprint normaliza objetivo.
6. Attack Surface Graph crea o actualiza superficie.
7. LaIA/Mistral interpreta intención.
8. LaIA/Mistral propone plan JSON validado.
9. X5/OjoRouter valida registry, permisos, modo, scope, allowlist, ToolHealth, VersionLock, Knowledge Status, confirmaciones, lógica privada, hardware y evidence contract.
10. AutonomousTargetAuditLoop selecciona el siguiente job autorizado.
11. JobRunner crea ejecución.
12. Worker asignado ejecuta solo lo permitido.
13. EvidenceStore guarda resultado, errores, bloqueos y artefactos.
14. Attack Surface Graph se actualiza si aparece nueva superficie.
15. ScoringEngine actualiza eficacia.
16. LaIA/Mistral analiza evidence.
17. X5/OjoRouter decide continuar, parar, pedir confirmación, pedir datos, hacer fallback o pedir proposal Hermes.
18. AutonomousTargetAuditLoop repite el ciclo si procede.
19. El bucle termina con stop_reason explícito.

## 6. Entrada del usuario

El usuario debe poder expresarse de forma natural.

Ejemplos:

- "Analiza esta web autorizada."
- "Revisa este servidor dentro del scope."
- "Haz auditoría completa del dominio."
- "Sigue hasta que no queden rutas útiles."
- "Modo asistido."
- "Modo controlled con confirmación."
- "Solo dry_run."
- "No hagas nada fuera del scope."
- "Usa credenciales autorizadas guardadas en el perfil."
- "Excluye este subdominio."
- "Para si hay impacto alto."
- "Pide permiso antes de cualquier acción sensible."

LaIA/Mistral debe convertir esa intención en JSON validado.

AutonomousTargetAuditLoop nunca debe interpretar texto libre por su cuenta sin pasar por LaIA/Mistral y X5/OjoRouter.

## 7. Plan LaIA conceptual

El plan de LaIA/Mistral para el bucle debe ser estructurado y validable.

Campos conceptuales mínimos:

- goal;
- target_id;
- mode;
- scope;
- strategy;
- recommended_paths;
- selected_techniques;
- missing_parameters;
- stop_conditions;
- success_conditions;
- requires_user_confirmation.

La implementación real futura deberá usar schemas del sistema.

Si el JSON no valida, X5/OjoRouter no ejecuta.

## 8. Policy y permisos

AutonomousTargetAuditLoop debe respetar siempre:

- permission_level;
- requires_confirmation;
- requires_allowlisted_target;
- requires_hardware;
- requires_network;
- requires_user_logic;
- can_run_in_demo;
- can_run_in_dry_run;
- can_run_in_controlled;
- modo expert solo si el usuario lo activa;
- Kill Switch;
- ToolHealth;
- VersionLock;
- Knowledge Status;
- EvidenceStore.

El bucle no puede elevar modo por sí solo.

El bucle no puede pasar de dry_run a controlled.

El bucle no puede pasar de controlled a expert.

El bucle no puede usar credenciales, hardware, cloud mutation, RF transmit, persistencia o acciones sensibles sin los permisos y confirmaciones correspondientes.

## 9. Modos de operación del bucle

### demo

Modo para probar interfaz, flujos, fixtures y evidence demo.

No cuenta como ejecución real.

### dry_run

Modo por defecto para nuevos objetivos.

Permite planificar, validar, simular, preparar parámetros, comprobar contratos y mostrar qué se haría.

No debe ejecutar acciones reales que excedan dry_run.

### controlled

Modo con ejecución controlada permitida por usuario, scope, permisos y confirmaciones.

Solo ejecuta técnicas registradas, disponibles, con ToolHealth/VersionLock válidos y evidence contract.

### expert

Modo avanzado activado por usuario administrador.

No elimina controles. Solo permite mayor profundidad o intensidad si registry, permisos, scope, X5/OjoRouter, Kill Switch y confirmaciones lo permiten.

## 10. StopPolicy

AutonomousTargetAuditLoop debe parar si ocurre cualquiera de estas condiciones:

- Kill Switch activo;
- usuario pulsa stop;
- objetivo fuera de scope;
- allowlist no valida;
- JSON LaIA inválido;
- X5/OjoRouter rechaza plan;
- permiso insuficiente;
- modo no permite la acción;
- falta confirmación humana;
- falta herramienta crítica;
- ToolHealth indica MISSING_REQUIRED o FAILED;
- falta hardware;
- falta lógica privada;
- técnica devuelve MANUAL_REQUIRED;
- evidence indica stop;
- evidence contract no se cumple;
- demasiados errores consecutivos;
- límite de intentos alcanzado;
- límite de tiempo alcanzado;
- límite de jobs alcanzado;
- límite de intensidad alcanzado;
- no quedan técnicas candidatas;
- no aparece superficie nueva;
- scoring indica baja utilidad repetida;
- Hermes proposal requerida;
- Knowledge Base está STALE/FAILED y el modo no permite continuar;
- VersionLock requerido no existe;
- hay contradicción entre fuentes de conocimiento;
- el sistema solo puede seguir con acción sensible no aprobada.

Cada parada debe registrar stop_reason.

## 11. Stop reasons oficiales

Lista inicial de stop_reason para esta capa:

- USER_STOPPED
- KILL_SWITCH_ACTIVE
- OUT_OF_SCOPE
- ALLOWLIST_REQUIRED
- INVALID_LAIA_JSON
- X5_PLAN_REJECTED
- PERMISSION_DENIED
- MODE_NOT_ALLOWED
- CONFIRMATION_REQUIRED
- MISSING_REQUIRED_TOOL
- TOOL_HEALTH_FAILED
- HARDWARE_REQUIRED
- USER_LOGIC_REQUIRED
- MANUAL_REQUIRED
- EVIDENCE_CONTRACT_FAILED
- EVIDENCE_REQUESTED_STOP
- MAX_ITERATIONS_REACHED
- MAX_RUNTIME_REACHED
- MAX_JOBS_REACHED
- MAX_ERRORS_REACHED
- MAX_INTENSITY_REACHED
- NO_APPLICABLE_TECHNIQUES
- NO_NEW_SURFACE
- LOW_EXPECTED_UTILITY
- HERMES_PROPOSAL_REQUIRED
- HERMES_PROMOTION_REQUIRED
- KNOWLEDGE_STALE
- KNOWLEDGE_FAILED
- VERSIONLOCK_REQUIRED
- SOURCE_CONTRADICTION
- WAITING_FOR_USER_INPUT
- COMPLETED_WITH_EVIDENCE
- COMPLETED_DRY_RUN
- COMPLETED_DEMO

Los stop_reason son estados operativos, no juicios externos.

## 12. Iteration model

Cada vuelta del bucle debe tener un registro conceptual:

- loop_id;
- target_id;
- iteration_number;
- mode;
- selected_path;
- selected_module;
- selected_technique;
- x5_decision;
- job_id;
- evidence_ids;
- scoring_before;
- scoring_after;
- laia_summary;
- next_recommendation;
- stop_reason;
- created_at;
- finished_at.

Esto documenta el modelo futuro. Este documento no crea tablas ni modelos.

## 13. Relación con Attack Surface Graph

AutonomousTargetAuditLoop debe usar Attack Surface Graph como memoria técnica del objetivo.

Attack Surface Graph ayuda a saber:

- qué hosts existen;
- qué puertos existen;
- qué servicios existen;
- qué productos/versiones existen;
- qué CPE/CVE candidatas existen;
- qué técnicas candidatas existen;
- qué evidence existe;
- qué rutas ya se probaron;
- qué rutas quedan pendientes;
- qué rutas requieren permiso;
- qué rutas requieren lógica privada;
- qué rutas necesitan Hermes.

El bucle debe evitar repetir la misma ruta sin nueva evidencia o cambio de contexto.

## 14. Relación con LaIA/Mistral

LaIA/Mistral es el cerebro operativo.

LaIA/Mistral debe:

- interpretar la petición del usuario;
- convertir intención natural a JSON;
- explicar qué hará el bucle;
- analizar evidence;
- proponer siguiente paso;
- detectar fallback;
- detectar necesidad de Hermes;
- redactar resumen de progreso;
- avisar bloqueos;
- no inventar éxito;
- no ejecutar comandos libres;
- no saltarse X5/OjoRouter.

LaIA/Mistral no mantiene por sí sola el bucle. El bucle la consulta en cada iteración.

## 15. Relación con X5/OjoRouter

X5/OjoRouter es el validador y motor de decisión.

X5/OjoRouter debe:

- cargar registry;
- validar técnica;
- validar permisos;
- validar modo;
- validar scope;
- validar ToolHealth;
- validar VersionLock;
- validar evidence contract;
- decidir si se puede crear job;
- decidir fallback;
- decidir si debe entrar Hermes;
- bloquear lo no permitido.

AutonomousTargetAuditLoop no puede ejecutar nada que X5/OjoRouter rechace.

## 16. Relación con JobRunner y Workers

JobRunner ejecuta jobs aprobados.

Workers ejecutan acciones concretas por módulo.

AutonomousTargetAuditLoop solo coordina el ciclo. No debe contener lógica interna de técnicas.

Cada worker debe devolver estados honestos:

- SUCCESS;
- FAILED;
- PARTIAL;
- MANUAL_REQUIRED;
- MISSING_TOOL;
- HARDWARE_REQUIRED;
- DISABLED_BY_POLICY;
- DEMO_ONLY;
- DRY_RUN_ONLY.

SUCCESS solo es válido con evidence contract cumplido.

## 17. Relación con EvidenceStore

EvidenceStore es la verdad operativa.

Cada iteración debe guardar evidence o bloqueo explícito.

El bucle debe registrar:

- job_id;
- run_id;
- target_id;
- module_id;
- technique_id;
- status real;
- mode;
- permissions snapshot;
- summary;
- timestamps;
- files;
- hashes;
- normalized_output_json;
- errors;
- stop_reason;
- manual_required si aplica.

No hay éxito sin evidence.

## 18. Relación con ScoringEngine

ScoringEngine ayuda a priorizar.

El bucle puede usar scoring para:

- priorizar técnicas con mejor historial;
- bajar prioridad a técnicas con fallos repetidos;
- detectar baja utilidad;
- decidir fallback;
- evitar repeticiones;
- proponer Hermes si hay error estructural repetido.

ScoringEngine no debe fingir aprendizaje.

Demo no cuenta como ejecución real.

SUCCESS vacío no sube score.

PARTIAL solo mejora score si hay evidence útil.

MANUAL_REQUIRED no debe penalizar como fallo operativo.

## 19. Relación con Hermes

Hermes entra cuando falta una pieza.

Ejemplos:

- falta parser;
- falta wrapper;
- falta librería;
- falta panel field;
- falta evidence schema;
- falta normalizador;
- falta técnica registrada;
- falta mapeo CVE;
- servicio desconocido;
- CVE nueva;
- salida no parseada;
- error repetido;
- lógica privada pendiente;
- propuesta de mejora solicitada por usuario.

El bucle no debe esperar que Hermes resuelva en producción.

Flujo correcto:

1. AutonomousTargetAuditLoop detecta bloqueo.
2. X5/OjoRouter clasifica que falta pieza.
3. Hermes crea proposal en sandbox.
4. Hermes deja estado review_required.
5. Mistral/LaIA revisa.
6. Usuario aprueba o rechaza.
7. Promotion Pipeline promociona si procede.
8. VersionLock registra.
9. Registry reload.
10. Knowledge Refresh.
11. El bucle futuro podrá usar la nueva pieza.

Una proposal Hermes no desbloquea una ejecución actual hasta que esté promoted y validada.

## 20. Relación con Knowledge Bootstrap

AutonomousTargetAuditLoop depende del estado de conocimiento.

Antes de operar de forma fiable, debe existir Knowledge Bootstrap mínimo:

- docs principales indexados;
- registry indexado;
- permisos indexados;
- JSON schemas validados;
- ToolHealth disponible;
- VersionLock disponible;
- EvidenceStore disponible;
- ScoringEngine disponible;
- Hermes protocol cargado;
- context packs disponibles.

Si Knowledge Base está STALE o FAILED:

- en demo puede explicar;
- en dry_run puede degradar y avisar;
- en controlled/expert debe bloquear o pedir confirmación explícita según X5/OjoRouter.

## 21. UI esperada futura

La UI debe permitir entender y gobernar el bucle.

En la pantalla del target o Attack Surface debe mostrarse:

- estado del bucle;
- modo actual;
- scope activo;
- iteración actual;
- técnicas ya revisadas;
- técnicas pendientes;
- técnicas bloqueadas;
- motivo de bloqueo;
- evidence reciente;
- scoring reciente;
- recomendación LaIA;
- decisión X5;
- botón continuar;
- botón pausar;
- botón detener;
- botón pedir propuesta Hermes;
- botón aprobar/rechazar cuando corresponda;
- botón cambiar límites;
- stop_reason final.

El usuario no debe tener que entender todos los números internos. La UI debe traducir el estado a mensajes claros.

## 22. Límites configurables

El bucle debe tener límites configurables futuros:

- max_iterations;
- max_runtime_minutes;
- max_jobs;
- max_errors;
- max_consecutive_failures;
- max_retries_per_technique;
- max_same_surface_retries;
- max_intensity;
- allowed_modules;
- excluded_modules;
- excluded_techniques;
- require_confirmation_for_sensitive;
- pause_on_manual_required;
- pause_on_hermes_required;
- pause_on_cve_candidate;
- pause_on_high_impact;
- dry_run_only;
- evidence_required_for_continue.

Este documento solo documenta límites. No crea settings.

## 23. Estados del bucle

Estados conceptuales:

- NOT_STARTED
- INITIALIZING
- WAITING_FOR_SCOPE
- WAITING_FOR_CONFIRMATION
- PLANNING
- X5_VALIDATING
- READY_TO_RUN
- RUNNING_JOB
- WAITING_FOR_EVIDENCE
- ANALYZING_EVIDENCE
- UPDATING_GRAPH
- UPDATING_SCORING
- SELECTING_NEXT_STEP
- WAITING_FOR_HERMES
- WAITING_FOR_USER_INPUT
- PAUSED
- STOPPING
- STOPPED
- COMPLETED
- FAILED
- DEGRADED_DEMO_ONLY
- DEGRADED_DRY_RUN_ONLY

## 24. Errores específicos

Errores específicos de AutonomousTargetAuditLoop:

- TARGET_LOOP_NOT_FOUND
- TARGET_LOOP_ALREADY_RUNNING
- TARGET_LOOP_NOT_RUNNING
- TARGET_LOOP_INVALID_STATE
- TARGET_LOOP_SCOPE_REQUIRED
- TARGET_LOOP_MODE_REQUIRED
- TARGET_LOOP_LIMITS_REQUIRED
- TARGET_LOOP_INVALID_LAIA_JSON
- TARGET_LOOP_X5_REJECTED_PLAN
- TARGET_LOOP_JOB_CREATION_FAILED
- TARGET_LOOP_EVIDENCE_MISSING
- TARGET_LOOP_EVIDENCE_CONTRACT_FAILED
- TARGET_LOOP_SCORING_FAILED
- TARGET_LOOP_GRAPH_UPDATE_FAILED
- TARGET_LOOP_NO_APPLICABLE_TECHNIQUES
- TARGET_LOOP_NO_NEW_SURFACE
- TARGET_LOOP_PERMISSION_DENIED
- TARGET_LOOP_CONFIRMATION_REQUIRED
- TARGET_LOOP_KILL_SWITCH_ACTIVE
- TARGET_LOOP_TOOL_HEALTH_FAILED
- TARGET_LOOP_VERSIONLOCK_REQUIRED
- TARGET_LOOP_USER_LOGIC_REQUIRED
- TARGET_LOOP_HERMES_REQUIRED
- TARGET_LOOP_HERMES_PROMOTION_REQUIRED
- TARGET_LOOP_KNOWLEDGE_NOT_READY
- TARGET_LOOP_MAX_ITERATIONS_REACHED
- TARGET_LOOP_MAX_RUNTIME_REACHED
- TARGET_LOOP_MAX_ERRORS_REACHED

Los errores deben ser accionables y mostrarse en UI con explicación.

## 25. Qué significa "revisar todo"

"Revisar todo" nunca significa ejecutar sin límites.

En Ojo de Dios significa:

- revisar todas las rutas aplicables;
- dentro del scope;
- con modo permitido;
- con permisos correctos;
- con confirmaciones cuando toque;
- con ToolHealth válido;
- con VersionLock si aplica;
- con evidence obligatoria;
- con Kill Switch activo;
- sin inventar resultados;
- sin usar proposals Hermes no promocionadas;
- sin saltarse IMPLEMENTACION_USUARIO_REQUERIDA;
- sin repetir inútilmente;
- hasta llegar a stop_reason honesto.

El sistema debe poder explicar al usuario qué queda por hacer y por qué no puede continuar si hay bloqueo.

## 26. Frase oficial

AutonomousTargetAuditLoop mantiene el ciclo. LaIA/Mistral piensa. X5/OjoRouter valida. JobRunner ejecuta. Workers trabajan. EvidenceStore prueba. ScoringEngine prioriza. Attack Surface Graph recuerda. Hermes crea lo que falta en laboratorio. El usuario gobierna.

## 27. Criterio de aceptación documental

Este documento queda aceptado si:

- define AutonomousTargetAuditLoop;
- deja claro que no es módulo 17;
- lo ubica en Módulo 12;
- lo conecta con Módulo 16;
- respeta LaIA/Mistral como cerebro operativo;
- respeta X5/OjoRouter como validador;
- respeta JobRunner/Workers como ejecución;
- respeta EvidenceStore como verdad;
- respeta ScoringEngine como priorización;
- respeta Hermes como laboratorio;
- respeta Knowledge Bootstrap;
- define StopPolicy;
- define stop_reason;
- define estados;
- define errores específicos;
- define UI futura;
- define límites configurables;
- aclara qué significa revisar todo;
- no crea código;
- no crea tests;
- no toca app/;
- no cambia módulos oficiales;
- no cambia Módulo 9;
- no crea DNS independiente.
