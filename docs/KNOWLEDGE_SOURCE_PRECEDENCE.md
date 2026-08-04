# KNOWLEDGE SOURCE PRECEDENCE — OJO DE DIOS

## Propósito

Evitar que LaIA, Hermes, Codex u otros asistentes mezclen documentación antigua, planes futuros, runtime real y propuestas no aprobadas.

Este documento define qué fuente manda cuando hay contradicciones.

## Orden de autoridad

1. ARCHITECTURE_LOCK_OJO_DE_DIOS.md
2. MASTER_PLAN_OJO_DE_DIOS.md
3. AI_HANDOFF_OJO_DE_DIOS.md
4. docs/AUTHORIZED_OFFENSIVE_DOCTRINE.md
5. docs/DEEPSEEK_ASSIST_EXTERNAL_BRAIN.md
6. docs/HERMES_DEEPSEEK_EVOLUTION_PIPELINE.md
7. docs/MANO_DE_DIOS_SEPARATION.md
8. Registry real generado
9. Contratos Python reales
10. VersionLock real
11. ToolHealth real
12. EvidenceStore real
13. ScoringEngine real
14. Hermes promoted aprobado
15. Hermes proposals no promocionadas
16. docs/tools/
17. documentación de módulos
18. documentación externa oficial
19. memoria antigua de chat
20. suposición del modelo

## Regla crítica

Si una fuente inferior contradice una fuente superior, gana la fuente superior.

Ningún asistente puede usar memoria antigua, planes aspiracionales o documentación externa para superar architecture lock, master plan, handoff, registry, contratos, permisos, evidence o approvals.

## Diferencia entre documentación y runtime

Una técnica documentada no es funcional hasta que:

- existe archivo real;
- existe clase real;
- está en registry;
- tiene worker o demo/dry_run definido;
- tiene evidence contract;
- tiene estado correcto;
- no está marcada como IMPLEMENTACION_USUARIO_REQUERIDA salvo que sea solo chasis;
- ha pasado validación;
- X5 puede verla.

Si cualquiera de esos puntos falta, LaIA debe describirla como documentación, propuesta, chasis o pendiente, no como capacidad funcional.

## Propuestas Hermes

Una propuesta Hermes:

- no es producción;
- no es técnica funcional;
- no modifica registry productivo;
- no ejecuta;
- no se indexa como funcional.

Solo Hermes promoted + approval + VersionLock + registry reload puede considerarse disponible.

## Fuentes externas

Fuentes externas como NVD, CVE.org, CISA KEV, FIRST EPSS, OSV, Kali, ProjectDiscovery, MITRE ATT&CK o documentación de herramientas son conocimiento auxiliar.

No mandan por encima de:

- scope;
- permisos;
- registry;
- X5;
- EvidenceStore;
- estado IMPLEMENTACION_USUARIO_REQUERIDA;
- aprobación del usuario.

Las fuentes externas pueden justificar documentación, propuestas Hermes o priorización, pero no prueban ejecución ni explotación.

## Regla para LaIA

LaIA debe indicar source_paths y confidence en respuestas operativas.

Si no hay fuente suficiente, debe devolver MISSING_DOC o UNKNOWN.

LaIA debe diferenciar al menos:

- documented;
- registered;
- available;
- executable_by_policy;
- confirmed_by_evidence;
- unknown.

## Regla para Hermes

Hermes puede usar fuentes externas para crear una propuesta, pero debe guardar:

- fuente;
- fecha;
- resumen;
- impacto;
- archivos generados;
- evidence demo;
- límites;
- estado;
- si requiere IMPLEMENTACION_USUARIO_REQUERIDA.

Hermes no puede autoaprobar la propuesta ni indexarla como funcional antes de promoción controlada.

## Regla para colaboradores y agentes

Antes de modificar arquitectura o documentación estratégica, un agente debe revisar este documento y resolver contradicciones contra el orden de autoridad. Si una ronda pide algo que contradice una fuente superior, debe señalar la contradicción y no inventar una solución funcional.


## DeepSeekAssist como fuente externa

DeepSeekAssist es fuente externa auxiliar y opcional. No manda por encima de Mistral/LaIA, X5/OjoRouter, scope, permisos, EvidenceStore, VersionLock, ToolHealth, registry ni aprobación del usuario.

Su salida debe tratarse como JSON de investigación validable, cacheable y de mínimo coste. No prueba ejecución, explotación ni disponibilidad funcional por sí misma.

## Doctrina ofensiva autorizada

La doctrina ofensiva autorizada fija que no se bloquean técnicas por nombres, categorías o palabras. Si existe contradicción entre un test moralizante y la doctrina, manda la doctrina: el control correcto es scope, allowlist, permisos, execution_mode, evidence, kill switch, VersionLock, ToolHealth, audit log y aprobación del usuario.

## Separación Mano de Dios

Mano de Dios es producto separado. Ninguna memoria antigua, propuesta o fuente externa puede usar Ojo de Dios para integrar Mano de Dios sin una ronda futura explícita del usuario.
