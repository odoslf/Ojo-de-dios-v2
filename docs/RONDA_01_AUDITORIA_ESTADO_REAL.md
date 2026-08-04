# Ronda 1 — Auditoría de estado real

## Decisión de la ronda

Esta ronda no implementa técnicas, no instala herramientas externas y no crea stubs. Su objetivo es dejar un corte verificable del estado real del repositorio antes de avanzar a la Ronda 2. Todo lo marcado aquí debe tratarse como referencia de trabajo para las siguientes rondas.

## Comandos ejecutados

| Comando | Resultado | Uso en auditoría |
| --- | --- | --- |
| `git status --short` | Limpio al inicio de la ronda. | Confirmar que se trabaja sobre el mismo workspace sin cambios pendientes. |
| `find .. -name AGENTS.md -print` | Sin archivos `AGENTS.md` encontrados. | Confirmar que no hay instrucciones locales adicionales. |
| `python -m pip install -r requirements-dev.txt` | Correcto; instaló/alineó `pytest==8.3.4`, `httpx==0.28.1` y `httpcore==1.0.9`. | Preparar entorno de pruebas declarado por el repo. |
| `python -m pytest` | 387 passed, 4 failed, 4 warnings. | Baseline real de calidad de Ronda 1. |
| `rg --files -g '*.py' \| wc -l` | 222 archivos Python. | Tamaño aproximado de código. |
| `rg --files tests -g '*.py' \| wc -l` | 86 archivos de test. | Cobertura contractual existente. |
| `rg --files docs -g '*.md' \| wc -l` | 93 documentos Markdown. | Peso documental actual. |
| `find app/modules -maxdepth 2 -name module_manifest.json \| wc -l` | 20 manifiestos de módulo. | 16 oficiales + 4 reservados. |
| `rg --files app/templates -g '*.html' \| wc -l` | 6 templates HTML. | Superficie web actual. |
| `rg -n "@.*\\.get\|@.*\\.post\|APIRouter\|FastAPI" app` | Rutas FastAPI/API/web localizadas. | Mapa de entrada UI/API. |

## Resumen ejecutivo

El repositorio ya no es un chasis vacío: tiene aplicación FastAPI, rutas API, rutas web, modelos de target, repositorios, registry, módulos, workers, tests contractuales, EvidenceStore, ToolHealth, VersionLock, ScoringEngine, Kill Switch, Knowledge Base builder, Hermes/DeepSeek contracts y documentación estratégica amplia.

El estado real sigue siendo `lab core / chasis avanzado`, no aplicación 100% acabada. La suite revela que el objetivo principal de la siguiente fase técnica debe ser cerrar inconsistencias entre contratos de target/API/UI y la implementación actual antes de ampliar técnicas.

## Baseline de pruebas

Resultado de `python -m pytest` tras instalar dependencias de desarrollo declaradas:

- Total recogido: 391 tests.
- Correctos: 387.
- Fallidos: 4.
- Warnings: 4 de `starlette.templating` por firma de `TemplateResponse` deprecada.

### Fallos reales detectados

1. `tests/test_targets_api_contract.py::test_targets_api_create_read_list_plan_workspace_context_refresh_and_not_available_actions`
   - Espera que `POST /api/targets/{target_id}/start` devuelva `501`.
   - La implementación actual devuelve `200` y ejecuta `JobRunner` local in-process.
   - Esto no debe resolverse a ciegas: hay que decidir en Ronda 2 si el contrato de test está atrasado o si el endpoint se adelantó a una fase no cerrada.

2. `tests/test_targets_pages_routes.py::test_new_target_page_renders`
   - Espera que la página `/targets/new` incluya `/api/targets/create`.
   - El template actual usa formulario HTML a `/targets/new` y redirección a detalle.

3. `tests/test_targets_pages_templates_exist.py::test_new_target_template_contains_required_content`
   - Mismo desacople: el contrato exige mención a `/api/targets/create`, pero el template no la incluye.

4. `tests/test_targets_pages_templates_exist.py::test_detail_template_contains_disabled_actions`
   - Espera el texto `Planificar` en `app/templates/targets/detail.html`.
   - El detalle actual muestra `Plan JSON`, enlaces API y acciones deshabilitadas, pero no ese texto exacto.

### Warnings reales detectados

- Varias rutas de página usan `TemplateResponse(name, {"request": request})`; Starlette recomienda `TemplateResponse(request, name)`.
- No rompe la app ahora, pero debe limpiarse antes de release.

## Inventario real por zona

### 1. Aplicación web/API

Estado:

- Existe `app/main.py` con factory FastAPI y rutas raíz.
- Existen routers API de health, kill switch, módulos y targets.
- Existen páginas HTML para dashboard de módulos, detalle/workspace de módulos, nuevo objetivo y detalle de objetivo.

Gaps:

- La UI de targets y los tests contractuales no están alineados.
- Faltan vistas visuales dedicadas para evidencia, jobs, settings, IA, ToolHealth, VersionLock y reportes.
- La navegación ya enumera áreas futuras, pero varias aún llevan a anchors del dashboard o JSON, no a pantallas completas.

### 2. Targets, workspaces y planificación

Estado:

- Hay creación de target, fingerprint local, workspace por target, attack surface graph pasivo, service fingerprint report y planificación OjoRouter.
- `POST /api/targets/{target_id}/start` ya crea y completa jobs mediante `JobRunner` local.

Gaps:

- El contrato de tests aún espera que `start` no esté disponible; hay desacople de fase.
- Falta decisión explícita sobre si `start` queda dentro de Ronda 1-3 como ejecución real controlada o si se degrada temporalmente a `501` hasta cerrar cola/cancelación.
- Falta UI de job lifecycle y cancelación cooperativa real.

### 3. Módulos

Estado:

- Hay 20 manifiestos: 16 módulos oficiales y 4 módulos reservados.
- Los módulos oficiales tienen `readiness: documented` y `doc_path` hacia documentación técnica.
- M17-M20 están reservados y marcados como no oficiales, sin declararse funcionales.

Gaps:

- Los módulos están mayoritariamente documentados/catalogados, no cerrados como ejecución 100%.
- Falta convertir técnicas prioritarias en adapters reales con preflight, worker, evidence y UI de campos concretos.
- Debe mantenerse la regla de no registrar técnicas vacías genéricas.

### 4. Registry, contratos y runtime

Estado:

- Existen `TechniqueRegistry`, `TechniqueCatalog`, `ModuleCatalog`, `RuntimeRegistry`, loader/exporter/validator y tests contractuales.
- La política dinámica de registry evita depender de conteos fijos.

Gaps:

- Falta revisar en Ronda 2 si todos los contratos usados por tests reflejan el estado real más reciente.
- Falta promoción real desde Hermes/plugin hacia registry productivo con rollback.

### 5. Workers y ejecución

Estado:

- Hay workers por dominios: android, cloud, demo, docker, hackrf, hardware, hermes lab, ops, phishing, scraping, windows, wsl y base worker.
- Hay `JobRunner` y tests de dry_run/demo/kill switch/manual required.

Gaps:

- No todos los workers equivalen a ejecución real de herramienta externa.
- Hay que separar con claridad: demo fixture, dry_run, ejecución controlada y `IMPLEMENTACION_USUARIO_REQUERIDA`.
- Falta UI para ver cada run, artifacts, permisos y errores.

### 6. EvidenceStore, Scoring y calidad

Estado:

- Hay EvidenceStore, evidence repository, scoring engine/repository y tests de no fake success.
- Hay workspace artifacts con hash y contratos.

Gaps:

- Falta evidence center visual.
- Falta reporte final por objetivo/módulo/técnica.
- Falta timeline unificado de evidencia y jobs.

### 7. ToolHealth, VersionLock e instalación

Estado:

- Hay ToolInventory, ToolHealth, ToolInstallPlan, ToolInstallRunner, receipts, workspaces de instalación y VersionLock.
- La documentación insiste en que Codex no debe instalar herramientas externas del operador.

Gaps:

- Falta panel operativo de herramientas con estado por estación.
- Falta bloqueo visible por versiones no verificadas en flujos de ejecución.
- Falta first-run guiado final para Windows.

### 8. LaIA/Mistral, Knowledge Base y DeepSeekAssist

Estado:

- Hay contratos de schemas IA, healthcheck local LLM, Knowledge Base builder, context endpoints y Hermes/DeepSeek assist receipts/reviews.
- La documentación define RAG/local KB antes que fine-tuning.

Gaps:

- Falta demostrar arranque completo de Knowledge Bootstrap en una estación limpia.
- Falta panel de estado IA completo.
- Falta enforcement transversal: si KB está stale/failed, X5 debe degradar o bloquear planes IA según regla documental.

### 9. Hermes Agent Lab y promoción

Estado:

- Hay contratos y documentación amplia de Hermes Lab, proposals, DeepSeekAssist y pipelines.

Gaps:

- Falta implementar ciclo completo real: proposal → sandbox → tests → diff → revisión → aprobación → promoción → rollback.
- Falta aislamiento visible de workspaces Hermes y política de no tocar producción.

### 10. Seguridad operacional

Estado:

- Hay roles, permisos, policy engine, kill switch API/core y tests básicos.

Gaps:

- Falta auditoría transversal de bypasses.
- Falta aplicar permisos/roles de forma completa en UI y API.
- Falta audit log centralizado para acciones sensibles.

## Riesgos priorizados para Ronda 2

1. **Desacople tests vs implementación en targets.** Es el único motivo de fallo de la suite tras instalar dependencias.
2. **Start endpoint adelantado o contrato atrasado.** Hay que decidir si se conserva ejecución local `JobRunner` o se adapta a la expectativa `501` hasta cola/cancelación.
3. **UI de targets no sincronizada con contratos.** El formulario usa ruta HTML, los tests esperan referencia API.
4. **Warnings de TemplateResponse.** No bloquean, pero anticipan deuda técnica.
5. **Mucho documento y contrato, menos UI final.** El siguiente progreso visible debe alinear contratos con pantallas reales.

## Recomendación para la Ronda 2

Ronda 2 debe ser una limpieza de contradicciones concretas, empezando por targets:

1. Decidir contrato oficial de `POST /api/targets/{target_id}/start`.
2. Ajustar tests o implementación según la decisión, sin fingir ejecución.
3. Alinear `/targets/new` con `/api/targets/create` o documentar/mostrar ambos flujos: HTML humano y API Android-ready.
4. Añadir texto/acción `Planificar` real en detalle de objetivo si el contrato se mantiene.
5. Migrar `TemplateResponse` a la firma recomendada para eliminar warnings.
6. Reejecutar `python -m pytest` y dejar baseline verde o con fallos documentados si la decisión exige una ronda adicional.

## Cierre de Ronda 1

Ronda 1 queda cerrada como auditoría real si este documento se usa como entrada directa de Ronda 2. No se ha declarado ninguna funcionalidad nueva como terminada. No se han creado técnicas, payloads, conectores ficticios ni stubs.
