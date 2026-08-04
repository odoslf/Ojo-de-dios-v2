# LAIA X5 HERMES CONTROL LOOP — OJO DE DIOS

## Principio

LaIA razona.
DeepSeekAssist investiga solo si LaIA/Mistral no llega.
X5 valida y ejecuta.
Hermes evoluciona en sandbox como manos operativas.
EvidenceStore demuestra.
ScoringEngine aprende.
El usuario gobierna.

Ninguna capa debe suplantar a otra.

## Ciclo operativo

1. Usuario define objetivo autorizado.
2. TargetFingerprint normaliza objetivo.
3. Attack Surface Graph representa superficie si aplica.
4. LaIA interpreta intención y propone plan JSON validado.
5. X5/OjoRouter valida registry, permisos, modo, scope, herramientas, hardware y estados.
6. Si LaIA/Mistral no tiene conocimiento suficiente, prepara consulta mínima y sanitizada a DeepSeekAssist.
7. DeepSeekAssist devuelve JSON corto, validable y cacheable sin ejecutar nada.
8. LaIA/Mistral interpreta la respuesta y X5 vuelve a validar.
9. X5 crea job y selecciona worker.
10. Worker ejecuta solo lo permitido.
11. EvidenceStore guarda salida, errores, bloqueos y artefactos.
12. LaIA analiza evidence.
13. ScoringEngine actualiza eficacia.
14. X5 decide continuar, parar, hacer fallback o pedir mejora.
15. Hermes crea proposal en sandbox si falta una pieza.
16. Mistral revisa proposal.
17. Usuario aprueba o rechaza promoción.

## LaIA no debe

- ejecutar comandos libres;
- inventar técnicas;
- saltarse registry;
- saltarse X5;
- declarar SUCCESS sin evidence;
- ocultar bloqueos;
- ignorar IMPLEMENTACION_USUARIO_REQUERIDA.

## DeepSeekAssist no debe

- sustituir a Mistral/LaIA;
- sustituir a X5/OjoRouter;
- sustituir a Hermes;
- ejecutar comandos;
- instalar herramientas;
- promocionar técnicas;
- decidir producción;
- recibir secretos;
- recibir el repo completo;
- auto-escalar fuera de los modelos configurados sin registro, política y aprobación explícita cuando aplique.

## X5 no debe

- ejecutar técnicas no registradas;
- saltarse permisos;
- saltarse scope;
- ignorar kill switch;
- convertir demo en real;
- marcar stubs como funcionales;
- depender de lógica interna no declarada.

## Hermes no debe

- ejecutar producción;
- autoaprobarse;
- tocar core sin aprobación;
- instalar plugins sin aprobación;
- activar lógica sensible;
- declarar funcionalidad sin evidence;
- ocultar diffs.

## Usuario

El usuario:

- define objetivos autorizados;
- confirma modos sensibles;
- conecta lógica privada en IMPLEMENTACION_USUARIO_REQUERIDA;
- aprueba o rechaza promociones Hermes;
- decide instalación de plugins;
- gobierna cambios de herramientas oficiales.

## Condiciones de parada

El ciclo se detiene si:

- kill switch activo;
- objetivo fuera de scope;
- JSON inválido;
- permiso insuficiente;
- falta herramienta crítica;
- falta hardware;
- falta lógica privada;
- evidence indica stop;
- usuario detiene job;
- límite de intentos alcanzado.

## Resultado válido

Un resultado válido es SUCCESS, FAILED, PARTIAL, MANUAL_REQUIRED, MISSING_TOOL, HARDWARE_REQUIRED, DISABLED_BY_POLICY, DEMO_ONLY o DRY_RUN_ONLY con evidence o registro explícito.

Solo SUCCESS exige evidence contract cumplido.


## Extensión Ronda 0-G — Control loop condicionado por Knowledge Status

El ciclo LaIA→X5→Hermes queda condicionado por Knowledge Bootstrap:

- LaIA solo recomienda planes operativos confiables si Knowledge Base está al menos READY_WITH_REGISTRY.
- X5 consulta knowledge_status, context_pack_status, ai_json_schema_status y hermes_protocol_status.
- Hermes solo crea proposals promocionables si Hermes Agent knowledge está OK y Promotion Pipeline está cargado.
- Si Knowledge Base está STALE/FAILED, X5 degrada a demo/dry_run o pide confirmación.
- EvidenceStore y ScoringEngine siguen siendo la verdad operativa.


## Separación Mano de Dios

Mano de Dios es producto separado y no participa en este ciclo. No debe añadirse como módulo, worker, pipeline, panel, ruta ni dependencia de Ojo de Dios.
