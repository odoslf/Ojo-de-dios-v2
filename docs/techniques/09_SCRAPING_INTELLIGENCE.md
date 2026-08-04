# MÓDULO 9 — SCRAPING INTELIGENTE X4 + X5 + IA

Catálogo declarativo. Sin código, comandos, scripts, tests, requirements, credenciales reales, scraping fuera de scope, bypass operativo ni pasos de ejecución.

module_id: scraping_intelligence
panel: Scraping
status_default: IMPLEMENTACION_USUARIO_REQUERIDA
docker_allowed: false
runtime_preferente: windows_python + wsl2_kali
install_profile: kali-linux-large_or_toolhealth
toolhealth: check_binary_and_version
versionlock: resolve_real_version_in_environment
storage: SQLite, CSV, JSON, EvidenceStore
workers: ScrapingWorker, SchedulerWorker, X5Worker, WSLWorker, PythonToolWorker, BrowserWorker, EvidenceWorker, AIWorker

## Regla operativa del módulo

Ojo de Dios centraliza panel, chat, scheduler, SQLite y evidence.
Mistral/LaIA traduce lenguaje natural a plan de scraping, analiza datos y propone técnica.
X5 ejecuta 47 técnicas propias + wrappers Kali, puntúa resultados y reinyecta aprendizaje.
Hermes crea wrappers, parsers, schemas, fixtures y panel_fields en sandbox si falta pieza.
X4/Cantera IQ queda separado; solo puede recibir exportaciones CSV/JSON si el usuario lo decide.
Lógica privada X5 queda marcada como IMPLEMENTACION_USUARIO_REQUERIDA.

## Campos comunes

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
scope_required: true
rate_limit_profile_required: true
storage_profile_required: true
notes: catalog_only,user_logic_required,no_commands_in_docs

## Hook común

app/modules/scraping_intelligence/<id_sin_scraping>.py::<ClasePascal>Technique.execute

## PARTE 1/3 — PANEL, PLANIFICACIÓN, CRAWLERS Y URL HISTORY

Regla:
Catálogo declarativo para panel, workers, adapters, hooks, evidence, almacenamiento y estados.
Sin comandos, parámetros operativos, scraping fuera de scope, credenciales reales, bypass funcional ni pasos operativos.

## Panel Scraping

sections: chat_mistral, recurring_scraping_config, data_viewer, quick_analysis, export_csv_json, task_manager
api_routes: /api/scraping/chat, /api/scraping/tasks, /api/scraping/tables, /api/scraping/export
db_tables: scraping_tasks, scraping_runs, scraping_results, scraping_messages, scraping_alerts, scraping_scores
evidence: scraping_plan, extracted_rows, run_log, export_reference, normalized_json

## Submódulo 9.1 — Chat Mistral + plan táctico

### Técnicas

#### 1. scraping.ai.natural_language_plan

tool: Dolphin Mistral Nemo 12B
runtime: local_ai
worker: AIWorker
adapter: ScrapingPlanAdapter
evidence: plan_json
hook: app/modules/scraping_intelligence/ai_natural_language_plan.py::AiNaturalLanguagePlanTechnique.execute

#### 2. scraping.ai.table_analysis

tool: Dolphin Mistral Nemo 12B
runtime: local_ai
worker: AIWorker
adapter: ScrapingAnalysisAdapter
evidence: analysis_json
hook: app/modules/scraping_intelligence/ai_table_analysis.py::AiTableAnalysisTechnique.execute

#### 3. scraping.scheduler.recurring_task

tool: internal scheduler
runtime: python_lib
worker: SchedulerWorker
adapter: ScrapingSchedulerAdapter
evidence: task_state
hook: app/modules/scraping_intelligence/scheduler_recurring_task.py::SchedulerRecurringTaskTechnique.execute

#### 4. scraping.storage.sqlite_table_writer

tool: SQLite
runtime: internal
worker: PythonToolWorker
adapter: SQLiteScrapingAdapter
evidence: sqlite_rows
hook: app/modules/scraping_intelligence/storage_sqlite_table_writer.py::StorageSqliteTableWriterTechnique.execute

## Submódulo 9.2 — Crawlers Kali/WSL2

evidence: discovered_urls, crawl_summary, raw_output_path, normalized_json
graph: TargetNode, URLNode, EndpointNode, EvidenceNode

### Técnicas

#### 5. scraping.crawler.katana

tool: Katana
version: v1.6.1
runtime: wsl2
worker: WSLWorker
adapter: KatanaAdapter
hook: app/modules/scraping_intelligence/crawler_katana.py::CrawlerKatanaTechnique.execute

#### 6. scraping.crawler.hakrawler

tool: Hakrawler
version: 2.1
runtime: wsl2
worker: WSLWorker
adapter: HakrawlerAdapter
hook: app/modules/scraping_intelligence/crawler_hakrawler.py::CrawlerHakrawlerTechnique.execute

#### 7. scraping.crawler.gospider

tool: Gospider
version: v1.1.6
runtime: wsl2
worker: WSLWorker
adapter: GospiderAdapter
hook: app/modules/scraping_intelligence/crawler_gospider.py::CrawlerGospiderTechnique.execute

#### 8. scraping.crawler.cariddi

tool: Cariddi
version: v1.4.6
runtime: wsl2
worker: WSLWorker
adapter: CariddiAdapter
hook: app/modules/scraping_intelligence/crawler_cariddi.py::CrawlerCariddiTechnique.execute

## Submódulo 9.3 — URLs históricas

evidence: historical_urls, source_provider_summary, raw_output_path, normalized_json
graph: DomainNode, URLNode, ArchiveNode, EvidenceNode

### Técnicas

#### 9. scraping.history.gau

tool: Gau
version: v2.2.4
runtime: wsl2
worker: WSLWorker
adapter: GauAdapter
hook: app/modules/scraping_intelligence/history_gau.py::HistoryGauTechnique.execute

#### 10. scraping.history.waybackurls

tool: Waybackurls
version: v0.1.0
runtime: wsl2
worker: WSLWorker
adapter: WaybackurlsAdapter
hook: app/modules/scraping_intelligence/history_waybackurls.py::HistoryWaybackurlsTechnique.execute

## Estado documental de la parte 1

Módulo 9 — Scraping Inteligente X4 + X5 + IA queda iniciado como catálogo técnico declarativo para panel, chat, scheduler, SQLite, exportaciones, workers, adapters, hooks, evidence y estado de implementación.
Las 10 técnicas de la parte 1 quedan marcadas como IMPLEMENTACION_USUARIO_REQUERIDA.
Todas las técnicas requieren scope, rate limit profile, storage profile, validación de worker y evidence útil antes de cualquier implementación futura del usuario.
Ojo de Dios centraliza panel, chat, scheduler, SQLite y evidence.
Mistral/LaIA solo traduce lenguaje natural a plan de scraping, analiza datos y propone técnica.
X5 mantiene su lógica privada como IMPLEMENTACION_USUARIO_REQUERIDA, puntúa resultados y reinyecta aprendizaje cuando exista implementación autorizada.
Hermes solo crea wrappers, parsers, schemas, fixtures o panel_fields en sandbox si falta una pieza.
X4/Cantera IQ permanece separado y solo recibe exportaciones CSV/JSON si el usuario lo decide.

## PARTE 2/3 — BROWSER, SCRAPING AVANZADO, OSINT Y EVASIÓN

Regla común:
Todas las técnicas mantienen status IMPLEMENTACION_USUARIO_REQUERIDA, docker:false, scope_required:true, rate_limit_profile_required:true, storage_profile_required:true, toolhealth:check_binary_and_version, versionlock:true, notes:catalog_only,user_logic_required,no_commands_in_docs.
Si falta conocer nombres reales del motor privado X4/X5, anotar: X4_X5_CODE_REFERENCE_REQUIRED=true.
No se inventan clases, funciones ni técnicas internas de X5.

Hook común:
app/modules/scraping_intelligence/<id_sin_scraping>.py::<ClasePascal>Technique.execute

Regla:
Catálogo declarativo para browser, scraping avanzado, extractores OSINT, antibloqueo, lectura visual controlada, workers, adapters, hooks, evidence y estados.
Sin comandos, parámetros operativos, credenciales reales, bypass funcional, resolución automática de CAPTCHA ni pasos operativos.

## Submódulo 9.4 — Scraping avanzado

evidence: extracted_rows, selector_summary, api_detection_summary, raw_output_path, normalized_json
graph: TargetNode, PageNode, SelectorNode, APIEndpointNode, EvidenceNode

### Técnicas

#### 11. scraping.advanced.scrapy

tool: Scrapy
version: 2.16.0
runtime: python_lib_or_wsl2
worker: ScrapingWorker
adapter: ScrapyAdapter
hook: app/modules/scraping_intelligence/advanced_scrapy.py::AdvancedScrapyTechnique.execute

#### 12. scraping.advanced.playwright

tool: Playwright
version: 1.60.0
runtime: windows_python_or_wsl2
worker: BrowserWorker
adapter: PlaywrightAdapter
hook: app/modules/scraping_intelligence/advanced_playwright.py::AdvancedPlaywrightTechnique.execute

#### 13. scraping.advanced.playwright_stealth

tool: playwright-stealth
version: latest-release-lock
runtime: python_lib
worker: BrowserWorker
adapter: PlaywrightStealthAdapter
hook: app/modules/scraping_intelligence/advanced_playwright_stealth.py::AdvancedPlaywrightStealthTechnique.execute

#### 14. scraping.advanced.selenium

tool: Selenium
version: latest-release-lock
runtime: windows_python
worker: BrowserWorker
adapter: SeleniumAdapter
hook: app/modules/scraping_intelligence/advanced_selenium.py::AdvancedSeleniumTechnique.execute

#### 15. scraping.advanced.undetected_chromedriver

tool: undetected-chromedriver
version: latest-release-lock
runtime: windows_python
worker: BrowserWorker
adapter: UndetectedChromeAdapter
hook: app/modules/scraping_intelligence/advanced_undetected_chromedriver.py::AdvancedUndetectedChromedriverTechnique.execute

#### 16. scraping.advanced.api_requests

tool: Python requests/httpx
version: latest-release-lock
worker: PythonToolWorker
adapter: ApiRequestsAdapter
hook: app/modules/scraping_intelligence/advanced_api_requests.py::AdvancedApiRequestsTechnique.execute

#### 17. scraping.advanced.rss_atom

tool: feedparser/httpx
version: latest-release-lock
worker: PythonToolWorker
adapter: RssAtomAdapter
hook: app/modules/scraping_intelligence/advanced_rss_atom.py::AdvancedRssAtomTechnique.execute

#### 18. scraping.advanced.internal_x5_technique

tool: X5 private engine
version: private_reference
worker: X5Worker
adapter: X5PrivateTechniqueAdapter
hook: app/modules/scraping_intelligence/advanced_internal_x5_technique.py::AdvancedInternalX5Technique.execute
notes_extra: X4_X5_CODE_REFERENCE_REQUIRED=true, no_internal_x5_names_in_docs=true

## Submódulo 9.5 — Extractores OSINT Kali

evidence: extracted_entities, metadata_summary, source_summary, raw_output_path, normalized_json
graph: DomainNode, EmailNode, PersonNode, MetadataNode, EvidenceNode

### Técnicas

#### 19. scraping.osint.metagoofil

tool: Metagoofil
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
adapter: MetagoofilAdapter
hook: app/modules/scraping_intelligence/osint_metagoofil.py::OsintMetagoofilTechnique.execute

#### 20. scraping.osint.theharvester

tool: theHarvester
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
adapter: TheHarvesterAdapter
hook: app/modules/scraping_intelligence/osint_theharvester.py::OsintTheharvesterTechnique.execute

#### 21. scraping.osint.spiderfoot

tool: SpiderFoot
version: latest-release-lock
runtime: wsl2_or_local_service
worker: WSLWorker
adapter: SpiderFootAdapter
hook: app/modules/scraping_intelligence/osint_spiderfoot.py::OsintSpiderfootTechnique.execute

#### 22. scraping.osint.recon_ng

tool: Recon-ng
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
adapter: ReconNgAdapter
hook: app/modules/scraping_intelligence/osint_recon_ng.py::OsintReconNgTechnique.execute

## Submódulo 9.6 — Antibloqueo y lectura visual controlada

evidence: block_detection_summary, proxy_route_summary, captcha_or_ocr_summary, raw_output_path, normalized_json
graph: TargetNode, BlockNode, ProxyNode, OCRNode, EvidenceNode

### Técnicas

#### 23. scraping.evasion.tor_profile

tool: Tor
version: system_package
runtime: wsl2
worker: WSLWorker
adapter: TorProfileAdapter
hook: app/modules/scraping_intelligence/evasion_tor_profile.py::EvasionTorProfileTechnique.execute

#### 24. scraping.evasion.proxychains_profile

tool: proxychains
version: system_package
runtime: wsl2
worker: WSLWorker
adapter: ProxychainsAdapter
hook: app/modules/scraping_intelligence/evasion_proxychains_profile.py::EvasionProxychainsProfileTechnique.execute

#### 25. scraping.evasion.tesseract_ocr

tool: Tesseract OCR
version: system_package
runtime: wsl2_or_windows
worker: PythonToolWorker
adapter: TesseractOCRAdapter
hook: app/modules/scraping_intelligence/evasion_tesseract_ocr.py::EvasionTesseractOcrTechnique.execute

#### 26. scraping.evasion.mistral_captcha_assist

tool: Mistral vision/text assist
version: local_ai
worker: AIWorker
adapter: CaptchaAssistAdapter
hook: app/modules/scraping_intelligence/evasion_mistral_captcha_assist.py::EvasionMistralCaptchaAssistTechnique.execute
notes_extra: human_review_required=true

#### 27. scraping.evasion.block_fallback_decider

tool: Mistral + X5 scoring
version: internal
worker: AIWorker
adapter: ScrapingFallbackAdapter
hook: app/modules/scraping_intelligence/evasion_block_fallback_decider.py::EvasionBlockFallbackDeciderTechnique.execute

#### 28. scraping.evasion.rate_limit_controller

tool: internal controller
version: internal
worker: ScrapingWorker
adapter: RateLimitAdapter
hook: app/modules/scraping_intelligence/evasion_rate_limit_controller.py::EvasionRateLimitControllerTechnique.execute

## Estado documental de la parte 2

Módulo 9 — Scraping Inteligente X4 + X5 + IA amplía el catálogo técnico declarativo con browser automation, scraping avanzado, extractores OSINT, antibloqueo y lectura visual controlada.
Las técnicas 11 a 28 quedan marcadas como IMPLEMENTACION_USUARIO_REQUERIDA.
Todas las técnicas de la parte 2 mantienen docker:false, scope requerido, rate limit profile, storage profile, toolhealth, versionlock y ausencia de comandos en documentación.
Si falta conocer nombres reales del motor privado X4/X5, queda marcado X4_X5_CODE_REFERENCE_REQUIRED=true y no se documentan clases, funciones ni técnicas internas de X5 inventadas.
Mistral/LaIA solo traduce lenguaje natural a plan de scraping, analiza datos y propone técnica.
X5 mantiene su lógica privada como IMPLEMENTACION_USUARIO_REQUERIDA, puntúa resultados y reinyecta aprendizaje cuando exista implementación autorizada.
Hermes solo crea wrappers, parsers, schemas, fixtures o panel_fields en sandbox si falta una pieza.
X4/Cantera IQ permanece separado y solo recibe exportaciones CSV/JSON si el usuario lo decide.

## PARTE 3/3 — SQLITE, SCHEDULER, SCORING Y EXPORTACIÓN

Regla común:
Todas las técnicas mantienen status IMPLEMENTACION_USUARIO_REQUERIDA, docker:false, storage_profile_required:true, toolhealth:check_binary_and_version, versionlock:true, notes:catalog_only,user_logic_required,no_commands_in_docs.
Si falta código real X4/X5: X4_X5_CODE_REFERENCE_REQUIRED=true.

Hook común:
app/modules/scraping_intelligence/<id_sin_scraping>.py::<ClasePascal>Technique.execute

Regla:
Catálogo declarativo para persistencia SQLite, scheduler recurrente, scoring X5, exportación, análisis, workers, adapters, hooks, evidence y estados.
Sin comandos, scripts funcionales, credenciales reales, scraping fuera de scope, nombres internos inventados de X5 ni pasos operativos.

## Submódulo 9.7 — Persistencia SQLite

evidence: sqlite_table_summary, inserted_rows_summary, schema_change_summary, normalized_json
graph: DataTableNode, ScrapingRunNode, EvidenceNode

### Técnicas

#### 29. scraping.sqlite.create_table

tool: SQLite
version: internal
worker: PythonToolWorker
adapter: SQLiteSchemaAdapter
hook: app/modules/scraping_intelligence/sqlite_create_table.py::SqliteCreateTableTechnique.execute

#### 30. scraping.sqlite.insert_rows

tool: SQLite
version: internal
worker: PythonToolWorker
adapter: SQLiteInsertAdapter
hook: app/modules/scraping_intelligence/sqlite_insert_rows.py::SqliteInsertRowsTechnique.execute

#### 31. scraping.sqlite.table_manager

tool: SQLite
version: internal
worker: PythonToolWorker
adapter: SQLiteTableManagerAdapter
hook: app/modules/scraping_intelligence/sqlite_table_manager.py::SqliteTableManagerTechnique.execute

#### 32. scraping.sqlite.query_for_analysis

tool: SQLite
version: internal
worker: PythonToolWorker
adapter: SQLiteQueryAdapter
hook: app/modules/scraping_intelligence/sqlite_query_for_analysis.py::SqliteQueryForAnalysisTechnique.execute

## Submódulo 9.8 — Scheduler recurrente

evidence: scheduled_task_summary, run_history_summary, alert_summary, normalized_json
graph: ScheduleNode, ScrapingRunNode, AlertNode, EvidenceNode

### Técnicas

#### 33. scraping.scheduler.create_task

tool: internal scheduler
version: internal
worker: SchedulerWorker
adapter: ScrapingSchedulerAdapter
hook: app/modules/scraping_intelligence/scheduler_create_task.py::SchedulerCreateTaskTechnique.execute

#### 34. scraping.scheduler.edit_task

tool: internal scheduler
version: internal
worker: SchedulerWorker
adapter: ScrapingSchedulerAdapter
hook: app/modules/scraping_intelligence/scheduler_edit_task.py::SchedulerEditTaskTechnique.execute

#### 35. scraping.scheduler.cancel_task

tool: internal scheduler
version: internal
worker: SchedulerWorker
adapter: ScrapingSchedulerAdapter
hook: app/modules/scraping_intelligence/scheduler_cancel_task.py::SchedulerCancelTaskTechnique.execute

#### 36. scraping.scheduler.alert_condition

tool: Mistral + SQLite
version: local_ai
worker: AIWorker
adapter: AlertConditionAdapter
hook: app/modules/scraping_intelligence/scheduler_alert_condition.py::SchedulerAlertConditionTechnique.execute

## Submódulo 9.9 — Scoring X5 y aprendizaje

evidence: technique_score_summary, fallback_decision_summary, source_learning_summary, normalized_json
graph: TechniqueNode, ScoreNode, SourceNode, EvidenceNode

### Técnicas

#### 37. scraping.x5.score_update

tool: X5 scoring
version: private_reference
worker: X5Worker
adapter: X5ScoringAdapter
hook: app/modules/scraping_intelligence/x5_score_update.py::X5ScoreUpdateTechnique.execute
notes_extra: X4_X5_CODE_REFERENCE_REQUIRED=true

#### 38. scraping.x5.best_technique_selector

tool: X5 strategy
version: private_reference
worker: X5Worker
adapter: X5SelectorAdapter
hook: app/modules/scraping_intelligence/x5_best_technique_selector.py::X5BestTechniqueSelectorTechnique.execute
notes_extra: X4_X5_CODE_REFERENCE_REQUIRED=true

#### 39. scraping.x5.result_reinjection

tool: X5 learning
version: private_reference
worker: X5Worker
adapter: X5ReinjectionAdapter
hook: app/modules/scraping_intelligence/x5_result_reinjection.py::X5ResultReinjectionTechnique.execute
notes_extra: X4_X5_CODE_REFERENCE_REQUIRED=true

#### 40. scraping.x5.fallback_chain

tool: X5 + Mistral
version: private_reference
worker: X5Worker
adapter: X5FallbackChainAdapter
hook: app/modules/scraping_intelligence/x5_fallback_chain.py::X5FallbackChainTechnique.execute
notes_extra: X4_X5_CODE_REFERENCE_REQUIRED=true

## Submódulo 9.10 — Exportación y análisis

evidence: export_reference, analysis_summary, chart_reference, normalized_json
graph: DataTableNode, ExportNode, AnalysisNode, EvidenceNode

### Técnicas

#### 41. scraping.export.csv

tool: CSV writer
version: internal
worker: PythonToolWorker
adapter: CsvExportAdapter
hook: app/modules/scraping_intelligence/export_csv.py::ExportCsvTechnique.execute

#### 42. scraping.export.json

tool: JSON writer
version: internal
worker: PythonToolWorker
adapter: JsonExportAdapter
hook: app/modules/scraping_intelligence/export_json.py::ExportJsonTechnique.execute

#### 43. scraping.export.x4_external

tool: X4 external export
version: external_reference
worker: PythonToolWorker
adapter: X4ExportAdapter
hook: app/modules/scraping_intelligence/export_x4_external.py::ExportX4ExternalTechnique.execute
notes_extra: x4_not_runtime_dependency=true

#### 44. scraping.analysis.quick_stats

tool: Mistral + SQLite
version: local_ai
worker: AIWorker
adapter: QuickStatsAdapter
hook: app/modules/scraping_intelligence/analysis_quick_stats.py::AnalysisQuickStatsTechnique.execute

#### 45. scraping.analysis.trend_detection

tool: Mistral + SQLite
version: local_ai
worker: AIWorker
adapter: TrendDetectionAdapter
hook: app/modules/scraping_intelligence/analysis_trend_detection.py::AnalysisTrendDetectionTechnique.execute

#### 46. scraping.analysis.volatility_alert

tool: Mistral + SQLite
version: local_ai
worker: AIWorker
adapter: VolatilityAlertAdapter
hook: app/modules/scraping_intelligence/analysis_volatility_alert.py::AnalysisVolatilityAlertTechnique.execute

#### 47. scraping.analysis.chat_report

tool: Mistral report writer
version: local_ai
worker: AIWorker
adapter: ChatReportAdapter
hook: app/modules/scraping_intelligence/analysis_chat_report.py::AnalysisChatReportTechnique.execute

## Estado documental del módulo

Módulo 9 queda documentado como panel de scraping con chat Mistral, X5, Kali WSL2, SQLite, scheduler, scoring, export CSV/JSON y análisis local.
X4 es externo y no dependencia runtime.
La lógica privada X5 queda en IMPLEMENTACION_USUARIO_REQUERIDA.
No se inventan nombres internos de X5; si hacen falta, se pide código X4/X5.
