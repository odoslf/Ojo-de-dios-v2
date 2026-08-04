# Hoja de ruta de 10 rondas para cerrar Ojo de Dios funcional

## Estado real actual antes de sacar ZIP

### Funciona ya en código

1. **Arranque Windows desde ZIP de GitHub**
   - Descargar ZIP del repositorio en GitHub.
   - Extraer en Windows.
   - Ejecutar `scripts\windows\iniciar_ojo_de_dios_windows.bat`.
   - El BAT crea `.venv`, instala `requirements.txt`, crea `.env` desde `.env.example` si falta, prepara carpetas locales y arranca `uvicorn` en `http://127.0.0.1:8000/modules`.

2. **Centro M16**
   - Pantalla: `/ops/m16`.
   - Muestra readiness, manifiesto Windows, scripts requeridos, estado de conocimiento local y acciones seguras.
   - Puede guardar `storage/runtime/m16_readiness_status.json`.
   - Puede construir base de conocimiento `docs-only` sin llamadas externas.

3. **LaIA/Mistral local**
   - Modelo fijado: `CognitiveComputations/dolphin-mistral-nemo:12b`.
   - Instalación Windows preparada por `scripts\windows\ia\instalar_modulo16_completo.bat`.
   - Ollama/modelo no se guardan en el repo; se descargan en el PC del operador.
   - El prompt contractual está en `docs/ai_prompts/laia_mistral_system_prompt.md`.

4. **Hermes Agent Lab**
   - Workspace: `modules/laboratory`.
   - Scripts Windows preparados para workspace y healthcheck DeepSeek/Hermes.
   - Hermes no escribe producción directo; trabaja en laboratorio y requiere aprobación/promoción.
   - Prompt contractual: `docs/ai_prompts/angel_hermes_system_prompt.md`.

5. **Módulo 1 OSINT pasivo**
   - Pantalla: `/modules/m01_osint/passive-dns`.
   - API: `POST /api/modules/m01_osint/osint/domain-snapshot`.
   - Target-bound API: `POST /api/targets/{target_id}/m01/passive-dns`.
   - Resuelve DNS pasivo con registros `A`, `AAAA`, `MX`, `NS`, `TXT`, `CNAME`, `SOA`.
   - Guarda JSON de evidencia y reporte Markdown para targets.
   - No escanea puertos, no hace crawling, no fuerza subdominios.

6. **Catálogo y workspaces**
   - Los módulos oficiales están catalogados.
   - Hay workspaces por módulo, herramienta, técnica y target.
   - Hay EvidenceStore, ToolHealth, VersionLock, Scoring, runtime registry y targets.

7. **Exportador local opcional**
   - `scripts\windows\exportar_ojo_de_dios_zip.bat` existe, pero no es obligatorio si el operador descarga ZIP desde GitHub.
   - El flujo primario es GitHub ZIP + `iniciar_ojo_de_dios_windows.bat`.

### Falta para decir “100% funcional” sin exagerar

1. M01 necesita más fuentes pasivas reales además de DNS: WHOIS/RDAP, CT logs, robots/sitemap opcional, certificados y tecnología pasiva sin crawling agresivo.
2. El panel de targets necesita listar histórico de evidencias/reportes y permitir abrir reportes generados.
3. LaIA/Mistral necesita panel conversacional local con prompt aplicado, contexto del módulo, knowledge base y receipts visibles.
4. Hermes necesita flujo completo de propuestas: crear proposal, revisar, validar, aprobar, promocionar y rollback desde UI.
5. Falta un administrador visual de módulos/técnicas para que Hermes/operador añadan capacidades sin editar archivos a mano.
6. Falta instalador/healthcheck visual de herramientas por módulo con VersionLock real y receipts de instalación.
7. Falta cola de ejecución controlada desde UI para tareas permitidas, con Kill Switch visible y evidencia automática.
8. Falta centro de reportes por target, módulo, técnica y fecha.
9. Falta empaquetado/release final con comprobación “listo para Windows” ejecutable antes de publicar en GitHub.
10. Falta validación real en un PC Windows con Ollama, Mistral y DeepSeek configurados en `.env` local.

## Ronda 1 — Cierre Windows first-run

Objetivo: que el ZIP descargado de GitHub arranque en Windows de forma repetible.

Entregables:
- Mejorar `iniciar_ojo_de_dios_windows.bat` con preflight más detallado: Python, pip, permisos, puerto 8000, `.env`, dependencias.
- Crear estado `storage/runtime/windows_first_run_status.json` con cada paso.
- Añadir página `/ops/m16/first-run` o bloque ampliado en Centro M16.
- Añadir comprobación API de first-run.

Criterio de cierre:
- Un usuario extrae ZIP de GitHub, ejecuta un BAT y abre `/modules` sin tocar código.

## Ronda 2 — M01 OSINT pasivo completo

Objetivo: dejar M01 como primer módulo realmente usable.

Entregables:
- Añadir RDAP/WHOIS pasivo para dominios e IPs usando fuentes públicas documentadas.
- Añadir Certificate Transparency para dominios.
- Añadir análisis de SPF/DMARC/MX/NS más detallado.
- Añadir histórico de snapshots M01 por target.
- Añadir vista de reportes M01 en UI.

Criterio de cierre:
- Para un dominio propio/autorizado, M01 genera evidencia, reporte y lectura operativa sin escaneo activo.

## Ronda 3 — Centro de reportes y evidencias

Objetivo: que todo resultado real sea visible y navegable.

Entregables:
- Página `/reports`.
- Página `/targets/{target_id}/reports`.
- Lectura de JSON/Markdown generados.
- Filtros por módulo, target, fecha, estado.
- Hash/metadata visible por artifact.

Criterio de cierre:
- El operador puede encontrar, abrir y exportar cualquier evidencia generada.

## Ronda 4 — LaIA/Mistral operativo local

Objetivo: que Mistral interactúe con Ojo de Dios desde UI con reglas reales.

Entregables:
- Panel chat local LaIA usando Ollama `/api/chat`.
- Envío obligatorio del prompt contractual.
- Context pack por módulo/target.
- Knowledge base integrada.
- Receipts de cada respuesta.
- Modo JSON validado para acciones recomendadas.

Criterio de cierre:
- Mistral responde desde la app con contexto local y sin inventar ejecución.

## Ronda 5 — Hermes Agent Lab operativo

Objetivo: que Hermes cree propuestas controladas sin tocar producción.

Entregables:
- UI para crear proposal Hermes.
- Workspace por propuesta.
- Manifest obligatorio `PROMOTION_MANIFEST.json`.
- Validación estructural.
- Revisión LaIA/Mistral.
- Estado: draft, reviewed, rejected, approved, promoted.

Criterio de cierre:
- Hermes puede preparar una capacidad en laboratorio y dejarla lista para revisión humana.

## Ronda 6 — Instalación y salud de herramientas por módulo

Objetivo: que el operador sepa qué herramientas faltan y cómo instalarlas.

Entregables:
- Panel ToolHealth por módulo.
- Instalación controlada solo con aprobación.
- Receipts de instalación.
- VersionLock actualizado.
- Reintentos y errores visibles.

Criterio de cierre:
- Cada módulo muestra herramientas instaladas, faltantes, versión y estado real.

## Ronda 7 — Ejecución controlada y Kill Switch UI

Objetivo: ejecutar solo tareas permitidas con scope, confirmación y parada.

Entregables:
- Cola visual de jobs.
- Confirmación explícita por target/módulo/técnica.
- Kill Switch visible.
- Estados: queued, running, completed, failed, stopped.
- Logs y evidencia por run.

Criterio de cierre:
- Una tarea permitida puede iniciarse, seguirse, pararse y auditarse desde UI.

## Ronda 8 — Administrador de módulos y técnicas

Objetivo: que Hermes/operador añadan capacidades sin romper catálogo.

Entregables:
- UI para crear módulo reservado o técnica nueva en laboratorio.
- Validación de manifest.
- Generación de workspace.
- Revisión de conflictos.
- Promoción controlada.

Criterio de cierre:
- Se puede añadir una técnica nueva como proposal sin editar a mano producción.

## Ronda 9 — Integración M16 + M01 + targets como flujo guiado

Objetivo: flujo completo de operador desde objetivo hasta reporte.

Entregables:
- Wizard: crear target → elegir M01 → ejecutar DNS pasivo → ver reporte → preguntar a LaIA → guardar conclusiones.
- Context pack automático para Mistral.
- Evidencia enlazada al target.
- Estado final de target.

Criterio de cierre:
- Un operador nuevo puede completar un caso M01 entero desde UI.

## Ronda 10 — Release Windows validado

Objetivo: publicar una versión lista para PC Windows.

Entregables:
- Checklist automático `/ops/release`.
- Validación de GitHub ZIP.
- Validación en Windows real: Python, pip, Ollama, modelo, `.env`, Mistral, Hermes opcional.
- Documentación corta de usuario final.
- Tag/release versionado.

Criterio de cierre:
- El ZIP de GitHub puede instalarse y ejecutarse en Windows siguiendo una guía corta, con M01 operativo y M16 verificable.
