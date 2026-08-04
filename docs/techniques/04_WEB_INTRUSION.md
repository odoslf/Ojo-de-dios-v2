# MÓDULO 4 — INTRUSIÓN WEB AVANZADA

## PARTE 1/5 — BASE + INYECCIONES

### Regla absoluta

NO_DOCKER=true

Este módulo solo usa:

- binarios Windows;
- aplicaciones Windows;
- Python en Windows;
- Node.js en Windows;
- WSL2 con paquetes instalados manualmente;
- APIs locales;
- proxies locales;
- IA local;
- lógica privada del usuario en hooks marcados.

Runtimes prohibidos:

- docker
- docker_compose
- container_runtime

### Objetivo del módulo

El Módulo 4 cubre intrusión web avanzada contra aplicaciones modernas:

- aplicaciones clásicas;
- SPAs;
- APIs REST;
- GraphQL;
- gRPC;
- WebSockets;
- WebAssembly;
- uploads;
- SSRF;
- lógica de negocio;
- autenticación;
- sesiones;
- supply chain cliente;
- evasión de WAF/RASP/CDN.

Este catálogo NO contiene lógica funcional ni comandos.

Cada técnica define:

- id exacto;
- herramienta;
- versión;
- runtime;
- worker;
- permisos;
- fields de panel;
- input_schema;
- campos rellenables por LaIA;
- evidence esperada;
- nodos del Attack Surface Graph;
- hook exacto futuro donde el usuario conectará su lógica privada.

### Base del módulo

module_id: web_intrusion
module_name: Intrusión Web Avanzada
panel: Intrusión Web
default_status: IMPLEMENTACION_USUARIO_REQUERIDA
default_demo: true
default_dry_run: true
default_user_logic: true
docker_allowed: false

workers:

- WebIntrusionWorker
- WindowsWorker
- WSLWorker
- APIWorker
- PythonToolWorker
- BrowserAutomationWorker
- NodeToolWorker
- ProxyToolWorker
- AIWorker
- EvidenceWorker

runtimes:

- windows_binary
- windows_app
- java_app
- node_tool
- python_lib
- wsl2
- local_api
- proxy_local
- browser_automation
- local_ai
- manual_required

### Entradas desde otros módulos

inputs_base:

- target_id
- target_type
- target_value
- web_endpoints
- service_fingerprints
- technology_fingerprints
- headers
- cookies_profile
- auth_context
- request_profile
- scope_profile
- finding_id
- cve_id
- execution_mode
- evidence_profile
- confirmation_profile

### Salidas del módulo

outputs_base:

- web_finding
- exploit_attempt_summary
- token_reference
- session_reference
- shell_reference
- data_access_summary
- file_read_summary
- upload_test_summary
- request_response_evidence
- normalized_json
- evidence_ids
- next_module_recommendations

### Evidence común

evidence_comun:

- run_id
- target_id
- technique_id
- module_id
- worker_id
- tool_name
- tool_version
- runtime
- request_reference
- response_reference
- raw_output_path
- normalized_json
- finding_id
- affected_endpoint
- affected_parameter
- vulnerability_class
- confidence
- severity
- access_verified
- token_reference
- shell_reference
- file_reference
- started_at
- finished_at
- errors
- warnings
- next_recommended_techniques

Regla:

SUCCESS nunca es válido sin evidence útil.

### Panel base

panel_base:

- target_selector
- endpoint_selector
- request_profile
- auth_context
- cookie_profile
- header_profile
- body_profile
- proxy_profile
- browser_profile
- scan_profile
- payload_profile
- confirmation_required
- timeout_seconds
- evidence_profile
- notes_for_laia

execution_mode:

- demo
- dry_run
- controlled
- expert

### Herramientas comunes del módulo

Burp Suite: latest-release-lock
Burp baseline_usuario: 2026.5.1
Burp runtime: java_app_windows
Burp notes: versionlock_required=true

ZAP: 2.17.0
ZAP baseline_usuario: 2.16.0
ZAP runtime: windows_app_local_api

Caido: 0.56.0
Caido baseline_usuario: 0.4.0
Caido runtime: windows_app
Caido notes: version_updated_from_user_baseline=true

Python: 3.12
Python libs baseline: requests, aiohttp, websockets, httpx, pycurl

Playwright: 1.60.0
Playwright baseline_usuario: 1.48
Playwright notes: version_updated_from_user_baseline=true

Node.js: 24 LTS
Node.js baseline_usuario: 22 LTS
Node.js notes: Node 22 LTS remains compatible baseline; Node 24 LTS is preferred current LTS.

Mistral: Dolphin Mistral Nemo 12B baseline
Mistral runtime: local_ai

### Submódulo 4.1 — Inyecciones clásicas y modernas

submodule_id: web_intrusion.injection
submodule_name: SQLi, NoSQLi, OS command injection, SSTI, LDAP, XPath, GraphQL, WebSocket command injection
primary_worker: WebIntrusionWorker
secondary_workers:

- PythonToolWorker
- WSLWorker
- ProxyToolWorker
- BrowserAutomationWorker
- AIWorker

Versiones de esta parte:

SQLMap: 1.10
SQLMap baseline_usuario: 1.8.5

NoSQLMap: latest-release-lock
NoSQLMap baseline_usuario: 0.9
NoSQLMap notes: version_requires_review=true

Commix: latest-release-lock
Commix baseline_usuario: 4.0
Commix notes: version_requires_review=true

Tplmap: latest-release-lock
Tplmap baseline_usuario: 0.8
Tplmap notes: version_requires_review=true

Burp Suite: latest-release-lock
Burp baseline_usuario: 2026.5.1

InQL: latest-release-lock
InQL baseline_usuario: 5.0
InQL notes: version_requires_review=true

Python websockets: latest-release-lock

### Técnicas 1-9

#### 1. webintrusion.injection.sqlmap_ai_tamper

tool: SQLMap + Dolphin Mistral Nemo 12B
version: SQLMap 1.10 + Dolphin Mistral Nemo 12B
baseline_usuario: SQLMap 1.8.5
runtime: python_lib + local_ai
worker: PythonToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: target_url, request_profile, parameter_profile, dbms_profile, waf_context, tamper_strategy_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: target_url:string, request_profile:string, parameter_profile:string, dbms_profile:auto|mysql|postgresql|mssql|oracle|sqlite|custom, waf_context:string_optional, tamper_strategy_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: parameter_profile, dbms_profile, waf_context, tamper_strategy_profile, timeout_seconds
evidence: injection_summary, dbms_fingerprint, tamper_strategy_summary, raw_output_path, normalized_json
graph: WebEndpointNode, ParameterNode, DatabaseNode, WeaknessNode, FindingNode
hook: app/modules/web_intrusion/injection_sqlmap_ai_tamper.py::InjectionSqlmapAiTamperTechnique.execute
notes: no_tamper_code_in_docs, no_payloads_in_docs, user_logic_required, requires_confirmation=true

#### 2. webintrusion.injection.sqlmap_os_shell

tool: SQLMap
version: 1.10
baseline_usuario: 1.8.5
runtime: python_lib
worker: PythonToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: target_url, request_profile, parameter_profile, dbms_profile, execution_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: target_url:string, request_profile:string, parameter_profile:string, dbms_profile:auto|mysql|postgresql|mssql|oracle|sqlite|custom, execution_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: parameter_profile, dbms_profile, execution_profile, timeout_seconds
evidence: injection_summary, dbms_fingerprint, shell_reference, raw_output_path, normalized_json
graph: WebEndpointNode, DatabaseNode, SessionCandidateNode, FindingNode
hook: app/modules/web_intrusion/injection_sqlmap_os_shell.py::InjectionSqlmapOsShellTechnique.execute
notes: no_commands_in_docs, no_payloads_in_docs, user_logic_required, requires_confirmation=true

#### 3. webintrusion.injection.nosqlmap_rce

tool: NoSQLMap
version: latest-release-lock
baseline_usuario: 0.9
runtime: python_lib
worker: PythonToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: target_url, request_profile, database_profile, injection_context, execution_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: target_url:string, request_profile:string, database_profile:mongodb|redis|couchdb|custom, injection_context:string, execution_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: database_profile, injection_context, execution_profile, timeout_seconds
evidence: nosql_injection_summary, database_access_summary, raw_output_path, normalized_json
graph: WebEndpointNode, DatabaseNode, WeaknessNode, FindingNode
hook: app/modules/web_intrusion/injection_nosqlmap_rce.py::InjectionNosqlmapRceTechnique.execute
notes: version_requires_review=true, no_payloads_in_docs, user_logic_required, requires_confirmation=true

#### 4. webintrusion.injection.commix_os_cmd

tool: Commix
version: latest-release-lock
baseline_usuario: 4.0
runtime: python_lib_or_wsl2
worker: PythonToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: target_url, request_profile, parameter_profile, injection_context, execution_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: target_url:string, request_profile:string, parameter_profile:string, injection_context:string, execution_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: parameter_profile, injection_context, execution_profile, timeout_seconds
evidence: command_injection_summary, execution_attempt_summary, raw_output_path, normalized_json
graph: WebEndpointNode, ParameterNode, WeaknessNode, ExecutionNode
hook: app/modules/web_intrusion/injection_commix_os_cmd.py::InjectionCommixOsCmdTechnique.execute
notes: version_requires_review=true, no_commands_in_docs, no_payloads_in_docs, user_logic_required, requires_confirmation=true

#### 5. webintrusion.injection.tplmap_ssti

tool: Tplmap
version: latest-release-lock
baseline_usuario: 0.8
runtime: python_lib_or_wsl2
worker: PythonToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: target_url, request_profile, parameter_profile, template_engine_hint, execution_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: target_url:string, request_profile:string, parameter_profile:string, template_engine_hint:auto|jinja2|twig|freemarker|ejs|pug|custom, execution_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: parameter_profile, template_engine_hint, execution_profile
evidence: ssti_summary, template_engine_fingerprint, execution_attempt_summary, raw_output_path, normalized_json
graph: WebEndpointNode, TemplateEngineNode, WeaknessNode, FindingNode
hook: app/modules/web_intrusion/injection_tplmap_ssti.py::InjectionTplmapSstiTechnique.execute
notes: version_requires_review=true, no_template_payloads_in_docs, user_logic_required, requires_confirmation=true

#### 6. webintrusion.injection.ldap_injection

tool: Burp Suite + internal scripts
version: Burp latest-release-lock
baseline_usuario: 2026.5.1
runtime: java_app_windows + python_lib
worker: ProxyToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: request_profile, parameter_profile, ldap_context, test_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: request_profile:string, parameter_profile:string, ldap_context:string_optional, test_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: parameter_profile, ldap_context, test_profile
evidence: ldap_injection_summary, response_diff_summary, raw_output_path, normalized_json
graph: WebEndpointNode, ParameterNode, LDAPNode, WeaknessNode
hook: app/modules/web_intrusion/injection_ldap_injection.py::InjectionLdapInjectionTechnique.execute
notes: no_payloads_in_docs, user_logic_required, requires_confirmation=true

#### 7. webintrusion.injection.xpath_injection

tool: Burp Suite + internal scripts
version: Burp latest-release-lock
baseline_usuario: 2026.5.1
runtime: java_app_windows + python_lib
worker: ProxyToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: request_profile, parameter_profile, xpath_context, test_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: request_profile:string, parameter_profile:string, xpath_context:string_optional, test_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: parameter_profile, xpath_context, test_profile
evidence: xpath_injection_summary, response_diff_summary, raw_output_path, normalized_json
graph: WebEndpointNode, ParameterNode, XMLNode, WeaknessNode
hook: app/modules/web_intrusion/injection_xpath_injection.py::InjectionXpathInjectionTechnique.execute
notes: no_payloads_in_docs, user_logic_required, requires_confirmation=true

#### 8. webintrusion.injection.graphql_injection

tool: InQL + internal scripts
version: latest-release-lock
baseline_usuario: InQL 5.0
runtime: java_app_windows + python_lib
worker: ProxyToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: graphql_endpoint, request_profile, schema_profile, injection_context, confirmation_profile, timeout_seconds, evidence_profile
inputs: graphql_endpoint:string, request_profile:string, schema_profile:string_optional, injection_context:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: schema_profile, injection_context, timeout_seconds
evidence: graphql_injection_summary, schema_context_summary, response_diff_summary, raw_output_path, normalized_json
graph: GraphQLNode, WebEndpointNode, WeaknessNode, FindingNode
hook: app/modules/web_intrusion/injection_graphql_injection.py::InjectionGraphqlInjectionTechnique.execute
notes: version_requires_review=true, no_graphql_payloads_in_docs, user_logic_required, requires_confirmation=true

#### 9. webintrusion.injection.websocket_cmd_injection

tool: Python websockets + internal scripts
version: latest-release-lock
runtime: python_lib
worker: PythonToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: websocket_url, handshake_profile, message_profile, injection_context, confirmation_profile, timeout_seconds, evidence_profile
inputs: websocket_url:string, handshake_profile:string, message_profile:string, injection_context:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: handshake_profile, message_profile, injection_context
evidence: websocket_interaction_summary, response_diff_summary, execution_attempt_summary, raw_output_path, normalized_json
graph: WebSocketNode, ParameterNode, WeaknessNode, FindingNode
hook: app/modules/web_intrusion/injection_websocket_cmd_injection.py::InjectionWebsocketCmdInjectionTechnique.execute
notes: no_messages_or_payloads_in_docs, user_logic_required, requires_confirmation=true

### Integración de esta parte con LaIA + X5

LaIA debe:

- detectar contexto web desde Attack Surface Graph;
- clasificar parámetros y endpoints;
- seleccionar técnica candidata;
- rellenar fields;
- detectar missing_inputs;
- pedir confirmation_profile si hay acción sensible;
- no ejecutar directamente;
- no inventar hallazgos;
- no marcar acceso sin evidence;
- no generar payload funcional dentro de documentación.

X5/OjoRouter debe:

- validar TechniqueRegistry;
- validar scope;
- validar permission_level;
- validar confirmation_profile;
- seleccionar worker;
- crear job;
- guardar EvidenceStore;
- actualizar ScoringEngine;
- actualizar Attack Surface Graph;
- permitir Kill Switch.

Hermes puede proponer en sandbox:

- wrapper;
- parser;
- normalizador de respuestas;
- schema;
- panel_fields;
- evidence_writer;
- plugin;
- documentación de herramienta.

## PARTE 2/5 — LÓGICA DE NEGOCIO + AUTENTICACIÓN

### Regla absoluta de esta parte

NO_DOCKER=true

Runtimes permitidos:

- windows_app
- java_app
- python_lib
- wsl2
- proxy_local
- browser_automation
- local_ai
- manual_required

Runtimes prohibidos:

- docker
- docker_compose
- container_runtime

### Versiones oficiales de esta parte

Autorize: latest-release-lock
Autorize runtime: Burp extension
Autorize notes: bapp_extension=true

Turbo Intruder: 1.2.0 latest-release-lock
Turbo Intruder runtime: Burp extension

Burp Suite: latest-release-lock
Burp baseline_usuario: 2026.5.1

Playwright: 1.60.0
Playwright baseline_usuario: 1.48

jwt_tool: 2.3.0
jwt_tool baseline_usuario: 2.2.6

THC Hydra: 9.7

o365spray: baseline_usuario 1.0
o365spray notes: upstream_ported_to_omnispray=true, no_sustituir_sin_aprobacion=true

Evilginx: latest-release-lock
Evilginx baseline_usuario: 3.3
Evilginx notes: version_requires_review=true

Python requests/aiohttp: latest-release-lock
Python Flask: latest-release-lock

### Submódulo 4.2 — Abuso de lógica de negocio

submodule_id: web_intrusion.business
submodule_name: IDOR, authorization bypass, race conditions, price manipulation, workflow abuse
primary_worker: WebIntrusionWorker
secondary_workers:

- ProxyToolWorker
- PythonToolWorker
- BrowserAutomationWorker
- AIWorker

#### 10. webintrusion.business.idor_autorize

tool: Autorize Burp extension
version: latest-release-lock
runtime: proxy_local
worker: ProxyToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: request_profile, high_priv_context, low_priv_context, unauth_context, authorization_profile, comparison_profile, evidence_profile
inputs: request_profile:string, high_priv_context:string, low_priv_context:string_optional, unauth_context:string_optional, authorization_profile:string, comparison_profile:string, evidence_profile:string
ai: authorization_profile, comparison_profile
evidence: authorization_diff_summary, idor_candidate, response_comparison, raw_output_path, normalized_json
graph: WebEndpointNode, AuthorizationNode, IdentityNode, FindingNode
hook: app/modules/web_intrusion/business_idor_autorize.py::BusinessIdorAutorizeTechnique.execute
notes: no_request_replay_steps_in_docs, user_logic_required, requires_confirmation=true

#### 11. webintrusion.business.idor_custom_scripts

tool: Python requests/aiohttp
version: latest-release-lock
runtime: python_lib
worker: PythonToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: request_profile, object_id_profile, auth_context, comparison_profile, rate_limit_profile, timeout_seconds, evidence_profile
inputs: request_profile:string, object_id_profile:string, auth_context:string, comparison_profile:string, rate_limit_profile:string, timeout_seconds:int, evidence_profile:string
ai: object_id_profile, comparison_profile, rate_limit_profile
evidence: idor_test_summary, unauthorized_access_candidate, response_diff_summary, raw_output_path, normalized_json
graph: WebEndpointNode, ObjectReferenceNode, AuthorizationNode, FindingNode
hook: app/modules/web_intrusion/business_idor_custom_scripts.py::BusinessIdorCustomScriptsTechnique.execute
notes: no_enumeration_logic_in_docs, user_logic_required, requires_confirmation=true

#### 12. webintrusion.business.race_conditions

tool: Turbo Intruder
version: 1.2.0 latest-release-lock
runtime: proxy_local
worker: ProxyToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: request_profile, race_profile, concurrency_profile, timing_profile, success_condition_profile, confirmation_profile, evidence_profile
inputs: request_profile:string, race_profile:string, concurrency_profile:string, timing_profile:string, success_condition_profile:string, confirmation_profile:string, evidence_profile:string
ai: race_profile, concurrency_profile, timing_profile, success_condition_profile
evidence: race_test_summary, response_timing_summary, state_change_candidate, raw_output_path, normalized_json
graph: WebEndpointNode, RaceConditionNode, FindingNode
hook: app/modules/web_intrusion/business_race_conditions.py::BusinessRaceConditionsTechnique.execute
notes: no_turbo_intruder_script_in_docs, user_logic_required, requires_confirmation=true

#### 13. webintrusion.business.price_manipulation

tool: Python requests/aiohttp
version: latest-release-lock
runtime: python_lib
worker: PythonToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: request_profile, parameter_profile, workflow_profile, validation_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: request_profile:string, parameter_profile:string, workflow_profile:string, validation_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: parameter_profile, workflow_profile, validation_profile
evidence: business_logic_summary, price_integrity_candidate, response_diff_summary, raw_output_path, normalized_json
graph: WebEndpointNode, BusinessLogicNode, FindingNode
hook: app/modules/web_intrusion/business_price_manipulation.py::BusinessPriceManipulationTechnique.execute
notes: no_business_abuse_steps_in_docs, user_logic_required, requires_confirmation=true

#### 14. webintrusion.business.workflow_abuse

tool: Python requests/aiohttp + Playwright
version: Playwright 1.60.0
baseline_usuario: 1.48
runtime: python_lib + browser_automation
worker: BrowserAutomationWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: workflow_profile, browser_profile, auth_context, state_model_profile, validation_profile, confirmation_profile, evidence_profile
inputs: workflow_profile:string, browser_profile:string, auth_context:string, state_model_profile:string, validation_profile:string, confirmation_profile:string, evidence_profile:string
ai: workflow_profile, state_model_profile, validation_profile
evidence: workflow_abuse_summary, state_transition_summary, browser_trace_reference, normalized_json
graph: WebEndpointNode, WorkflowNode, BusinessLogicNode, FindingNode
hook: app/modules/web_intrusion/business_workflow_abuse.py::BusinessWorkflowAbuseTechnique.execute
notes: no_workflow_abuse_steps_in_docs, user_logic_required, requires_confirmation=true

#### 15. webintrusion.business.coupon_exhaustion

tool: Python requests/aiohttp
version: latest-release-lock
runtime: python_lib
worker: PythonToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: request_profile, coupon_profile, rate_limit_profile, validation_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: request_profile:string, coupon_profile:string, rate_limit_profile:string, validation_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: coupon_profile, rate_limit_profile, validation_profile
evidence: coupon_logic_summary, rate_limit_summary, response_diff_summary, raw_output_path, normalized_json
graph: WebEndpointNode, BusinessLogicNode, RateLimitNode, FindingNode
hook: app/modules/web_intrusion/business_coupon_exhaustion.py::BusinessCouponExhaustionTechnique.execute
notes: no_coupon_abuse_steps_in_docs, user_logic_required, requires_confirmation=true

#### 16. webintrusion.business.invite_code_enumeration

tool: Python requests/aiohttp
version: latest-release-lock
runtime: python_lib
worker: PythonToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: request_profile, token_profile, rate_limit_profile, validation_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: request_profile:string, token_profile:string, rate_limit_profile:string, validation_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: token_profile, rate_limit_profile, validation_profile
evidence: invite_code_summary, enumeration_risk_summary, response_diff_summary, raw_output_path, normalized_json
graph: WebEndpointNode, TokenNode, BusinessLogicNode, FindingNode
hook: app/modules/web_intrusion/business_invite_code_enumeration.py::BusinessInviteCodeEnumerationTechnique.execute
notes: no_enumeration_logic_in_docs, user_logic_required, requires_confirmation=true

### Submódulo 4.3 — Autenticación y sesiones

submodule_id: web_intrusion.auth
submodule_name: JWT, OAuth2, SAML, cookies, login, O365, MFA, OpenID Connect
primary_worker: WebIntrusionWorker
secondary_workers:

- PythonToolWorker
- WSLWorker
- ProxyToolWorker
- BrowserAutomationWorker
- AIWorker

#### 17. webintrusion.auth.jwt_tool_attacks

tool: jwt_tool
version: 2.3.0
baseline_usuario: 2.2.6
runtime: python_lib
worker: PythonToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: token_reference, request_profile, jwt_profile, validation_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: token_reference:string, request_profile:string, jwt_profile:string, validation_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: jwt_profile, validation_profile, timeout_seconds
evidence: jwt_analysis_summary, jwt_weakness_candidates, response_diff_summary, raw_output_path, normalized_json
graph: JWTNode, TokenNode, AuthNode, FindingNode
hook: app/modules/web_intrusion/auth_jwt_tool_attacks.py::AuthJwtToolAttacksTechnique.execute
notes: no_jwt_attack_steps_in_docs, user_logic_required, requires_confirmation=true

#### 18. webintrusion.auth.oauth2_misconfiguration

tool: Burp Suite + Python scripts
version: Burp latest-release-lock
runtime: proxy_local + python_lib
worker: ProxyToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: oauth_flow_profile, client_profile, redirect_uri_profile, token_profile, validation_profile, confirmation_profile, evidence_profile
inputs: oauth_flow_profile:string, client_profile:string, redirect_uri_profile:string, token_profile:string_optional, validation_profile:string, confirmation_profile:string, evidence_profile:string
ai: oauth_flow_profile, client_profile, redirect_uri_profile, validation_profile
evidence: oauth_flow_summary, misconfiguration_candidates, response_diff_summary, normalized_json
graph: OAuthNode, TokenNode, AuthNode, FindingNode
hook: app/modules/web_intrusion/auth_oauth2_misconfiguration.py::AuthOauth2MisconfigurationTechnique.execute
notes: no_oauth_abuse_steps_in_docs, user_logic_required, requires_confirmation=true

#### 19. webintrusion.auth.saml_injection

tool: Burp Suite + Python scripts
version: Burp latest-release-lock
runtime: proxy_local + python_lib
worker: ProxyToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: saml_flow_profile, assertion_profile, identity_provider_profile, validation_profile, confirmation_profile, evidence_profile
inputs: saml_flow_profile:string, assertion_profile:string, identity_provider_profile:string_optional, validation_profile:string, confirmation_profile:string, evidence_profile:string
ai: saml_flow_profile, assertion_profile, validation_profile
evidence: saml_flow_summary, saml_weakness_candidates, response_diff_summary, normalized_json
graph: SAMLNode, IdentityProviderNode, AuthNode, FindingNode
hook: app/modules/web_intrusion/auth_saml_injection.py::AuthSamlInjectionTechnique.execute
notes: no_saml_attack_steps_in_docs, user_logic_required, requires_confirmation=true

#### 20. webintrusion.auth.cookie_theft_xss_mitm

tool: XSS/MITM cross-module connector
version: internal
runtime: cross_module
worker: WebIntrusionWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: xss_finding_reference, mitm_context_reference, cookie_profile, validation_profile, confirmation_profile, evidence_profile
inputs: xss_finding_reference:string_optional, mitm_context_reference:string_optional, cookie_profile:string, validation_profile:string, confirmation_profile:string, evidence_profile:string
ai: cookie_profile, validation_profile
evidence: cookie_risk_summary, session_risk_summary, cross_module_references, normalized_json
graph: CookieNode, SessionNode, XSSNode, MITMNode, FindingNode
hook: app/modules/web_intrusion/auth_cookie_theft_xss_mitm.py::AuthCookieTheftXssMitmTechnique.execute
notes: cross_module_reference=module_4_client_and_module_6_mitm, no_cookie_theft_steps_in_docs, user_logic_required, requires_confirmation=true

#### 21. webintrusion.auth.web_login_bruteforce

tool: THC Hydra
version: 9.7
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, login_profile, credential_profile, username_source, password_source, rate_limit_profile, lockout_policy_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, login_profile:string, credential_profile:string, username_source:string, password_source:string, rate_limit_profile:string, lockout_policy_profile:string, timeout_seconds:int, evidence_profile:string
ai: login_profile, username_source, password_source, rate_limit_profile, lockout_policy_profile
evidence: credential_test_summary, valid_login_candidate, lockout_safety_status, raw_output_path, normalized_json
graph: LoginNode, CredentialNode, AuthNode, FindingNode
hook: app/modules/web_intrusion/auth_web_login_bruteforce.py::AuthWebLoginBruteforceTechnique.execute
notes: no_wordlists_in_docs, user_logic_required, requires_confirmation=true

#### 22. webintrusion.auth.o365_password_spray

tool: o365spray
version: baseline_usuario 1.0
runtime: python_lib
worker: PythonToolWorker
perm: CREDENTIALS
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: tenant_profile, username_source, password_source, rate_limit_profile, lockout_policy_profile, output_profile, confirmation_profile, evidence_profile
inputs: tenant_profile:string, username_source:string, password_source:string, rate_limit_profile:string, lockout_policy_profile:string, output_profile:string, confirmation_profile:string, evidence_profile:string
ai: tenant_profile, username_source, password_source, rate_limit_profile, lockout_policy_profile
evidence: spray_summary, valid_login_candidate, lockout_safety_status, raw_output_path, normalized_json
graph: CloudIdentityNode, CredentialNode, AuthNode, FindingNode
hook: app/modules/web_intrusion/auth_o365_password_spray.py::AuthO365PasswordSprayTechnique.execute
notes: upstream_ported_to_omnispray=true, no_sustituir_sin_aprobacion=true, no_wordlists_in_docs, user_logic_required, requires_confirmation=true

#### 23. webintrusion.auth.mfa_bypass_evilginx

tool: Evilginx
version: latest-release-lock
baseline_usuario: 3.3
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: lab_domain_profile, phishlet_profile, tls_profile, target_service_profile, capture_profile, confirmation_profile, evidence_profile
inputs: lab_domain_profile:string, phishlet_profile:string, tls_profile:string, target_service_profile:string, capture_profile:string, confirmation_profile:string, evidence_profile:string
ai: target_service_profile, capture_profile
evidence: campaign_lab_summary, token_capture_risk_summary, session_token_reference, raw_output_path, normalized_json
graph: PhishingNode, TokenNode, SessionNode, AuthNode
hook: app/modules/web_intrusion/auth_mfa_bypass_evilginx.py::AuthMfaBypassEvilginxTechnique.execute
notes: cross_module_reference=module_14_phishing, no_phishlet_steps_in_docs, no_token_use_steps_in_docs, user_logic_required, requires_confirmation=true, version_requires_review=true

#### 24. webintrusion.auth.openid_connect_abuse

tool: Python requests/aiohttp + Flask lab connector
version: latest-release-lock
runtime: python_lib
worker: PythonToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: oidc_flow_profile, client_profile, redirect_uri_profile, jwks_profile, validation_profile, confirmation_profile, evidence_profile
inputs: oidc_flow_profile:string, client_profile:string, redirect_uri_profile:string, jwks_profile:string_optional, validation_profile:string, confirmation_profile:string, evidence_profile:string
ai: oidc_flow_profile, client_profile, redirect_uri_profile, validation_profile
evidence: oidc_flow_summary, oidc_misconfig_candidates, response_diff_summary, normalized_json
graph: OIDCNode, JWTNode, TokenNode, AuthNode, FindingNode
hook: app/modules/web_intrusion/auth_openid_connect_abuse.py::AuthOpenidConnectAbuseTechnique.execute
notes: no_oidc_abuse_steps_in_docs, user_logic_required, requires_confirmation=true

### Integración de esta parte con LaIA + X5

LaIA debe:

- detectar flujos de autorización y autenticación;
- clasificar endpoints sensibles;
- seleccionar técnica candidata;
- rellenar fields;
- detectar missing_inputs;
- recomendar perfiles de comparación y validación;
- pedir confirmation_profile en acciones sensibles;
- no ejecutar directamente;
- no inventar acceso;
- no marcar credenciales válidas sin evidence;
- no generar campañas ni payloads desde documentación.

X5/OjoRouter debe:

- validar TechniqueRegistry;
- validar scope;
- validar permission_level;
- validar confirmation_profile;
- seleccionar worker;
- crear job;
- guardar EvidenceStore;
- actualizar ScoringEngine;
- actualizar Attack Surface Graph;
- permitir Kill Switch.

Hermes puede proponer en sandbox:

- wrapper;
- parser;
- normalizador de respuestas;
- schema;
- panel_fields;
- evidence_writer;
- plugin;
- documentación de herramienta.

## PARTE 3/5 — CLIENT-SIDE + SSRF + APIs

Regla: solo catálogo, conexiones, fields, evidence y hooks. Sin comandos, payloads, PoC, wordlists ni pasos operativos.

### Submódulo 4.4 — XSS, navegador y cliente

#### 25. webintrusion.client.xsstrike_xss

tool: XSStrike
version: latest-release-lock
runtime: python_lib
worker: WebIntrusionWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, client_profile, validation_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, client_profile:string, validation_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/client_xsstrike_xss.py::ClientXsstrikeXssTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 26. webintrusion.client.xss_hunter_blind

tool: XSS Hunter compatible private endpoint
version: internal
runtime: local_api
worker: WebIntrusionWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, private_endpoint_profile, callback_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, private_endpoint_profile:string, callback_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/client_xss_hunter_blind.py::ClientXssHunterBlindTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 27. webintrusion.client.csrf_poc_builder

tool: Burp Suite + Python generator
version: Burp latest-release-lock
runtime: proxy_local+python_lib
worker: WebIntrusionWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, csrf_profile, request_profile, validation_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, csrf_profile:string, request_profile:string, validation_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/client_csrf_poc_builder.py::ClientCsrfPocBuilderTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 28. webintrusion.client.clickjacking_check

tool: Browser automation
version: Playwright 1.60.0
runtime: browser_automation
worker: WebIntrusionWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, browser_profile, frame_policy_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, browser_profile:string, frame_policy_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/client_clickjacking_check.py::ClientClickjackingCheckTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 29. webintrusion.client.prototype_pollution

tool: DOM Invader + pp-finder
version: Burp latest-release-lock + latest-release-lock
runtime: proxy_local+node_tool
worker: WebIntrusionWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, dom_profile, analysis_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, dom_profile:string, analysis_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/client_prototype_pollution.py::ClientPrototypePollutionTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 30. webintrusion.client.css_injection

tool: Browser automation
version: Playwright 1.60.0
runtime: browser_automation
worker: WebIntrusionWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, browser_profile, css_context_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, browser_profile:string, css_context_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/client_css_injection.py::ClientCssInjectionTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 31. webintrusion.client.asset_replacement

tool: Proxy lab connector
version: internal
runtime: proxy_local
worker: WebIntrusionWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, asset_profile, proxy_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, asset_profile:string, proxy_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/client_asset_replacement.py::ClientAssetReplacementTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

### Submódulo 4.5 — SSRF y request chaining

#### 32. webintrusion.ssrf.ssrfmap

tool: SSRFmap
version: latest-release-lock
runtime: python_lib
worker: WebIntrusionWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, ssrf_profile, request_chain_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, ssrf_profile:string, request_chain_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/ssrf_ssrfmap.py::SsrfSsrfmapTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 33. webintrusion.ssrf.gopherus_payload_model

tool: Gopherus
version: latest-release-lock
runtime: python_lib
worker: WebIntrusionWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, ssrf_profile, request_chain_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, ssrf_profile:string, request_chain_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/ssrf_gopherus_payload_model.py::SsrfGopherusPayloadModelTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 34. webintrusion.ssrf.cloud_metadata_check

tool: Python requests/httpx
version: latest-release-lock
runtime: python_lib
worker: WebIntrusionWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, cloud_profile, ssrf_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, cloud_profile:string, ssrf_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/ssrf_cloud_metadata_check.py::SsrfCloudMetadataCheckTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 35. webintrusion.ssrf.internal_port_probe

tool: Python requests/httpx
version: latest-release-lock
runtime: python_lib
worker: WebIntrusionWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, ssrf_profile, port_probe_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, ssrf_profile:string, port_probe_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/ssrf_internal_port_probe.py::SsrfInternalPortProbeTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

### Submódulo 4.6 — APIs modernas

#### 36. webintrusion.api.graphql_clairvoyance

tool: Clairvoyance
version: latest-release-lock
runtime: python_lib
worker: WebIntrusionWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, graphql_profile, schema_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, graphql_profile:string, schema_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/api_graphql_clairvoyance.py::ApiGraphqlClairvoyanceTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 37. webintrusion.api.graphql_inql

tool: InQL
version: latest-release-lock
runtime: proxy_local
worker: WebIntrusionWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, graphql_profile, proxy_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, graphql_profile:string, proxy_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/api_graphql_inql.py::ApiGraphqlInqlTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 38. webintrusion.api.rest_ffuf_discovery

tool: ffuf
version: latest-release-lock
runtime: wsl2
worker: WebIntrusionWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, rest_profile, discovery_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, rest_profile:string, discovery_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/api_rest_ffuf_discovery.py::ApiRestFfufDiscoveryTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 39. webintrusion.api.bola_idor

tool: Python requests/httpx
version: latest-release-lock
runtime: python_lib
worker: WebIntrusionWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, api_profile, authorization_profile, object_reference_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, api_profile:string, authorization_profile:string, object_reference_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/api_bola_idor.py::ApiBolaIdorTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 40. webintrusion.api.soap_xxe

tool: Burp Suite + Python parser
version: Burp latest-release-lock
runtime: proxy_local+python_lib
worker: WebIntrusionWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, soap_profile, parser_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, soap_profile:string, parser_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/api_soap_xxe.py::ApiSoapXxeTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 41. webintrusion.api.grpc_reflection

tool: grpcurl
version: latest-release-lock
runtime: windows_binary
worker: WebIntrusionWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, grpc_profile, reflection_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, grpc_profile:string, reflection_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/api_grpc_reflection.py::ApiGrpcReflectionTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 42. webintrusion.api.websocket_fuzzing

tool: websockets/httpx
version: latest-release-lock
runtime: python_lib
worker: WebIntrusionWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, websocket_profile, fuzzing_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, websocket_profile:string, fuzzing_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/api_websocket_fuzzing.py::ApiWebsocketFuzzingTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 43. webintrusion.api.openapi_abuse

tool: Python OpenAPI parser
version: latest-release-lock
runtime: python_lib
worker: WebIntrusionWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, openapi_profile, parser_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, openapi_profile:string, parser_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/api_openapi_abuse.py::ApiOpenapiAbuseTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

#### 44. webintrusion.api.postman_collection_abuse

tool: Postman/Newman
version: latest-release-lock
runtime: node_tool
worker: WebIntrusionWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, postman_collection_profile, validation_profile, timeout_seconds, evidence_profile
inputs: targets:list_string, postman_collection_profile:string, validation_profile:string, timeout_seconds:int, evidence_profile:string
evidence: request_response_evidence, finding_summary, raw_output_path, normalized_json
hook: app/modules/web_intrusion/api_postman_collection_abuse.py::ApiPostmanCollectionAbuseTechnique.execute
notes: no_payloads_in_docs,user_logic_required,requires_confirmation=true

## PARTE 4/5 — UPLOADS + EVASIÓN

### Regla absoluta de esta parte

NO_DOCKER=true

Runtimes permitidos:

- windows_binary
- windows_app
- java_app
- python_lib
- node_tool
- wsl2
- proxy_local
- browser_automation
- local_ai
- manual_required

Runtimes prohibidos:

- docker
- docker_compose
- container_runtime

### Versiones oficiales de esta parte

Fuxploider: latest-release-lock
Fuxploider baseline_usuario: 1.0
Fuxploider notes: version_requires_review=true

Weevely3: latest-release-lock
Weevely3 baseline_usuario: 4.0.1
Weevely3 notes: version_requires_review=true

SharPyShell: latest-release-lock
SharPyShell baseline_usuario: 1.0
SharPyShell notes: version_requires_review=true

WebShellJScript: latest-release-lock
WebShellJScript baseline_usuario: 1.0
WebShellJScript notes: version_requires_review=true

dotdotpwn: latest-release-lock
dotdotpwn baseline_usuario: 3.1
dotdotpwn notes: version_requires_review=true

PHPGGC: latest-release-lock

ysoserial: latest-release-lock

WAFW00F: 2.3.2
WAFW00F baseline_usuario: 2.2.0

WhatWaf: 1.0
WhatWaf baseline_usuario: 1.0

SQLMap: 1.10

Tor profile: external_runtime_profile
Tor notes: optional_connection_profile=true

Python requests/aiohttp/httpx: latest-release-lock

### Submódulo 4.7 — Archivos y uploads

submodule_id: web_intrusion.upload
submodule_name: Upload bypass, webshell artifacts, LFI/RFI, log poisoning, config read, deserialization
primary_worker: WebIntrusionWorker
secondary_workers:

- PythonToolWorker
- WSLWorker
- WindowsWorker
- ProxyToolWorker
- AIWorker

Regla del submódulo:

Este submódulo solo documenta conexiones, fields, evidence y hooks.

No se documentan webshells reales.
No se documentan payloads.
No se documentan comandos.
No se documentan bypasses paso a paso.
Toda lógica queda como IMPLEMENTACION_USUARIO_REQUERIDA.


### Submódulo 4.8 — Evasión de defensas

submodule_id: web_intrusion.evasion
submodule_name: WAF, RASP, CDN, IP bans, tamper profiles
primary_worker: WebIntrusionWorker
secondary_workers:

- PythonToolWorker
- WSLWorker
- AIWorker
- ProxyToolWorker

Regla del submódulo:

Este submódulo solo define perfiles, detección, conexión y evidence.

No se documentan técnicas de evasión paso a paso.
No se documentan payloads.
No se documentan scripts de bypass.
Toda lógica queda como IMPLEMENTACION_USUARIO_REQUERIDA.


## PARTE 5/5 — SUPPLY CHAIN + INTEGRACIÓN FINAL

### Regla absoluta de esta parte

NO_DOCKER=true

Runtimes permitidos:

- windows_binary
- windows_app
- node_tool
- python_lib
- wsl2
- local_ai
- manual_required

Runtimes prohibidos:

- docker
- docker_compose
- container_runtime

### Versiones oficiales de esta parte

npm audit: Node.js/npm built-in
Node.js baseline_usuario: 22 LTS
Node.js recomendado_actual: 24 LTS
Node.js notes: mantener compatibilidad con 22 LTS si el proyecto lo requiere

pip-audit: latest-release-lock
pip-audit notes: usa Python Packaging Advisory Database / PyPI advisory source

TruffleHog: 3.95.2
TruffleHog baseline_usuario: 3.69
TruffleHog notes: version_updated_from_user_baseline=true

source-map-explorer: 2.5.3
source-map-explorer notes: latest public npm version 2.5.3

dependency_confusion scripts: internal
dependency_confusion notes: solo_laboratorio, user_logic_required

### Submódulo 4.9 — Supply Chain y dependencias cliente

submodule_id: web_intrusion.supply
submodule_name: npm, pip, JS bundles, source maps, dependency confusion lab
primary_worker: WebIntrusionWorker
secondary_workers:

- NodeToolWorker
- PythonToolWorker
- WindowsWorker
- AIWorker

Regla del submódulo:

Este submódulo documenta análisis de dependencias, secretos en bundles, source maps y pruebas de laboratorio sobre cadena de suministro.

No se documenta publicación real de paquetes.
No se documentan pasos de dependency confusion.
No se documentan payloads.
No se ejecuta nada en esta ronda.
Toda lógica queda como IMPLEMENTACION_USUARIO_REQUERIDA.


### Integración final del Módulo 4 con LaIA

LaIA debe actuar como analista ofensivo-controlado del módulo web.

LaIA puede:

- recibir endpoints, requests, responses, headers, cookies y auth_context;
- leer ServiceFingerprint;
- leer Attack Surface Graph;
- clasificar la aplicación web;
- seleccionar submódulo;
- proponer técnica candidata;
- rellenar fields;
- detectar missing_inputs;
- analizar evidence posterior;
- recomendar siguiente paso;
- pedir Hermes si falta wrapper, parser, panel field, normalizador o evidence_writer.

LaIA no puede:

- ejecutar directamente;
- inventar vulnerabilidades;
- inventar tokens;
- inventar shells;
- marcar acceso sin evidence;
- saltar X5;
- saltar permission_level;
- saltar confirmation_profile;
- generar payload funcional desde documentación;
- promocionar propuestas Hermes.

### Integración final del Módulo 4 con X5/OjoRouter

X5/OjoRouter debe:

- validar que technique_id existe;
- validar module_id;
- validar scope;
- validar permission_level;
- validar execution_mode;
- validar confirmation_profile;
- validar required_inputs;
- seleccionar worker;
- crear job;
- permitir Kill Switch;
- guardar EvidenceStore;
- actualizar ScoringEngine;
- actualizar Attack Surface Graph;
- devolver result_status;
- proponer fallback;
- pedir Hermes si falta pieza.

Estados permitidos:

- SUCCESS
- FAILED
- PARTIAL
- MANUAL_REQUIRED
- MISSING_TOOL
- MISSING_INPUT
- PERMISSION_DENIED
- OUT_OF_SCOPE
- CONFIRMATION_REQUIRED
- IMPLEMENTACION_USUARIO_REQUERIDA

### Integración final del Módulo 4 con Hermes

Hermes puede crear en sandbox:

- wrapper de herramienta;
- parser de salida;
- normalizador de respuestas HTTP;
- normalizador de GraphQL;
- normalizador de WebSocket;
- normalizador de source maps;
- schema;
- panel_fields;
- evidence_writer;
- fixture demo;
- documentación;
- propuesta de técnica nueva.

Hermes no puede:

- tocar producción directamente;
- autoaprobarse;
- saltarse Mistral review;
- saltarse approval;
- ejecutar técnica real;
- marcar stub como funcional;
- eliminar IMPLEMENTACION_USUARIO_REQUERIDA;
- crear payload real desde documentación.

Flujo Hermes obligatorio:

sandbox
→ tests estructurales
→ evidence
→ revisión Mistral
→ diff
→ aprobación usuario
→ promoción controlada
→ rollback disponible

### Integración final con EvidenceStore

Toda técnica del Módulo 4 debe guardar:

- run_id
- target_id
- technique_id
- module_id
- worker_id
- tool_name
- tool_version
- runtime
- started_at
- finished_at
- result_status
- evidence_quality
- request_reference
- response_reference
- raw_output_path
- normalized_json
- finding_id
- affected_endpoint
- affected_parameter
- vulnerability_class
- confidence
- severity
- access_verified
- token_reference si existe
- shell_reference si existe
- file_reference si existe
- artifact_reference si existe
- confirmation_profile
- rollback_notes
- next_recommended_techniques

Regla:

SUCCESS nunca es válido sin evidence útil.

### Integración final con Attack Surface Graph

El Módulo 4 debe actualizar el grafo con:

- WebEndpointNode
- ParameterNode
- HeaderNode
- CookieNode
- AuthNode
- TokenNode
- SessionNode
- JWTNode
- OAuthNode
- SAMLNode
- OIDCNode
- GraphQLNode
- RESTNode
- SOAPNode
- GRPCNode
- WebSocketNode
- WebAssemblyNode
- UploadFindingNode
- LFINode
- RFINode
- SSRFNode
- WAFNode
- RASPNode
- DependencyNode
- PackageNode
- SecretExposureNode
- FindingNode
- EvidenceNode
- NextStepNode

Relaciones mínimas:

WEB_ENDPOINT_HAS_PARAMETER
WEB_ENDPOINT_HAS_HEADER
WEB_ENDPOINT_USES_AUTH
SERVICE_MATCHES_TECHNIQUE
TECHNIQUE_USES_WORKER
TECHNIQUE_EXPECTS_EVIDENCE
TECHNIQUE_PRODUCED_EVIDENCE
EVIDENCE_SUPPORTS_FINDING
FINDING_SUGGESTS_NEXT_STEP
TECHNIQUE_FAILED_NEEDS_HERMES

### Índice completo del Módulo 4

El catálogo completo del Módulo 4 contiene 44 técnicas:

1-9 Inyecciones clásicas y modernas
10-16 Lógica de negocio
17-24 Autenticación y sesiones
25-31 Cliente
32-35 SSRF
36-44 APIs modernas


## Estado documental del módulo

Módulo 4 — Intrusión web avanzada queda documentado como catálogo técnico de conexiones, workers, adapters, hooks, evidence y estado de implementación.
Las técnicas sensibles quedan marcadas como IMPLEMENTACION_USUARIO_REQUERIDA.
Este documento no contiene comandos operativos, payloads, PoC ni guías de explotación paso a paso.
