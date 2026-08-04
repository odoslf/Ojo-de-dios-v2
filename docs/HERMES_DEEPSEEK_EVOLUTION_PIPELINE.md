HERMES + DEEPSEEK EVOLUTION PIPELINE — OJO DE DIOS

Principio

Hermes es el agente constructor de Ojo de Dios.

Hermes no es el cerebro principal.
Hermes no decide producción.
Hermes no ejecuta ofensiva real por sí solo.
Hermes no instala herramientas fuera del flujo aprobado.
Hermes no salta X5/OjoRouter.

Hermes son las manos operativas que preparan en laboratorio lo que falta para que Ojo de Dios evolucione de forma controlada.

DeepSeekAssist es un cerebro externo opcional y barato que solo ayuda cuando Mistral/LaIA no llega.

La relación oficial es:

- Mistral/LaIA piensa, interpreta y decide si necesita ayuda externa;
- DeepSeekAssist investiga con contexto mínimo y coste mínimo;
- Hermes construye wrappers, parsers, schemas, paneles, proposals e integraciones en laboratorio;
- X5/OjoRouter valida scope, permisos, modo, evidence, riesgo y registry;
- el usuario aprueba cualquier promoción a producción.

Alcance de esta ronda

Esta ronda no implementa Hermes.
Esta ronda no implementa DeepSeekAssist.
Esta ronda no crea conectores.
Esta ronda no crea clientes API.
Esta ronda no crea wrappers.
Esta ronda no crea parsers.
Esta ronda no crea schemas funcionales.
Esta ronda no crea paneles.
Esta ronda no instala herramientas.
Esta ronda no ejecuta lógica ofensiva.

Esta ronda solo fija la norma para rondas futuras.

Flujo oficial futuro

1. El usuario define un objetivo autorizado.
2. Mistral/LaIA interpreta la intención y consulta conocimiento local.
3. X5/OjoRouter valida scope, allowlist, permisos, modo y kill switch.
4. Si la capacidad ya existe, X5 sigue el flujo normal.
5. Si falta conocimiento moderno, Mistral/LaIA puede pedir consulta mínima a DeepSeekAssist.
6. DeepSeekAssist devuelve JSON corto, validable y cacheable.
7. Mistral/LaIA revisa la respuesta y decide si hace falta construcción.
8. Hermes genera una proposal en laboratorio.
9. Hermes puede preparar chasis documental/técnico controlado:
   - wrapper;
   - parser;
   - schema;
   - panel;
   - contrato de evidencia;
   - mapping de registry;
   - instrucciones de instalación controlada;
   - informe de credibilidad;
   - tests estructurales futuros;
   - marca IMPLEMENTACION_USUARIO_REQUERIDA si aplica.
10. X5/OjoRouter valida la proposal.
11. Mistral revisa coherencia técnica y límites.
12. El usuario aprueba o rechaza promoción.
13. Solo Promotion Pipeline, VersionLock, ToolHealth, registry reload y audit log convierten algo en capacidad disponible.

Qué puede construir Hermes en laboratorio

Hermes puede preparar, siempre en laboratorio y sin promoción automática:

- wrappers para herramientas autorizadas;
- parsers de salida;
- schemas JSON;
- contratos de entrada;
- contratos de evidencia;
- panel_fields;
- propuestas de registry;
- documentación operativa;
- playbooks de uso controlado;
- integración con EvidenceStore;
- integración con ToolHealth;
- integración con VersionLock;
- fixtures y pruebas estructurales futuras;
- informes de compatibilidad;
- propuestas de migración;
- propuestas de rollback;
- clasificación de permisos;
- marcas de requires_confirmation;
- marcas de IMPLEMENTACION_USUARIO_REQUERIDA.

Qué no puede hacer Hermes

Hermes no puede:

- promocionar producción por sí mismo;
- ejecutar fuera de scope;
- saltarse allowlist;
- saltarse X5/OjoRouter;
- saltarse kill switch;
- saltarse aprobación del usuario;
- instalar dependencias sin flujo aprobado;
- descargar herramientas por iniciativa propia;
- guardar secretos;
- enviar secretos a DeepSeekAssist;
- convertir documentación aspiracional en funcionalidad real;
- marcar una CVE como explotable sin evidencia;
- ocultar IMPLEMENTACION_USUARIO_REQUERIDA;
- rebajar una técnica ofensiva a check pasivo si la técnica oficial requiere capacidad ofensiva.

Entrada permitida desde DeepSeekAssist

DeepSeekAssist solo puede entregar a Hermes datos mínimos, sanitizados y validados, por ejemplo:

- resumen técnico;
- productos afectados;
- versiones afectadas;
- advisories relevantes;
- señales de explotación pública;
- prerequisitos;
- comandos o formatos documentales de herramientas, si son públicos y necesarios;
- propuesta de campos para parser;
- propuesta de evidence_contract;
- unknowns;
- riesgos;
- next_steps;
- confidence;
- coste estimado;
- cache_key.

DeepSeekAssist no debe entregar secretos, credenciales, dumps, cookies, tokens ni datos internos innecesarios.

Salida esperada de Hermes

Toda salida futura de Hermes debe ser tratada como proposal hasta promoción.

Una proposal Hermes debe declarar:

- origen de la necesidad;
- si usó DeepSeekAssist;
- modelo usado por DeepSeekAssist;
- presupuesto/perfil usado;
- coste estimado;
- fuentes externas resumidas;
- confidence;
- permisos requeridos;
- execution_mode mínimo;
- requires_confirmation;
- evidence_contract;
- ToolHealth esperado;
- VersionLock esperado;
- riesgos;
- unknowns;
- rollback;
- aprobación requerida;
- estado IMPLEMENTACION_USUARIO_REQUERIDA si falta lógica privada.

Control de coste en evolución Hermes

Hermes no puede usar DeepSeekAssist como chat libre.

Antes de pedir ayuda externa deben agotarse:

1. documentación local;
2. Knowledge Bootstrap;
3. RAG/memoria local;
4. registry;
5. contratos internos;
6. EvidenceStore;
7. ToolHealth;
8. VersionLock;
9. análisis de Mistral/LaIA.

Si todavía falta conocimiento, la consulta debe ser mínima, cacheable y con salida JSON corta.

Modelo por defecto

Toda evolución futura que requiera DeepSeekAssist debe usar por defecto:

- deepseek-v4-flash.

El uso de:

- deepseek-v4-pro.

queda reservado para casos excepcionales y solo con aprobación explícita del usuario.

No debe existir auto-escalado automático fuera de los modelos configurados ni sin registrar motivo operativo.

Validación X5/OjoRouter

X5/OjoRouter valida toda proposal antes de cualquier ejecución o promoción.

Debe revisar como mínimo:

- scope;
- allowlist;
- permission_level;
- execution_mode;
- requires_confirmation;
- kill_switch;
- EvidenceStore;
- ScoringEngine;
- audit_log;
- VersionLock;
- ToolHealth;
- worker_binding;
- user_approval;
- presupuesto DeepSeekAssist si aplica;
- sanitización de contexto externo;
- cache_key si aplica.

Regla para técnicas ofensivas

La integración Hermes + DeepSeekAssist no debe eliminar técnicas por nombre.

No debe haber bloqueos por palabras como exploit, payload, pivot, credenciales, phishing, MITM, persistencia, evasión, DoS, RF, HackRF, lateral movement o privilege escalation.

El control correcto es scope, permisos, modo, evidencia, kill switch, VersionLock, ToolHealth, audit log y aprobación del usuario.


Tests dinámicos

Hermes puede crear proposals nuevas sin romper tests productivos por conteo. La existencia de una proposal, wrapper candidato o capability experimental no debe contarse como técnica productiva hasta promoción.

El pipeline debe obedecer DYNAMIC_REGISTRY_TESTING_POLICY.md: conteos informativos, invariantes obligatorios y separación clara entre proposal, sandbox, promoted y production.

Regla final

Mistral/LaIA es el cerebro operativo local.
DeepSeekAssist es consulta externa mínima cuando falta conocimiento.
Hermes son las manos que construyen en laboratorio.
X5/OjoRouter es el validador de ejecución.
El usuario gobierna producción.

Nada de este pipeline permite ejecución descontrolada ni promoción automática.
