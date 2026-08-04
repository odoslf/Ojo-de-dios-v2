# Módulo 12 — Orquestación, IA y Evolución del Arsenal

Documento base del Módulo 12. Esta versión define filosofía, jerarquía y modos esperados de la capa de orquestación; no implementa lógica, endpoints, workers, cambios de base de datos, tests ni dependencias.

## Índice final

- [Propósito y filosofía de autonomía supervisada](#propósito-del-módulo)
- [Jerarquía: Usuario, Policy/Kill Switch, Mistral, X5, Hermes Agent, DeepSeek](#jerarquía-de-control)
- [Modos: Asistido, Automático Supervisado, Laboratorio](#modos-de-ejecución)
- [Instalación Mistral/Ollama y Hermes/DeepSeek](#instalación-y-configuración-de-agentes-ia)
- [Bucle autónomo y Fallback Inteligente](#bucle-autónomo-y-fallback-inteligente)
- [Hermes Agent Lab: dependencias, sandbox, estados, promoción y rollback](#hermes-lab-y-ciclo-de-vida-de-técnicas)
- [Panel contextual por módulo](#panel-contextual-por-módulo)
- [Terminal Virtual manual controlado](#terminal-virtual)
- [Redis, SQLite, WebSocket y contratos JSON](#comunicación-persistencia-y-contratos)
- [Scoring X5](#scoring-x5)
- [DeepSeek como arquitecto operativo](#deepseek-chat--arquitecto-operativo-de-laboratorio)
- [Flujo no-code](#flujo-no-code-y-reparto-operativo-de-roles) y [fallback de capacidades](#fallback-de-capacidades-faltantes)
- [App Android](#app-android-y-módulos-13)
- [Criterios de aceptación](#criterios-de-aceptación-documental)

## Propósito del módulo

El Módulo 12 es el cerebro y sistema nervioso central de Ojo de Dios. No es una técnica más, no reemplaza a los módulos técnicos existentes y no debe tratarse como un chat genérico. Su función documental esperada es coordinar la intención del usuario, la validación de políticas, la ejecución controlada por X5/OjoRouter, el registro de evidencias y la evolución segura del arsenal.

Este módulo coordina los dominios de OSINT, vulnerabilidades, explotación, web, credenciales, wireless, Android y futuros módulos. Su misión es:

- orquestar planes técnicos autorizados;
- integrar LaIA/Mistral como asistente contextual en cada página de módulo;
- permitir que Hermes/DeepSeek evolucione el arsenal en laboratorio;
- conectar panel, X5, EvidenceStore, scoring, AuditLog y workers.

El Módulo 12 debe entender el estado operativo global de Ojo de Dios: qué activos están dentro de scope, qué permisos existen, qué evidencias ya fueron generadas, qué workers están disponibles, qué técnica corresponde a cada módulo y qué riesgos deben bloquearse antes de cualquier ejecución. Cuando una ruta, contrato o integración se mencione como futura, debe leerse como arquitectura esperada y no como afirmación de disponibilidad actual.

## Filosofía de autonomía supervisada

La filosofía central del Módulo 12 es la de un sistema todoterreno de laboratorio: semiautomático o autónomo dentro de activos autorizados y laboratorio controlado, pero siempre gobernado por alcance, políticas, auditoría y capacidad de parada inmediata. El objetivo no es que el usuario dependa de comandos manuales ni de memoria operativa herramienta por herramienta; el usuario expresa órdenes de alto nivel y el sistema traduce esa intención a planes técnicos revisables.

En esta filosofía, LaIA/Mistral convierte la intención en planes JSON, parámetros propuestos, evidencias esperadas, criterios de parada, riesgos y explicaciones comprensibles. X5/OjoRouter valida esos planes contra scope, Policy Engine, permisos, disponibilidad de workers, estado de herramientas, Kill Switch y requisitos de confirmación. La ejecución, cuando proceda, debe producir evidencias trazables y eventos auditables, no acciones opacas.

La autonomía supervisada no suaviza el carácter todoterreno del sistema: Ojo de Dios debe poder encadenar técnicas, seleccionar fallback inteligente, adaptar parámetros y avanzar en un flujo técnico sin pedir al usuario comandos de bajo nivel. La supervisión significa que toda acción se mantiene dentro de activos autorizados, con límites explícitos, confirmaciones cuando correspondan, registro de decisiones y control superior del usuario, Policy Engine, scope y Kill Switch.

## Jerarquía de control

La cadena de control del Módulo 12 debe ser clara, predecible y auditable:

1. **Usuario**: máxima autoridad operativa. Aprueba, pausa, deniega o detiene desde el panel o la app. Sus decisiones prevalecen sobre recomendaciones de IA, planes tácticos y flujos automáticos.
2. **Policy Engine / Scope / Kill Switch**: guardián superior antes de ejecución. Valida alcance, permisos, límites, riesgo, estado global y condiciones de parada. El Kill Switch siempre manda y debe poder detener cualquier ejecución activa o futura dentro del sistema.
3. **LaIA/Mistral**: planificador táctico y asistente contextual. Propone planes, rellena parámetros, explica decisiones, resume evidencias, sugiere fallback y ayuda al usuario en cada página de módulo. No ejecuta herramientas directamente.
4. **X5/OjoRouter**: validador y ejecutor. Recibe planes, valida políticas, enruta hacia workers y, cuando corresponda, hacia Kali WSL2 u otros runtimes autorizados. Recoge evidencias, actualiza scoring y devuelve resultados estructurados al panel y a LaIA/Mistral.
5. **Hermes Agent Lab/DeepSeek**: creador de laboratorio. Genera módulos, wrappers, parsers, contratos o propuestas dentro de `modules/laboratory/`. No promociona capacidades a producción ni ejecuta en producción por sí mismo.

Esta jerarquía evita que una recomendación de IA se confunda con autorización de ejecución. LaIA/Mistral asiste; X5/OjoRouter valida y ejecuta; Hermes/DeepSeek crea en laboratorio; Policy Engine, scope y Kill Switch gobiernan; el usuario conserva la autoridad máxima.

## Modos de ejecución

### Modo Asistido

Modo por defecto. LaIA/Mistral analiza el contexto del módulo, propone el siguiente paso, genera un plan revisable y explica riesgos, parámetros y evidencias esperadas. El usuario confirma antes de que X5/OjoRouter intente ejecutar cualquier acción que requiera aprobación. Es el modo recomendado para aprendizaje, operaciones sensibles, validación de hipótesis y uso inicial de técnicas.

Características esperadas:

- LaIA/Mistral propone; el usuario decide.
- Los planes deben ser legibles, auditables y expresados en JSON o contratos equivalentes.
- X5/OjoRouter no debe ejecutar si falta confirmación requerida, scope válido o permiso suficiente.
- El panel debe mostrar estado, riesgos, evidencias esperadas y motivo de bloqueo cuando exista.

### Modo Automático Supervisado

Modo semiautónomo dentro de scope preautorizado. Permite que Ojo de Dios encadene técnicas, aplique fallback inteligente y avance sin solicitar comandos manuales al usuario, siempre que cada paso esté dentro de políticas, permisos, límites y condiciones de parada. X5/OjoRouter valida todo antes de ejecutar y el Kill Switch siempre manda.

Características esperadas:

- Solo opera sobre activos autorizados y scope predefinido.
- Cada acción pasa por Policy Engine, scope, permisos, validación de worker, estado de herramienta y Kill Switch.
- LaIA/Mistral puede recomendar el siguiente paso, pero no ejecuta directamente.
- X5/OjoRouter debe registrar evidencias, resultados, errores, scoring y AuditLog.
- El usuario puede pausar, detener, reducir alcance o volver a Modo Asistido en cualquier momento.

### Modo Laboratorio/Sandbox

Modo reservado para Hermes Agent Lab/DeepSeek y evolución del arsenal. Hermes puede crear y probar nuevas capacidades en laboratorio, generar archivos bajo `modules/laboratory/`, proponer contratos, parsers, wrappers, documentación técnica y pruebas de validación controlada. Este modo no puntúa el scoring general, no promociona dependencias ni incorpora capacidades a producción sin aprobación explícita.

Características esperadas:

- Las capacidades generadas permanecen aisladas del arsenal productivo hasta revisión.
- No se ejecutan contra objetivos productivos ni fuera del laboratorio controlado.
- No alteran scoring general, rutas productivas ni workers principales por sí mismas.
- Dependencias, promoción, activación en panel y conexión con X5 requieren aprobación humana y validación documental/técnica.
- La salida del laboratorio debe ser trazable: propósito, contrato, riesgos, evidencias esperadas, limitaciones y criterio de promoción.

## Instalación y configuración de agentes IA

Esta sección documenta la arquitectura prevista de instalación y configuración de los agentes IA del Módulo 12. No implementa conectores, no crea carpetas, no modifica `.env.example`, no añade dependencias y no habilita ejecución automática. Las rutas, variables y comandos descritos son referencias documentales para rondas futuras.

### LaIA / Mistral local

LaIA será el asistente táctico local de Ojo de Dios. Está pensado para ejecutarse en Windows 10 LTSC sobre la máquina del usuario, con aceleración local orientada a GPU AMD RX 6600 8GB mediante Ollama cuando el entorno lo permita. Su rol es acompañar el trabajo operativo de cada módulo sin sustituir la autoridad del usuario, el Policy Engine, el scope, el Kill Switch ni la validación de X5/OjoRouter.

LaIA/Mistral se integra como:

- chat contextual dentro de cada módulo;
- generador de `attack_plan`;
- rellenador de parámetros técnicos;
- explicador de resultados;
- selector de técnicas registradas usando contexto y scoring X5.

LaIA no ejecuta herramientas directamente. Su salida esperada debe ser un plan, explicación, recomendación o conjunto de parámetros revisables. Toda acción derivada debe pasar por X5/OjoRouter, Policy Engine, scope, permisos, confirmaciones requeridas y Kill Switch.

### Ollama

La instalación local prevista para LaIA/Mistral se documenta sobre Ollama para Windows. El modelo exacto previsto es:

```text
CognitiveComputations/dolphin-mistral-nemo:12b
```

Comandos documentales de preparación y prueba manual:

```powershell
ollama pull CognitiveComputations/dolphin-mistral-nemo:12b
ollama run CognitiveComputations/dolphin-mistral-nemo:12b "Hola, ¿funcionas?"
```

Ojo de Dios hablará con Ollama por REST en una integración futura mediante:

```text
POST http://localhost:11434/api/generate
```

Variables futuras previstas:

```env
MISTRAL_API_URL=http://localhost:11434
MISTRAL_MODEL=CognitiveComputations/dolphin-mistral-nemo:12b
```

Esta ronda solo documenta esas variables. No modifica `.env.example`, no carga configuración real y no activa ningún cliente HTTP.

### Alternativa llama.cpp/Vulkan

Como alternativa avanzada futura, se contempla `llama.cpp` con backend Vulkan y un modelo GGUF compatible para usuarios que prefieran ejecución manual optimizada sobre hardware local. Esta opción queda documentada como ruta técnica posible para perfiles avanzados, no como implementación actual del proyecto.

La alternativa llama.cpp/Vulkan no se implementa en esta ronda. No se añaden binarios, scripts, instrucciones operativas de compilación, dependencias ni cambios de configuración.

### Hermes Agent Lab / DeepSeek

Hermes usa DeepSeek API como motor de generación y evolución de laboratorio. Hermes no sustituye a LaIA/Mistral y no debe confundirse con el asistente táctico contextual de cada módulo:

- LaIA/Mistral = táctico contextual por módulo.
- Hermes = generador de módulos en laboratorio.
- DeepSeek = arquitecto operativo de laboratorio en Orquestación.

Variables futuras previstas:

```env
DEEPSEEK_API_KEY=ALAZAN_REEMPLAZAR_EN_ENV_LOCAL
DEEPSEEK_API_KEY=ALAZAN_REEMPLAZAR_EN_ENV_LOCAL
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-coder
```

No deben escribirse claves reales en el repositorio, documentación, ejemplos versionados, logs ni evidencias. Cualquier clave deberá residir en configuración local privada cuando exista la implementación correspondiente.

### Trabajo aislado de Hermes

Hermes trabaja de forma aislada en la arquitectura prevista:

```text
modules/laboratory/<technique_id>/
```

Cada módulo generado en laboratorio debe poder contener, como contrato documental previsto:

- `technique.json`
- `worker.py`
- `evidence_schema.json`
- `requirements.generated.txt`
- `README.md`

Estas rutas y archivos son arquitectura prevista. No se crean en esta ronda y no implican que exista una implementación productiva. La promoción desde laboratorio hacia el arsenal principal requiere revisión, aprobación humana, validación de seguridad, control de dependencias, trazabilidad en AuditLog y compatibilidad con X5/OjoRouter.

### Dependencias generadas

Regla absoluta: Hermes nunca instala dependencias automáticamente.

Si Hermes genera `requirements.generated.txt`, el panel deberá mostrar el diff completo, pedir aprobación explícita y registrar AuditLog antes de cualquier instalación. La instalación futura, si se aprueba, se realizará dentro del entorno de Ojo de Dios en WSL2 y deberá respetar scope operativo, aislamiento, versionado, revisión humana y capacidad de rollback.

La generación de dependencias por Hermes es una propuesta de laboratorio, no una autorización. Ningún archivo generado debe modificar `requirements`, entornos, workers o runtimes productivos sin flujo de promoción aprobado.

### Fuentes abiertas

Hermes/DeepSeek podrá trabajar con contexto de fuentes abiertas si el laboratorio tiene navegación habilitada y autorizada para esa tarea. Cuando el laboratorio esté aislado, Hermes podrá trabajar con texto aportado por Mistral/LaIA o por el Módulo 9, siempre que ese contexto sea trazable, pertinente y compatible con el scope de laboratorio.

El uso de fuentes abiertas debe conservar la filosofía de autonomía supervisada: la IA puede resumir, comparar, proponer y generar artefactos de laboratorio, pero no promociona capacidades, no instala dependencias y no ejecuta producción sin aprobación y validación por la cadena de control del Módulo 12.


## Bucle autónomo y Fallback Inteligente

Esta sección documenta la arquitectura prevista del bucle autónomo supervisado, la iteración técnica y el fallback inteligente del Módulo 12. No implementa eventos, endpoints, base de datos, workers, colas, registros ni contratos ejecutables. Todo lo descrito es una especificación documental para rondas futuras y debe mantenerse subordinado a la jerarquía de control, scope autorizado, Policy Engine, Kill Switch, AuditLog y aprobación del usuario cuando corresponda.

### Entrada por fingerprint

Los módulos de reconocimiento publican perfiles en el canal/evento `fingerprint`. Esta entrada representa el punto de arranque natural para que Ojo de Dios convierta descubrimientos técnicos en planes de acción autorizados. Los perfiles pueden provenir de OSINT, Vulnerabilidades, Wireless/RF y futuros módulos que generen identificación, superficie de ataque o contexto operativo.

El perfil `fingerprint` debe incluir, cuando exista:

- `target_id`
- IP, dominio o dispositivo
- puertos, servicios y banners
- CVEs asociados
- `fingerprint_confidence`
- `source_module`
- `scope_id` autorizado

La presencia de un `fingerprint` no autoriza ejecución por sí misma. El evento solo aporta contexto técnico inicial; cualquier acción posterior debe conservar scope vigente, trazabilidad, validación de políticas y control superior del usuario/Kill Switch.

### Generación de plan por LaIA/Mistral

LaIA/Mistral recibe el `fingerprint`, consulta el contexto persistente disponible y genera un `attack_plan` JSON. El plan debe convertir el perfil técnico en una propuesta ordenada, explicable y revisable, evitando que el usuario tenga que escribir comandos manuales o seleccionar a ciegas entre herramientas. LaIA propone y prepara; no ejecuta herramientas.

El `attack_plan` debe incluir:

- `plan_id`
- `source_module`
- `target_profile`
- técnicas candidatas ordenadas
- parámetros ya rellenados
- evidencias esperadas
- riesgo/ruido estimado
- `require_approval`
- modo de ejecución: `assisted`, `supervised_auto` o `lab`

El plan debe indicar por qué cada técnica candidata fue seleccionada, qué evidencia se espera, qué ruido o riesgo introduce y qué condición permitiría continuar, detenerse o activar fallback. En Modo Asistido, el usuario confirma antes de ejecutar. En Modo Automático Supervisado, el avance puede encadenarse sin comandos manuales, pero cada paso sigue sujeto a validación de X5/OjoRouter, Policy Engine, scope y Kill Switch.

### Validación y ejecución por X5

X5/OjoRouter recibe el `attack_plan` y lo valida contra Policy Engine, Scope, permisos, estado del Kill Switch y TechniqueRegistry. También debe considerar el modo de ejecución solicitado, la vigencia del `scope_id`, la disponibilidad del worker registrado, el estado de la técnica y los requisitos de confirmación.

Si la validación falla, el plan queda en estado `blocked_by_policy` y se notifica al panel con motivo claro, sin ejecutar herramientas. Si la validación pasa, X5/OjoRouter ejecuta mediante el worker registrado y Kali WSL2 cuando el runtime previsto lo requiera. La ejecución debe producir eventos de progreso, resultado estructurado, evidencias trazables y registros de auditoría.

X5/OjoRouter es el punto de ejecución, no LaIA/Mistral. Esta separación preserva la autonomía supervisada: la IA puede planificar y adaptar, pero la ejecución real queda controlada por políticas, registros, workers autorizados y Kill Switch.

### Iteración automática

El flujo autónomo supervisado esperado es:

1. X5/OjoRouter ejecuta la técnica de mayor prioridad del `attack_plan`.
2. Publica progreso como `execution_progress` para que panel, app y asistentes contextuales puedan mostrar estado en tiempo real.
3. Al terminar, guarda resultado persistente y publica `execution_result`.
4. Si hay éxito con evidencia válida, EvidenceStore guarda pruebas, scoring actualiza y el plan queda `completed`.
5. Si falla, X5/OjoRouter pasa a la siguiente técnica candidata del plan, siempre revalidando las condiciones aplicables antes de ejecutar.
6. Si se agotan las candidatas, el plan queda `paused` y se activa Fallback Inteligente.

Este flujo no debe convertirse en una cadena manual de comandos. El usuario da intención de alto nivel, el sistema mantiene el bucle técnico dentro de scope autorizado y X5/OjoRouter decide continuar, bloquear, pausar o pedir confirmación según política, riesgo, evidencias y modo operativo.

### Fallback Inteligente

El Fallback Inteligente se activa cuando las técnicas candidatas no producen evidencia válida, cuando el plan agota opciones o cuando el error indica que falta capacidad en el arsenal. Mistral analiza error observado, perfil del objetivo, CVE asociado, historial de ejecución, evidencias previas, scoring y contexto persistente. Si falta capacidad, genera una `create_module_request` para Hermes.

La `create_module_request` debe incluir:

- `source_module`
- descripción técnica
- contexto completo
- error observado
- PoC/link si existe
- evidence esperada
- `plan_id` pausado

Hermes debe crear un módulo completo en laboratorio, no un simple esqueleto. La salida esperada bajo arquitectura prevista incluye `technique.json`, `worker.py`, parser, `evidence_schema.json`, `requirements.generated.txt` si procede y `README.md`. Esa creación permanece aislada en laboratorio, no ejecuta producción, no modifica workers principales y no promociona capacidades por sí misma.

El fallback mantiene la filosofía todoterreno de laboratorio: el sistema intenta avanzar de forma autónoma y útil dentro de límites autorizados, pero cualquier nueva capacidad queda separada, revisable, auditable y sujeta a promoción explícita.

### Plan pausado y reanudación

Cuando se activa Fallback Inteligente, el plan original queda `paused` en SQLite como fuente de verdad persistente. El estado pausado debe conservar `plan_id`, objetivo, fingerprint, técnicas probadas, errores, evidencias asociadas, motivo de pausa y relación con la `create_module_request` enviada a Hermes.

El plan solo puede reanudarse si se cumplen todas estas condiciones:

- la técnica nueva está `promoted`;
- el scope sigue vigente;
- el usuario activó “reanudar automáticamente” o confirma manualmente;
- X5/OjoRouter revalida Policy Engine y Kill Switch;
- la técnica ya está registrada y con scoring inicial.

La reanudación no debe depender de memoria volátil ni de eventos perdidos. X5/OjoRouter debe reconstruir el estado desde SQLite, verificar EvidenceStore y AuditLog cuando corresponda, confirmar la técnica registrada en TechniqueRegistry y continuar desde el punto seguro del plan, no desde una suposición generada por la IA.

### Redis vs SQLite

La persistencia y mensajería del Módulo 12 deben separarse con claridad:

- Redis Pub/Sub = eventos en tiempo real.
- SQLite = fuente de verdad persistente.
- EvidenceStore = evidencias.
- AuditLog = aprobaciones, bloqueos, promociones y cambios de estado.

Redis Pub/Sub sirve para notificar `fingerprint`, `execution_progress`, `execution_result`, cambios visibles en panel y señales operativas de tiempo real. No debe usarse como histórico ni como única fuente de recuperación ante caída del proceso.

SQLite conserva planes, estados, referencias, pausas, reanudaciones y relaciones entre fingerprint, plan, ejecución, fallback y promoción. EvidenceStore conserva pruebas y artefactos. AuditLog conserva decisiones humanas y automáticas relevantes: aprobaciones, denegaciones, bloqueos por política, activación de Kill Switch, solicitudes de creación, promociones y cambios de estado. El sistema no debe depender de Redis como histórico.


## Hermes Agent Lab y ciclo de vida de técnicas

Esta sección documenta el ciclo de vida previsto para técnicas creadas o evolucionadas por Hermes Agent Lab. No implementa lógica, no crea carpetas, no modifica workers, no toca base de datos real, no cambia dependencias y no añade tests. Las rutas, comandos y eventos descritos son arquitectura documental para rondas futuras.

### Rol de Hermes Agent Lab

Hermes/DeepSeek es el motor de evolución del arsenal. Trabaja solo en laboratorio y crea módulos completos cuando falta una capacidad técnica. No es un chat decorativo ni un generador de esqueletos vacíos: su función es producir una unidad de laboratorio revisable, trazable y preparada para validación controlada antes de cualquier promoción.

Hermes podrá generar, dentro de la arquitectura prevista:

```text
modules/laboratory/<technique_id>/
```

los siguientes artefactos:

- `technique.json`
- `worker.py`
- parser de salida si aplica
- `evidence_schema.json`
- `requirements.generated.txt` si necesita dependencias
- `README.md`

Estas rutas y archivos son arquitectura prevista y no deben crearse en esta ronda. Ningún artefacto de Hermes queda disponible para producción por el simple hecho de existir en laboratorio.

### Estados de una técnica

El ciclo de vida documental de una técnica generada, importada o evolucionada por Hermes debe usar estos estados exactos:

- `experimental`: recién creada/importada; visible solo en laboratorio; no ejecutable automáticamente.
- `lab_ready`: pasó sintaxis y validación documental mínima.
- `review_required`: usuario pidió informe de revisión a Mistral/DeepSeek.
- `approved_by_user`: aprobada para pruebas controladas tras revisión y evidencia sandbox.
- `promoted`: integrada en `modules/custom/<module>/<technique_id>/` y disponible para X5/Mistral.
- `rejected`: descartada, conservando trazabilidad.

Ninguna técnica puede saltar de `experimental` a `promoted`. La promoción requiere pasar por validaciones, revisión, evidencia de sandbox y aprobación humana explícita.

### Validación para lab_ready

Para que una técnica pueda pasar a `lab_ready`, debe cumplir como mínimo:

- `python -m py_compile worker.py` sin errores.
- `technique.json` completo.
- `evidence_schema.json` válido.
- `requirements.generated.txt` válido si existe.
- técnica asociada a un módulo destino real: exploitation, web, wireless, android, cloud, etc.

La validación `lab_ready` no autoriza ejecución productiva ni promoción. Solo confirma que la técnica tiene una forma mínima revisable dentro del laboratorio.

### Dependencias

Regla absoluta: Hermes nunca instala dependencias automáticamente.

Si existe `requirements.generated.txt`, el panel debe:

- mostrar paquetes nuevos;
- comparar con dependencias actuales;
- pedir aprobación explícita;
- registrar decisión en AuditLog;
- si se aprueba, ejecutar en entorno Ojo de Dios/WSL2:

```bash
pip install -r modules/laboratory/<technique_id>/requirements.generated.txt
```

Si el usuario rechaza la instalación, la técnica queda `experimental` o bloqueada para prueba/promoción. La existencia de dependencias propuestas no implica autorización de instalación ni modificación del entorno.

### Sandbox

La acción “Probar en sandbox” solo está disponible si:

- técnica está `lab_ready` o `approved_by_user`;
- dependencias instaladas;
- objetivo dentro de scope de laboratorio;
- Kill Switch activo y visible;
- ejecución registrada en AuditLog.

El resultado de una prueba sandbox genera evidencia de laboratorio en EvidenceStore, pero no puntúa scoring general. La evidencia de laboratorio sirve para revisión, aprobación y promoción controlada; no debe mezclarse con resultados productivos ni activar planes automáticos fuera del laboratorio.

### Revisión y aprobación

Mistral/DeepSeek puede generar un informe de revisión para una técnica de laboratorio. El informe debe cubrir:

- coherencia con contratos Ojo de Dios;
- evidence schema;
- riesgos técnicos;
- dependencias;
- veredicto: recomendado / requiere cambios.

Para alcanzar `approved_by_user` debe existir prueba sandbox con evidencia real y un botón explícito del usuario. La aprobación no debe inferirse a partir de una recomendación de IA, un estado de archivo, una ejecución parcial o un resultado sin evidencia trazable.

### Promoción y rollback

La promoción de una técnica desde laboratorio al arsenal disponible para X5/Mistral requiere este checklist:

- contrato válido;
- worker funcional;
- evidence schema;
- sandbox exitoso;
- revisión IA;
- aprobación humana;
- dependencias instaladas;
- backup en `modules/laboratory/backup/<technique_id>/`.

La promoción mueve la técnica a la arquitectura prevista `modules/custom/<module>/<technique_id>/`, registra el estado `promoted`, crea score inicial 50 y publica el evento `technique_promoted`. Desde ese momento, la técnica puede quedar disponible para selección por Mistral/LaIA y ejecución por X5/OjoRouter, siempre bajo Policy Engine, Scope, TechniqueRegistry y Kill Switch.

Rollback devuelve la técnica a laboratorio, la excluye de planes, elimina scoring activo y registra AuditLog. El rollback debe conservar trazabilidad de promoción, motivo de reversión, evidencias relacionadas y estado final para que el usuario pueda auditar qué cambió y por qué.


## Panel contextual por módulo

Esta sección documenta la arquitectura prevista del panel contextual por módulo. No implementa HTML, endpoints, componentes, workers, base de datos ni tests. El objetivo es fijar el modelo de interacción: Ojo de Dios debe conservar su enfoque semiautomático/autónomo supervisado, donde el usuario expresa intención de alto nivel, LaIA/Mistral propone planes técnicos y X5/OjoRouter valida y ejecuta bajo Policy Engine, scope y Kill Switch.

### Principio general

Ojo de Dios no tendrá solo un chat global. Cada módulo tendrá su propia página o panel con IA contextual integrada, adaptada a los objetivos, técnicas, evidencias y permisos de ese dominio. Los paneles previstos incluyen:

- OSINT
- Vulnerabilidades
- Explotación
- Web
- Credenciales
- Wireless/RF
- Android
- Phishing
- Cloud
- Evidencia/Ops

LaIA/Mistral debe conocer el módulo activo, el objetivo seleccionado, las técnicas disponibles, el estado de herramientas, las evidencias previas y los permisos vigentes. Ese contexto permite que el asistente proponga planes útiles sin obligar al usuario a traducir manualmente cada intención en comandos, parámetros o selección de herramientas.

El panel contextual no sustituye a X5/OjoRouter ni al Policy Engine. LaIA/Mistral asiste, explica y prepara; X5/OjoRouter valida y ejecuta; el usuario conserva control superior y Kill Switch permanece por encima de cualquier flujo.

### Estructura común de una página de módulo

Cada página de módulo debe tener, como arquitectura prevista:

- campos específicos del módulo;
- selector/visor de objetivo;
- lista de técnicas con estado;
- visor de herramientas necesarias;
- chat contextual LaIA;
- botón “Ejecutar plan sugerido”;
- visor de evidencias;
- acceso a Hermes si falta una capacidad.

Los campos específicos deben reflejar el dominio real del módulo, no un formulario genérico. El selector de objetivo debe mostrar el activo dentro de scope, su estado y referencias relevantes. La lista de técnicas debe indicar disponibilidad, estado, requisitos, scoring y si la técnica está promovida, experimental o bloqueada. El visor de herramientas debe mostrar qué binarios, servicios, runtimes o dependencias serían necesarios antes de intentar cualquier ejecución.

### Ejemplo Android

Como ejemplo futuro, una página contextual de Android podría exponer:

- “Dispositivo conectado”: detección por `adb devices`, modelo, versión Android, root/no root.
- “Tipo de payload”: `reverse_tcp`, `reverse_https`, `bind_tcp`.
- “Ofuscación”: ProGuard, Obfuscapk, Donut, ninguna.
- Técnicas Android con estado: promovida, experimental, requiere herramienta.
- Herramientas: adb, apktool, msfvenom, jarsigner/apksigner.
- Visor de APKs generadas, sesiones, capturas y evidencias.

Este ejemplo es documental y futuro. No afirma que la página Android, detección ADB, generación de APKs, sesiones, capturas o integración de herramientas estén implementadas en esta ronda.

### Chat contextual

El flujo esperado del chat contextual es:

1. El usuario escribe una intención natural dentro del panel del módulo activo.
2. LaIA/Mistral recibe el contexto completo del módulo: objetivo seleccionado, scope, permisos, técnicas registradas, scoring, estado de herramientas, evidencias previas y modo operativo.
3. LaIA/Mistral consulta TechniqueRegistry, scoring X5 y estado de herramientas para proponer un plan técnico con parámetros ya rellenados.
4. LaIA/Mistral explica qué hará el plan, qué evidencia espera, qué riesgo/ruido introduce y qué confirmaciones serían necesarias.
5. Si falta una técnica, wrapper, parser o `evidence_schema`, LaIA/Mistral puede indicar la carencia y derivar a Hermes Agent Lab mediante una solicitud de creación de capacidad de laboratorio.

LaIA/Mistral no ejecuta herramientas desde el chat contextual. Su función es interpretar intención, preparar `attack_plan`, explicar resultados y derivar a Hermes cuando falta capacidad, manteniendo siempre la autonomía supervisada.

### Botón “Ejecutar plan sugerido”

El botón “Ejecutar plan sugerido” no ejecuta directamente. Debe funcionar como puente revisable entre la recomendación contextual y la validación formal por X5/OjoRouter.

El flujo documental esperado es:

- solicitar `attack_plan` a Mistral;
- mostrar modal con técnicas, parámetros, riesgos, evidencias esperadas y modo;
- permitir modificar/cancelar;
- tras confirmación, enviar a X5;
- X5 valida Policy Engine/Kill Switch antes de ejecutar.

El modal debe dejar claro qué se intenta hacer, sobre qué objetivo, con qué permisos y qué evidencias se esperan. Si el usuario cancela, no se ejecuta nada. Si confirma, la confirmación no reemplaza la validación de X5/OjoRouter: el plan aún puede quedar bloqueado por Policy Engine, scope, permisos, TechniqueRegistry, estado de herramientas o Kill Switch.

## Terminal Virtual

Esta sección documenta la Terminal Virtual como capacidad prevista para fase futura. No implementa terminal, HTML, WebSocket, shell, endpoints, workers, persistencia ni pruebas. Su propósito es cubrir casos expertos e interactivos sin convertir el proyecto en un flujo manual ni recortar la automatización principal.

### Propósito

La Terminal Virtual es un modo experto/manual secundario, no el flujo principal de Ojo de Dios. Debe estar pensada para herramientas interactivas o capacidades que todavía no estén encapsuladas en workers, adapters o planes JSON. En una fase futura, el diseño previsto es usar xterm.js + WebSocket hacia una shell Kali WSL2 controlada.

El flujo principal sigue siendo semiautomático: intención de alto nivel, planes JSON, validación por X5/OjoRouter, workers registrados, EvidenceStore, scoring, AuditLog y aprobación cuando corresponda. La terminal existe como vía de soporte experto, no como sustituto de la orquestación.

### Reglas

La Terminal Virtual debe obedecer estas reglas documentales:

- solo usuario teclea comandos;
- IA no escribe ni ejecuta comandos dentro del terminal;
- ayuda de IA vuelve al chat contextual;
- sesión con scope laboratorio, Kill Switch visible y logs;
- al cerrar, preguntar si guardar como evidencia `manual_terminal_session`;
- AuditLog registra apertura, cierre y decisión del usuario.

Si el usuario necesita ayuda, LaIA/Mistral puede explicar conceptos, revisar salida pegada por el usuario o sugerir un plan formal en el chat contextual, pero no debe tomar control de la terminal ni ejecutar comandos por el usuario. Cualquier acción manual queda bajo responsabilidad explícita del usuario, con scope visible, Kill Switch disponible y registro auditable.

### Seguridad documental

La Terminal Virtual existe para herramientas interactivas no encapsuladas todavía. Su presencia no debe degradar el diseño central de Ojo de Dios ni convertir el sistema en una consola manual. El camino preferente sigue siendo: planes JSON, X5/OjoRouter, workers, EvidenceStore, scoring, AuditLog y aprobación.

La salida de una sesión manual puede conservarse como evidencia si el usuario lo decide al cerrar la terminal. Si se guarda, debe quedar clasificada como `manual_terminal_session`, asociada al scope de laboratorio, objetivo, usuario, timestamps y decisión de conservación. Si el usuario decide no guardarla, AuditLog debe registrar la decisión sin promover esa salida a evidencia operativa.


## Comunicación, persistencia y contratos

Esta sección documenta la arquitectura prevista de comunicación, persistencia, contratos JSON, WebSocket y scoring X5 del Módulo 12. No implementa código, no crea endpoints, no toca base de datos real, no crea migraciones y no añade tests. Todo lo descrito es una especificación documental para futuras rondas de implementación.

### Arquitectura de comunicación

La comunicación del Módulo 12 se organiza en tres capas complementarias:

- **Redis Pub/Sub**: eventos en tiempo real entre Mistral, X5, Hermes Agent y Panel.
- **SQLite/DB**: fuente de verdad persistente para planes, resultados, registry, scoring y auditoría.
- **WebSocket FastAPI**: actualización en vivo para panel web y app Android.

Redis no guarda histórico y no debe ser tratado como sistema de recuperación. Todo evento importante debe persistirse primero o inmediatamente en SQLite, AuditLog o EvidenceStore, según corresponda. Redis solo transporta señales vivas para coordinar componentes y refrescar interfaces; la reconstrucción de estado debe venir de la capa persistente.

### Canales Redis oficiales

Los canales Redis oficiales previstos son:

- `fingerprint`: módulos 1/2/10 u otros publican perfiles.
- `attack_plan`: Mistral publica planes para X5.
- `execution_progress`: X5 informa progreso al panel.
- `execution_result`: X5 publica resultado final.
- `create_module_request`: Mistral/DeepSeek solicitan creación a Hermes.
- `module_created`: Hermes informa módulo experimental creado.
- `install_dependencies`: petición controlada de instalación aprobada.
- `execute_sandbox_test`: petición de prueba en laboratorio.
- `promote_module`: promoción solicitada desde panel/DeepSeek.
- `technique_promoted`: X5 informa técnica promocionada.
- `user_notification`: mensajes al usuario.

Cada publicación debe incluir identificadores correlacionables cuando existan, como `plan_id`, `technique_id`, `target_id`, `scope_id`, usuario o timestamp. La emisión de un canal no sustituye validaciones de Policy Engine, Scope, TechniqueRegistry, permisos, Kill Switch ni aprobación humana cuando aplique.

### Tablas persistentes previstas

Como arquitectura esperada, la capa SQLite/DB deberá conservar estas entidades persistentes. No se crean tablas en esta ronda.

- `technique_registry`: técnica, módulo, estado, rutas, metadatos.
- `technique_scores`: `technique_id`, `target_type`, `success`, `evidence_valid`, `score`.
- `attack_plans`: `plan_id`, target, estado `pending`/`running`/`paused`/`completed`/`failed`/`blocked`.
- `execution_results`: resultado por técnica.
- `evidence_store`: referencias a evidencias.
- `audit_log`: decisiones, aprobaciones, bloqueos, instalaciones, promociones.
- `deepseek_chat_history`: historial extensión DeepSeek.

SQLite/DB debe permitir reconstruir el estado después de reinicio, caída de Redis, cierre del panel o pérdida temporal de WebSocket. EvidenceStore conserva artefactos y pruebas; AuditLog conserva decisiones y cambios de estado relevantes.

### Contratos JSON principales

Los contratos JSON principales se documentan de forma resumida como arquitectura prevista. Estos contratos no son schemas implementados en esta ronda.

#### `fingerprint`

Campos esperados:

- `type`
- `source_module`
- `target_profile`
- `cves`
- `confidence`
- `scope_id`

#### `attack_plan`

Campos esperados:

- `type`
- `plan_id`
- `source_module`
- `target_profile`
- `techniques[]`
- `require_approval`
- `mode`
- `created_at`

#### `execution_progress`

Campos esperados:

- `plan_id`
- `technique_id`
- `status`
- `message`
- `timestamp`

#### `execution_result`

Campos esperados:

- `plan_id`
- `technique_id`
- `status`
- `evidence`
- `time_spent`
- `score_delta`
- `error`

#### `create_module_request`

Campos esperados:

- `source_module`
- `description`
- `context`
- `paused_plan_id`

#### `module_created`

Campos esperados:

- `technique_id`
- `module_path`
- `dependencies`
- `state`

#### `promote_module`

Campos esperados:

- `technique_id`
- `approved_by`
- `checklist_status`

#### `technique_promoted`

Campos esperados:

- `technique_id`
- `module`
- `registry_state`

### Scoring X5

El scoring X5 debe medir utilidad real de técnicas bajo evidencia válida y trazabilidad. Sus reglas documentales son:

- solo puntúa si `evidence_valid=true`;
- éxito sin evidencia no sube;
- fallos reales bajan;
- `experimental` y `lab_ready` no puntúan;
- `promoted` puede puntuar;
- score inicial 50 si no hay histórico;
- fórmula orientativa:

```text
nuevo_score = (score_anterior * 9 + resultado * 1) / 10
```

Donde `resultado` es 100 si hubo éxito con evidencia y 0 si fue fallo real. Un resultado bloqueado por política, cancelado por usuario, detenido por Kill Switch o no ejecutado por falta de scope no debe mezclarse automáticamente con fallos reales de eficacia técnica.

El scoring no reemplaza la autorización. Una técnica con score alto sigue requiriendo scope válido, permisos, Policy Engine, TechniqueRegistry, Kill Switch y confirmaciones cuando correspondan. Una técnica de laboratorio no debe influir en scoring general hasta estar `promoted`.

### WebSocket Panel/App

El panel web y la app Android reciben actualizaciones en vivo mediante WebSocket FastAPI en una integración futura. Los eventos previstos para entrega en vivo son:

- `execution_progress`
- `execution_result`
- `user_notification`
- `module_created`
- `technique_promoted`

La conexión WebSocket requiere autenticación JWT/PIN y no debe enviar secretos sin control. Los mensajes al panel/app deben evitar exponer claves, tokens, credenciales, rutas sensibles o contenido que no corresponda al usuario/scope autenticado. El WebSocket actualiza vista y estado operativo, pero la fuente de verdad persistente sigue siendo SQLite/DB, EvidenceStore y AuditLog.


## DeepSeek — arquitecto operativo de laboratorio

Esta sección documenta la arquitectura prevista de DeepSeek dentro del Módulo 12. No implementa endpoints, no modifica base de datos real, no toca workers, no cambia dependencias y no añade tests. DeepSeek debe quedar definido como una capacidad operativa de laboratorio bajo orden del usuario, no como un chat pasivo ni como una revisión decorativa.

### Rol real

DeepSeek no es solo conversación ni un simple revisor. Es una pestaña independiente en Orquestación desde la que el usuario puede dar órdenes de alto nivel para que DeepSeek diseñe, genere y dirija trabajo de laboratorio a través de Hermes. Su función es actuar como arquitecto avanzado del laboratorio: entiende intención, diseña acciones estructuradas, propone cambios, solicita tareas a Hermes/agente laboratorio y mantiene trazabilidad de decisiones, riesgos y evidencias esperadas.

Separación de roles:

- **LaIA/Mistral**: asistente táctico contextual en cada módulo.
- **DeepSeek**: arquitecto avanzado con conversación directa.
- **Hermes/agente laboratorio**: ejecutor de tareas de laboratorio.
- **X5**: ejecutor de técnicas promovidas/registradas fuera del laboratorio.

DeepSeek puede diseñar y dirigir trabajo de laboratorio, pero no promociona por sí mismo, no instala dependencias sin aprobación, no ejecuta técnicas productivas y no sustituye a X5/OjoRouter. La autoridad final sigue siendo del usuario, con Policy Engine, Scope, Kill Switch, AuditLog y EvidenceStore como controles obligatorios.

### Pestaña DeepSeek

La pestaña DeepSeek debe permitir, como arquitectura prevista:

- conversación libre;
- enviar contexto del módulo/técnica/objetivo;
- generar código;
- revisar código;
- corregir módulos;
- crear tareas para Hermes;
- ver acciones pendientes;
- aprobar instalación de dependencias;
- lanzar pruebas sandbox;
- ver resultados y evidencias.

Esta pestaña debe mostrar con claridad qué parte es conversación, qué parte es propuesta y qué parte es acción pendiente. Ninguna acción de laboratorio debe quedar implícita: antes de publicar una tarea para Hermes/agente laboratorio, el panel debe presentar resumen, archivos afectados, dependencias, riesgos, scope, evidencia esperada y decisión requerida del usuario.

### Órdenes que el usuario puede dar

Ejemplos de intención que el usuario puede expresar en DeepSeek:

- “Crea un módulo para...”
- “Corrige el módulo X con este error...”
- “Instala las dependencias del módulo X”
- “Prueba el módulo X en sandbox”
- “Adapta esta PoC al contrato de Ojo de Dios”
- “Prepara la promoción del módulo X”
- “Genera parser/evidence schema/panel fields para esta técnica”

DeepSeek debe traducir esas intenciones en acciones estructuradas, no en ejecución directa e invisible. Si falta información, debe pedir aclaración o producir una acción pendiente bloqueada hasta completar contexto, scope, dependencias o aprobación.

### Flujo operativo

Flujo documental esperado:

1. El usuario escribe en DeepSeek.
2. DeepSeek interpreta la intención y genera una acción estructurada.
3. El panel muestra la acción pendiente con resumen, archivos afectados, dependencias, riesgos y evidencia esperada.
4. Si el usuario confirma, el servidor publica tarea para Hermes/agente laboratorio.
5. Hermes/agente laboratorio ejecuta la tarea dentro del sandbox/laboratorio previsto y devuelve logs, resultados y evidencias.
6. El panel actualiza estado, muestra resultados y registra decisiones relevantes en AuditLog.

Canales/acciones documentales asociados:

- `create_module_request`
- `update_lab_module`
- `install_dependencies`
- `execute_sandbox_test`
- `generate_review_report`
- `prepare_promotion`
- `promote_module`

La confirmación del usuario no elimina las validaciones. Las acciones deben respetar scope de laboratorio, estados de técnica, dependencias aprobadas, Kill Switch visible y trazabilidad completa.

### Hermes/agente laboratorio

Hermes/agente laboratorio recibe las tareas creadas desde DeepSeek y trabaja dentro de la arquitectura prevista:

```text
modules/laboratory/<technique_id>/
```

Puede:

- crear `technique.json`;
- crear/modificar `worker.py`;
- crear parser;
- crear `evidence_schema.json`;
- crear `requirements.generated.txt`;
- crear `README.md`;
- ejecutar validación de sintaxis;
- lanzar prueba sandbox;
- devolver logs y evidencias.

Todo trabajo de Hermes debe quedar aislado en laboratorio hasta revisión y promoción. La creación o modificación de un módulo de laboratorio no implica disponibilidad para X5, no altera workers productivos y no modifica scoring general hasta que la técnica esté `promoted`.

### Dependencias desde DeepSeek

DeepSeek puede pedir instalar dependencias, pero el panel debe mostrar diff y pedir confirmación explícita. La vista de aprobación debe explicar paquetes nuevos, comparación con dependencias actuales, módulo afectado, motivo técnico, riesgos y entorno de instalación.

Tras aprobación, Hermes/agente laboratorio ejecuta en el entorno de Ojo de Dios/WSL2:

```bash
pip install -r modules/laboratory/<technique_id>/requirements.generated.txt
```

La decisión y el resultado deben registrarse en AuditLog. Si el usuario rechaza la instalación, la acción queda cancelada o bloqueada y la técnica no debe avanzar a prueba/promoción dependiente de esas librerías.

### Terminal/laboratorio

DeepSeek no escribe en el Terminal Virtual manual del usuario. Para “teclear cosas” o ejecutar acciones de laboratorio debe crear tareas estructuradas para Hermes/agente laboratorio, con logs, scope, sandbox y evidencia. La Terminal Virtual queda reservada para modo experto manual, donde solo el usuario teclea comandos.

Si DeepSeek necesita validar sintaxis, ejecutar una prueba sandbox, adaptar una PoC o preparar una promoción, debe generar una acción estructurada y esperar confirmación del usuario cuando corresponda. La salida debe volver al panel como logs y evidencias, no como comandos inyectados en la terminal manual.

### Historial y trazabilidad

La arquitectura futura contempla la tabla `deepseek_chat_history` para conservar conversaciones, acciones propuestas, contexto asociado y resultados visibles de DeepSeek. Esta tabla debe relacionarse con `audit_log` para que toda acción ordenada desde DeepSeek quede trazada con `conversation_id`.

Toda acción originada en DeepSeek debe poder responder:

- quién la solicitó;
- en qué `conversation_id` nació;
- qué intención natural la originó;
- qué acción estructurada se generó;
- qué archivos o dependencias afectaba;
- quién aprobó o rechazó;
- qué tarea recibió Hermes/agente laboratorio;
- qué logs, evidencias o errores devolvió;
- si derivó o no en promoción, rollback o bloqueo.

DeepSeek queda así como arquitecto operativo de laboratorio bajo orden del usuario: conversa, diseña, estructura, revisa y dirige tareas a Hermes, pero toda ejecución relevante permanece confirmable, auditable, aislada y subordinada a la cadena de control del Módulo 12.


## Flujo no-code y reparto operativo de roles

Esta sección documenta el flujo no-code previsto y el reparto operativo de responsabilidades entre Mistral/LaIA, X5/OjoRouter, Hermes Agent, DeepSeek y el usuario. No implementa código, endpoints, base de datos, workers, dependencias ni tests. El objetivo es fijar una regla de arquitectura: el usuario gobierna desde panel/app, Mistral dirige la operación táctica, X5 ejecuta lo validado y Hermes Agent construye en laboratorio lo que falte.

### Principio no-code

El usuario no debe escribir código, scripts ni comandos para usar Ojo de Dios en el flujo principal. La operación normal debe realizarse desde panel web o app mediante lenguaje natural, formularios, botones, modales de revisión y planes técnicos revisables. La Terminal Virtual queda como modo experto secundario, no como camino principal.

El usuario pide objetivos de alto nivel. La plataforma traduce esa intención en:

- parámetros técnicos;
- técnicas candidatas;
- acciones estructuradas;
- evidencias esperadas;
- riesgos;
- tareas para X5 o para Hermes Agent.

Este principio no recorta autonomía supervisada: al contrario, evita que el usuario tenga que programar, recordar comandos o armar scripts manuales. LaIA/Mistral y DeepSeek ayudan a convertir intención en planes y tareas; X5/OjoRouter y Hermes Agent ejecutan solo dentro de sus límites, con validación, trazabilidad y confirmación cuando corresponda.

### Roles exactos

El reparto de roles debe quedar sin ambigüedad:

- **Mistral/LaIA** es el cerebro operativo y táctico. Está dentro de cada módulo, entiende el contexto activo, dirige planes, rellena parámetros, selecciona técnicas registradas y decide cuándo falta una capacidad.
- **X5/OjoRouter** es el validador y ejecutor. Recibe planes, valida Policy Engine, Scope, Kill Switch y TechniqueRegistry, y ejecuta con workers.
- **Hermes Agent** es el constructor/agente de laboratorio. Implementa lo que falta en `modules/laboratory/`, genera archivos, valida, prueba en sandbox y devuelve resultados.
- **DeepSeek** es arquitecto avanzado y apoyo de investigación/código. Puede ordenar tareas a Hermes Agent cuando el usuario lo pide, pero no sustituye a Mistral como cerebro táctico.
- **Usuario** gobierna todo desde panel/app.

Ningún rol debe invadir la responsabilidad crítica de otro. Mistral/LaIA no ejecuta herramientas directamente. X5/OjoRouter no inventa capacidades de laboratorio. Hermes Agent no toca producción directamente. DeepSeek no reemplaza al asistente táctico contextual. El usuario conserva autoridad final sobre confirmaciones, pausas, denegaciones y detención.

### Flujo desde un módulo

Flujo general esperado desde un módulo como Android, Web, Wireless u OSINT:

1. El usuario entra en el módulo y selecciona o confirma un objetivo autorizado.
2. El usuario escribe una intención natural o usa un formulario/botón del panel.
3. Mistral/LaIA recibe módulo activo, target, herramientas instaladas, técnicas disponibles, scoring, evidencias previas y permisos.
4. Mistral/LaIA genera un `attack_plan` con técnicas candidatas, parámetros rellenos, evidencias esperadas, riesgos, modo de ejecución y requisitos de aprobación.
5. El panel muestra el plan de forma revisable para que el usuario pueda entender, modificar, confirmar o cancelar.
6. Tras confirmación o en modo automático supervisado, X5/OjoRouter valida Policy Engine, Scope, Kill Switch, TechniqueRegistry, permisos y workers.
7. Si la validación pasa, X5/OjoRouter ejecuta mediante workers y registra progreso, resultado, evidencias, scoring y AuditLog.
8. Si la validación falla, el plan queda bloqueado o pausado con explicación visible en el panel.

Este flujo mantiene la operación en lenguaje natural y UI supervisada. El usuario no debe programar un módulo ni escribir comandos para que el sistema seleccione técnicas, prepare parámetros, ejecute validaciones o recopile evidencias.

### Cuando falta algo

Si Mistral/LaIA detecta que falta una técnica, parser, wrapper, payload contract, evidence schema, conector, plantilla o soporte de herramienta, no improvisa una ejecución insegura ni pide al usuario programar. Debe crear una tarea estructurada para Hermes Agent, manteniendo el plan original pausado si corresponde y conservando contexto, objetivo, error, evidencia esperada y motivo de la carencia.

Tareas documentales que Mistral/LaIA puede generar para Hermes Agent:

- `create_lab_module`
- `update_lab_module`
- `generate_parser`
- `generate_evidence_schema`
- `prepare_tool_wrapper`
- `run_syntax_check`
- `execute_sandbox_test`
- `prepare_promotion`
- `resume_paused_plan`

Estas tareas son arquitectura prevista. No implican ejecución actual ni creación de archivos en esta ronda. Cualquier tarea que modifique dependencias, prepare promoción o lance prueba sandbox debe pasar por confirmación, AuditLog, scope de laboratorio y Kill Switch visible cuando aplique.

### DeepSeek

DeepSeek se usa para trabajos profundos de arquitectura, investigación y código de laboratorio. Ejemplos de uso:

- “crea un módulo”;
- “adapta esta PoC”;
- “corrige este fallo”;
- “genera parser”;
- “pide a Hermes que lo pruebe”.

DeepSeek genera la propuesta técnica y la convierte en tarea para Hermes Agent con aprobación del usuario cuando la acción modifique sistema, dependencias o promoción. DeepSeek puede analizar contexto amplio, razonar sobre contratos, diseñar cambios, revisar resultados y preparar acciones, pero no sustituye a Mistral/LaIA como cerebro táctico integrado en cada módulo.

### Hermes Agent

Hermes Agent trabaja solo en la arquitectura prevista:

```text
modules/laboratory/<technique_id>/
```

Puede crear o modificar:

- `technique.json`
- `worker.py`
- parser
- `evidence_schema.json`
- `requirements.generated.txt`
- `README.md`

Hermes Agent devuelve estado, diff, logs, archivos y evidencias. No toca producción directamente. No instala dependencias sin aprobación. No registra técnicas como promovidas por sí mismo. No altera scoring general hasta que una técnica pase por revisión, sandbox, aprobación humana, promoción y registro formal.

### Regla final

Mistral/LaIA dirige la operación táctica. X5/OjoRouter ejecuta lo validado. Hermes Agent implementa lo que falta en laboratorio. DeepSeek diseña, revisa y puede ordenar tareas a Hermes Agent bajo petición del usuario. Terminal Virtual queda como modo experto secundario.

El flujo principal de Ojo de Dios debe seguir siendo no-code, semiautomático y supervisado: intención de alto nivel, contexto de módulo, planes JSON, validación X5, workers, EvidenceStore, scoring, AuditLog, fallback inteligente y laboratorio controlado para nuevas capacidades.


## Fallback de capacidades faltantes

Esta sección documenta el mecanismo previsto para que Ojo de Dios evolucione cuando descubre que falta una capacidad técnica. No implementa código, no crea carpetas, no define endpoints reales, no modifica base de datos, no toca workers, no cambia requirements y no añade tests. Todo lo descrito es arquitectura documental para futuras rondas.

### Idea central

Ojo de Dios debe evolucionar cuando descubre que falta una capacidad. Si durante una auditoría Mistral/LaIA detecta que no existe técnica, propiedad, parser, wrapper, plantilla, `evidence_schema` o soporte para una herramienta, CVE o protocolo, debe activar a Hermes Agent para construir esa capacidad en laboratorio.

El usuario no debe programarla manualmente. El flujo principal debe mantenerse no-code y supervisado: el usuario expresa el objetivo, Mistral/LaIA detecta la carencia, Hermes Agent construye en laboratorio, DeepSeek aporta inteligencia avanzada cuando haga falta y X5/OjoRouter ejecuta solo lo validado.

### Detección por Mistral

Mistral/LaIA puede detectar falta de capacidad cuando:

- X5 agota técnicas sin éxito;
- una herramienta falta o no está encapsulada;
- un CVE/servicio no tiene técnica registrada;
- una técnica no genera `evidence_schema` válido;
- falta parser para interpretar salida;
- falta campo/panel para una técnica;
- una PoC externa debe adaptarse al contrato Ojo de Dios.

La detección de carencia no autoriza improvisación ni ejecución fuera de contrato. Debe generar una petición estructurada, pausar el plan si corresponde y conservar contexto suficiente para reproducir el problema en laboratorio.

### Petición estructurada

Cuando detecta una carencia, Mistral/LaIA crea una petición para Hermes Agent con campos documentales como:

- `request_id`
- `source_module`
- `missing_capability_type`
- `target_context`
- `technical_goal`
- `known_errors`
- `cve_or_reference`
- `expected_files`
- `expected_evidence`
- `paused_plan_id` si aplica
- `approval_required`

La petición debe explicar qué falta, por qué bloquea o limita el plan, qué artefactos se esperan, qué evidencia demostraría éxito y qué aprobaciones son necesarias. Si la petición nace desde una auditoría en curso, debe vincularse al `paused_plan_id` para poder reanudar después de la validación.

### Trabajo de Hermes Agent

Hermes Agent recibe la petición y puede pedir lo necesario a DeepSeek/API, fuentes abiertas o configuración interna autorizada. Debe generar una pieza real de laboratorio, no texto suelto ni una explicación aislada.

Según el caso, debe producir:

- módulo completo;
- wrapper de herramienta;
- parser;
- evidence schema;
- panel fields;
- contrato `technique.json`;
- worker;
- README;
- `requirements.generated.txt`.

Todo el trabajo debe permanecer dentro de la arquitectura prevista:

```text
modules/laboratory/<technique_id>/
```

Hermes Agent no toca producción directamente, no registra técnicas como promovidas por sí mismo, no instala dependencias sin aprobación y no activa scoring general. Su salida debe volver al panel como estado, diff, archivos, logs, dependencias propuestas y evidencia de laboratorio cuando exista.

### DeepSeek como apoyo

DeepSeek puede apoyar a Hermes Agent en tareas de alta complejidad. Puede:

- investigar documentación o PoCs;
- diseñar lógica;
- revisar código;
- corregir errores;
- generar estructura completa;
- explicar dependencias;
- preparar informe de promoción.

DeepSeek no manda sobre producción. Su salida pasa por Hermes Agent y por el flujo de laboratorio: revisión, validación, sandbox, aprobación humana, promoción controlada y registro en AuditLog cuando corresponda. DeepSeek aporta inteligencia avanzada; no sustituye a X5/OjoRouter ni rompe la cadena de control.

### Validación

Hermes Agent debe ejecutar validaciones de laboratorio antes de proponer uso o promoción:

- validación de sintaxis;
- validación de contrato;
- validación de evidence schema;
- revisión de dependencias;
- prueba sandbox si el usuario lo aprueba.

Los logs deben registrarse en AuditLog y las evidencias válidas deben guardarse en EvidenceStore como evidencia de laboratorio. La validación no equivale a promoción productiva: solo demuestra que la pieza puede avanzar en el ciclo de vida si el usuario aprueba y las políticas lo permiten.

### Plan pausado

Si la capacidad nace por fallback, el plan original queda `paused`. Solo se reanuda cuando:

- la pieza está probada;
- usuario aprueba;
- técnica queda `promoted` o autorizada según modo;
- scope sigue vigente;
- X5/OjoRouter revalida Policy Engine y Kill Switch.

La reanudación debe reconstruirse desde estado persistente, no desde memoria volátil ni desde una conversación suelta. X5/OjoRouter debe verificar técnica, scope, estado de promoción/autorización, evidencias de laboratorio y AuditLog antes de continuar.

### Resultado en panel

El panel debe mostrar de forma clara:

- qué faltaba;
- qué creó Hermes Agent;
- archivos generados;
- dependencias;
- estado;
- pruebas;
- evidencias;
- siguiente acción sugerida por Mistral.

El usuario debe poder entender por qué se activó fallback, qué se construyó, qué riesgos existen, qué falta aprobar y si conviene reanudar el plan, revisar la técnica, instalar dependencias, ejecutar sandbox, promover o descartar.

### Regla final de fallback

El sistema aprende y se expande bajo supervisión: Mistral/LaIA detecta carencias, Hermes Agent las implementa en laboratorio, DeepSeek aporta inteligencia avanzada y X5/OjoRouter ejecuta solo lo validado. La autonomía no significa ejecución opaca; significa que Ojo de Dios puede avanzar desde intención a capacidad nueva sin exigir al usuario programar manualmente, manteniendo scope, evidencia, AuditLog, aprobación y Kill Switch.


## Cierre documental del Módulo 12

Esta sección cierra la especificación documental del Módulo 12. No implementa funcionalidad, no modifica `.env.example`, no crea carpetas, no toca base de datos, no crea endpoints, no modifica workers, no cambia requirements y no añade tests. Su función es ordenar la arquitectura final que deberá respetarse en rondas futuras.

### Cadena de autoridad final

La cadena de autoridad final del Módulo 12 queda definida sin contradicciones:

1. **Usuario** gobierna desde panel web o app. Aprueba, pausa, deniega, reanuda, promueve, rechaza o detiene.
2. **Policy Engine / Scope / Kill Switch** bloquean cualquier acción fuera de alcance, sin permiso, riesgosa o detenida por control superior.
3. **Mistral/LaIA** dirige la operación táctica y genera planes. Está integrado en cada módulo, entiende contexto activo, rellena parámetros, selecciona técnicas registradas y detecta capacidades faltantes.
4. **X5/OjoRouter** valida y ejecuta. Recibe planes, aplica Policy Engine, Scope, Kill Switch y TechniqueRegistry, y ejecuta solo mediante workers y runtimes autorizados.
5. **Hermes Agent** implementa capacidades faltantes en laboratorio. Trabaja en `modules/laboratory/`, genera artefactos, valida, prueba en sandbox y devuelve resultados; no toca producción directamente.
6. **DeepSeek** diseña, revisa y ordena tareas a Hermes Agent cuando el usuario lo pide. Es arquitecto operativo de laboratorio, no sustituto de Mistral/LaIA como cerebro táctico contextual.

Ningún agente salta Policy Engine, Scope, Kill Switch, AuditLog, EvidenceStore ni flujo de aprobación. Ningún agente toca producción sin promoción, registro, validación y autorización conforme a la cadena de control.

### Criterios de aceptación documental

Checklist documental del Módulo 12:

- [ ] Módulo 12 documenta autonomía supervisada real, no terminal manual como flujo principal.
- [ ] IA contextual aparece dentro de cada módulo/página.
- [ ] Mistral queda como cerebro táctico de planes y parámetros.
- [ ] X5 queda como validador/ejecutor.
- [ ] Hermes Agent queda como constructor de laboratorio.
- [ ] DeepSeek queda como arquitecto operativo, no sustituto de Mistral.
- [ ] Fallback de capacidades documentado: Mistral detecta, Hermes Agent implementa, DeepSeek aporta inteligencia.
- [ ] Redis se documenta solo como eventos en vivo.
- [ ] SQLite/AuditLog/EvidenceStore se documentan como persistencia.
- [ ] Dependencias generadas requieren aprobación.
- [ ] Sandbox, promoción, rollback y scoring están documentados.
- [ ] Android/app no tiene permisos superiores al panel.

### Estructura futura esperada

La estructura futura esperada se documenta como arquitectura prevista, no como implementación existente ni como carpetas creadas en esta ronda:

```text
app/ai/mistral/
app/ai/hermes_lab/
modules/laboratory/
modules/custom/
storage/evidence_store/
storage/audit_logs/
deepseek_chat_history
technique_registry
technique_scores
attack_plans
execution_results
```

Las rutas y nombres anteriores sirven como guía de diseño para futuras rondas. Cualquier implementación deberá verificar existencia real, crear migraciones o carpetas solo cuando una ronda lo solicite explícitamente, y mantener compatibilidad con roles, estados, aprobaciones, EvidenceStore, AuditLog y Kill Switch.

### App Android y módulos 13+

Android, iOS, Phishing, Cloud y Evidencia/Ops heredarán esta arquitectura. Cada módulo deberá tener página propia, LaIA contextual, acciones estructuradas, X5/OjoRouter para ejecución validada, Hermes Agent para capacidades faltantes y DeepSeek para laboratorio avanzado.

La app Android no tiene permisos superiores al panel. Debe respetar la misma cadena de autoridad: usuario, Policy Engine, Scope, Kill Switch, Mistral/LaIA, X5/OjoRouter, Hermes Agent, DeepSeek, EvidenceStore y AuditLog. Cualquier acción desde app deberá pasar por los mismos scopes, confirmaciones, bloqueos, eventos, evidencias y registros que una acción equivalente desde panel web.

### Herencia de orquestación para módulos actuales y futuros

El Módulo 12 define la arquitectura transversal de orquestación que heredarán los módulos actuales y futuros. Esta herencia aplica a:

- 13 Android;
- 13bis iOS;
- 14 Phishing;
- 15 Cloud/Containers/Kubernetes;
- 16 Evidencia/Ops/Calidad;
- futuros módulos 17 y 18, aunque aún no estén definidos.

Cada módulo futuro debe tener:

- página/panel propio;
- LaIA/Mistral contextual dentro del módulo;
- acciones no-code estructuradas;
- botón/flujo de plan revisable;
- X5/OjoRouter validando y ejecutando;
- Hermes Agent creando capacidades faltantes en laboratorio;
- DeepSeek como arquitecto/revisor avanzado;
- EvidenceStore, AuditLog, scoring, Policy Engine y Kill Switch.

Esta herencia no afirma que los módulos futuros, rutas futuras o integraciones futuras ya estén implementados. Define el contrato arquitectónico que deberán respetar cuando se documenten o implementen en rondas posteriores.

### Nota de cierre

Este documento no implementa funcionalidad. Es el bloque documental completo con extensión DeepSeek y herencia futura que guiará rondas posteriores de implementación del Módulo 12 y de los módulos que adopten su patrón de orquestación.

Cualquier implementación posterior deberá respetar roles, estados, scopes, aprobaciones, EvidenceStore, AuditLog y Kill Switch. También deberá preservar la filosofía todoterreno de autonomía supervisada: el usuario opera en no-code desde panel/app, Mistral/LaIA dirige planes, X5/OjoRouter ejecuta lo validado, Hermes Agent construye en laboratorio y DeepSeek aporta arquitectura avanzada bajo orden del usuario.
