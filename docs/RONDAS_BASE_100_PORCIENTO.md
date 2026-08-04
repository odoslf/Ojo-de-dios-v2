# Lista base por rondas para acabar Ojo de Dios al 100%

## Propósito

Este documento deja una referencia operativa para avanzar por rondas sin instalar herramientas externas, sin crear código ficticio y sin fingir capacidades. La primera estación Windows, Ollama/Mistral, herramientas pesadas y material que dependa de máquina local del operador se harán fuera de Codex cuando toque; en este repositorio se deja el programa preparado, verificable y honesto.

Cada ronda debe acabar con código/documentación real, tests o checks aplicables, evidencia de estado y sin stubs marcados como funcionales.

## Estado actual por zonas de investigación

| Zona | Estado actual | Qué falta para 100% |
| --- | --- | --- |
| Producto y reglas maestras | Documentación estratégica amplia ya existe: plan maestro, handoff, definición de acabado, políticas de evidencia, extensibilidad, evolución Hermes/DeepSeek y reglas de Codex. | Convertir cada regla documental en contratos ejecutables, UI visible, checks automáticos y criterios de aceptación por módulo. |
| Módulos oficiales | Hay 16 módulos oficiales declarados y módulos reservados para expansión; los manifiestos existen y las rutas de documentación están fijadas. | Completar técnicas reales por módulo, paneles específicos, workers conectados, contratos de evidencia y estados honestos por técnica. |
| Registry y contratos | Existen piezas base de registry, catálogo de técnicas, módulos, permisos, runtime y validadores. | Endurecer validación dinámica, exportaciones, recarga controlada, compatibilidad de plugins y promoción Hermes sin tocar muchos archivos. |
| X5/OjoRouter | Existe base de router, policy engine, strategy engine, job runner y estados. | Completar planificación multi-paso, scope enforcement, allowlists, degradación por readiness, kill switch global y trazabilidad completa. |
| LaIA/Mistral | Hay schemas, contratos y documentación de Knowledge Base/RAG. | Implementar bootstrap real de conocimiento, context packs, estado IA en panel, validación JSON, memoria/scoring y degradación si la KB no está lista. |
| DeepSeekAssist | Está definido como consulta externa opcional, sanitizada y de mínimo contexto. | Implementar cliente configurable, redacción de secretos, budget/cost guard, auditoría y fallback sin convertirlo en cerebro principal. |
| Hermes Agent Lab | Hay doctrina de sandbox, proposals, promoción y lifecycle. | Implementar proposals reales, workspace aislado, tests automáticos, diff review, aprobación del usuario, Promotion Pipeline y rollback. |
| EvidenceStore y scoring | Existen contratos y clases base para evidencia, scoring y resúmenes. | Cubrir todos los workers/técnicas, adjuntos, hashes, redacción, timeline, reportes exportables y aprendizaje operativo por resultado. |
| Tooling, VersionLock y ToolHealth | Hay inventario, planes de instalación, receipts, health y version lock. | Convertirlo en panel de estado, comprobaciones por herramienta, instrucciones de instalación por estación, bloqueo por versiones no verificadas y actualización segura. |
| Panel web y API | Existe aplicación web, rutas de módulos/targets y tests de arranque. | Completar UX responsive: Nuevo objetivo, dashboard, ficha de técnica, jobs en tiempo real, evidencia, IA, settings, Android-ready API y auth/roles visibles. |
| Workers y ejecución | Hay workers por áreas y job runner base. | Sustituir demo fixtures por conectores reales donde sea seguro, mantener dry_run/demo, aislar lógica sensible en IMPLEMENTACION_USUARIO_REQUERIDA y no simular éxito. |
| Primera estación Windows | Hay scripts y contratos de preparación Windows/IA. | Pulir first-run, prechecks, instalación guiada por usuario, healthcheck local, Knowledge Bootstrap inicial y diagnóstico reproducible. |
| Seguridad operacional | Hay kill switch, permisos, roles, políticas y límites. | Hacer enforcement transversal en UI/API/workers, audit log, secretos, scopes, aprobaciones, safe cleanup y pruebas de no bypass. |
| Calidad y release | Hay muchas pruebas contractuales. | Completar cobertura por invariantes, smoke E2E, migraciones, empaquetado, backup/restore, release manifest y documentación de operación diaria. |

## Lista base de lo que falta para considerar la aplicación acabada

1. Chasis web/API estable, responsive y probado.
2. Flujo completo de Nuevo objetivo hasta evidencia final.
3. Registry dinámico con técnicas reales y contratos estrictos.
4. Panel por módulo y panel por técnica con campos concretos.
5. Workers conectados a herramientas o a puntos explícitos `IMPLEMENTACION_USUARIO_REQUERIDA`.
6. Modos `demo`, `dry_run`, `controlled` y `expert` aplicados de verdad.
7. Scope, allowlist, permisos, kill switch y audit log en todo el ciclo.
8. EvidenceStore con hashes, adjuntos, timeline, redacción y exportación.
9. ScoringEngine alimentado por resultados reales.
10. ToolHealth y VersionLock visibles, bloqueantes cuando corresponda.
11. Knowledge Base local de LaIA/Mistral con refresco y panel de estado.
12. JSON schemas y validadores para toda salida IA operativa.
13. X5/OjoRouter con planificación multi-paso y degradación segura.
14. Hermes Lab con sandbox, proposals, tests, review y promoción aprobada.
15. DeepSeekAssist opcional, sanitizado, auditable y con control de coste.
16. Primera estación Windows preparada sin que Codex instale herramientas externas.
17. Reportes finales por objetivo, módulo, técnica y evidencia.
18. API Android-ready documentada y estable.
19. Auth, roles y permisos completos para operación local.
20. Backups, migraciones, export/import y release manifest.
21. Tests funcionales suficientes sin conteos fijos frágiles.
22. Documentación de usuario, operador y mantenimiento alineada con el código real.

## Plan base de 50 rondas

### Ronda 1 — Auditoría de estado real
Revisar código, tests, módulos, docs y manifiestos. Entregable: informe de gaps real por zona, sin tocar lógica funcional salvo correcciones menores necesarias.

### Ronda 2 — Limpieza de contradicciones documentales
Alinear README, plan maestro, handoff y roadmap para que todos apunten al mismo estado y a la misma secuencia.

### Ronda 3 — Baseline de tests y arranque
Ejecutar test suite, identificar fallos reales, fijar comandos oficiales y separar fallos de entorno de fallos de código.

### Ronda 4 — Modelo de configuración y secretos
Cerrar settings, `.env` esperado, redacción de secretos, rutas locales y validación de configuración.

### Ronda 5 — Base de datos y migraciones
Revisar SQLite primero, repositorios, migraciones futuras y contratos de persistencia.

### Ronda 6 — Target model y Nuevo objetivo
Completar flujo de creación de objetivo, fingerprint inicial, scope, autorización y workspace.

### Ronda 7 — UI Nuevo objetivo
Hacer la pantalla inicial usable, responsive y conectada a validación real.

### Ronda 8 — Dashboard operativo
Mostrar objetivos, jobs, módulos, readiness, alertas, kill switch y estado IA/herramientas.

### Ronda 9 — Registry dinámico v1
Endurecer carga, validación, unicidad, estados, permisos, schemas y export JSON/YAML.

### Ronda 10 — Contrato de técnica definitivo
Asegurar que cada técnica tenga campos, worker, evidence contract, permisos, modo y readiness honestos.

### Ronda 11 — Panel de técnica genérico pero real
Crear vista reutilizable basada en contratos sin inventar capacidades; renderiza campos reales y estados reales.

### Ronda 12 — Workers base y ciclo de job
Completar creación, cola local, ejecución, cancelación, errores, timeout, resumen y persistencia.

### Ronda 13 — Kill switch transversal
Aplicar kill switch en UI, API, job runner y workers antes de cualquier acción.

### Ronda 14 — PolicyEngine y permisos
Endurecer scope, allowlist, execution mode, roles, aprobaciones y bloqueos por módulo/técnica.

### Ronda 15 — EvidenceStore v1 completo
Guardar evidencia estructurada, adjuntos, hashes, origen, timestamps, redacción y relación con jobs.

### Ronda 16 — ToolRun lifecycle
Registrar intentos, comandos permitidos, receipts, salidas resumidas, errores y no-fake-success.

### Ronda 17 — ToolInventory y ToolHealth panel
Mostrar herramientas esperadas, detectadas, ausentes, versión, salud y acción manual requerida.

### Ronda 18 — VersionLock operativo
Bloquear o advertir por versiones no aprobadas, registrar lockfiles y preparar actualización segura.

### Ronda 19 — Demo mode honesto
Asegurar fixtures de demo separados de ejecución real y etiquetados visualmente como demo.

### Ronda 20 — Dry-run operativo
Simular planes y validaciones sin ejecutar herramientas, con evidencia de plan y razones de bloqueo.

### Ronda 21 — Módulos 1-4 mínimos reales
OSINT, Vulnerabilidades, Servicios de red y Web: paneles, campos, workers seguros, evidencia y docs.

### Ronda 22 — Módulos 5-8 mínimos reales
Credenciales, MITM/Red, Post-explotación y DoS/Resiliencia: contratos, límites, evidence y puntos de usuario donde aplique.

### Ronda 23 — Módulo 9 Scraping X4/X5
Conectar flujo de scraping inteligente, normalización, fuentes, exportación y evidence sin perder que X4 es conector.

### Ronda 24 — Módulos 10-13 mínimos reales
Wireless/RF general, IoT/físicos, Orquestación y Android: campos específicos, workers, límites y evidencia.

### Ronda 25 — Módulos 14-16 mínimos reales
Campañas autorizadas, Cloud/Containers/Kubernetes y Ops/Quality: workflows, reportes y readiness.

### Ronda 26 — Módulos reservados 17-20
Mantenerlos como reservados honestos o elevarlos solo con definición del usuario y contratos completos.

### Ronda 27 — Attack Surface Graph
Persistir relaciones entre target, servicios, tecnologías, hallazgos, CVEs, técnicas y evidencia.

### Ronda 28 — Service Intelligence Graph
Añadir fingerprints de servicios, priorización, historial y recomendaciones justificadas.

### Ronda 29 — ScoringEngine v1
Calcular severidad/prioridad/confianza con explicación, evidence links y aprendizaje local.

### Ronda 30 — Reportes exportables
Generar reportes por objetivo y módulo en formatos operativos, con anexos de evidencia y redacción.

### Ronda 31 — LaIA schemas operativos
Completar schemas JSON para explicación, rellenado de campos, plan, revisión de evidencia y next steps.

### Ronda 32 — LaIA Knowledge Bootstrap
Implementar carga local de conocimiento del repo, registry, docs, tools y estado runtime.

### Ronda 33 — RAG/context packs
Crear packs pequeños por módulo/técnica para que Mistral no dependa de prompts gigantes.

### Ronda 34 — Panel de estado IA
Mostrar Ollama/Mistral, embeddings si existen, KB status, freshness, schemas y degradación.

### Ronda 35 — X5/OjoRouter planificación v1
Planificar multi-paso con validación previa, permisos, scopes, readiness y evidence esperada.

### Ronda 36 — X5 ejecución controlada
Ejecutar solo acciones aprobadas por contrato, con rollback/cancelación cuando aplique.

### Ronda 37 — DeepSeekAssist cliente opcional
Implementar consulta externa sanitizada, mínimo contexto, sin secretos, con budget y audit log.

### Ronda 38 — AI Research Gates
Aplicar puertas de investigación antes de aceptar recomendaciones externas o nuevas técnicas.

### Ronda 39 — Hermes proposals
Crear modelo real de proposals, workspace, metadata, riesgos, tests requeridos y diff.

### Ronda 40 — Hermes sandbox
Ejecutar pruebas estructurales aisladas de proposals sin tocar producción ni autoaprobar.

### Ronda 41 — Promotion Pipeline
Promocionar proposals solo con aprobación, VersionLock, registry reload, tests y rollback.

### Ronda 42 — Plugin manager
Activar contratos de plugins, entry points, compatibilidad, aislamiento y panel de plugins.

### Ronda 43 — Tool Adoption Pipeline
Adoptar herramientas nuevas con quarantine, análisis, sandbox, health, version lock y docs.

### Ronda 44 — CVE-to-Technique Pipeline
Convertir CVE intelligence en propuestas de técnica/actualización sin ejecución automática.

### Ronda 45 — Primera estación Windows
Pulir scripts de preparación, prechecks, mensajes, healthcheck y guía para que el usuario instale lo externo.

### Ronda 46 — API Android-ready
Documentar y estabilizar endpoints, auth, target/job/evidence views y contratos para app móvil futura.

### Ronda 47 — Seguridad, auditoría y hardening
Revisar secretos, permisos, logs, redacción, bypasses, scopes, cleanup y operaciones peligrosas.

### Ronda 48 — E2E por flujo principal
Probar de Nuevo objetivo a reporte final en demo/dry_run y en controlled seguro donde exista herramienta real.

### Ronda 49 — Documentación de operador
Crear guía final: instalación, primera estación, uso diario, troubleshooting, backups, actualización y límites.

### Ronda 50 — Release 100% verificable
Congelar release manifest, ejecutar suite completa, revisar criterios de acabado, etiquetar versión y dejar checklist de mantenimiento.

## Regla para pedir la siguiente ronda

Cuando se pida una ronda concreta, se trabajará solo en esa ronda, en el mismo workspace, con código real o documentación normativa real según corresponda. Si una ronda descubre que falta una precondición, se documentará el bloqueo y se corregirá antes de avanzar, sin inventar funcionalidad.
