# HERMES CVE RESPONSE PLAYBOOK — OJO DE DIOS

## Propósito

Definir cómo Hermes ayuda a Ojo de Dios a responder a una CVE nueva sin ejecutar producción ni saltarse controles.

Este playbook no implementa exploit, scanner, worker ni ingesta. Define el camino controlado desde noticia externa hasta detección revisada y promocionada.

## Caso de uso

Aparece una CVE nueva que afecta a un producto detectado en un target autorizado.

Ojo de Dios debe poder:

- importarla;
- entenderla;
- cruzarla con Attack Surface Graph;
- priorizarla;
- comprobar si existe técnica registrada;
- preparar detección controlada;
- crear proposal Hermes si falta una pieza;
- guardar evidence;
- aprender.

## Flujo detallado

1. CVE Intelligence ingiere CVE.
2. Normalizador crea CVE record.
3. CPE matcher compara con productos/versiones.
4. Attack Surface Graph marca candidate.
5. LaIA recibe cve_intelligence_pack.
6. Si LaIA/Mistral no alcanza confianza suficiente, solicita consulta mínima a DeepSeekAssist con deepseek-v4-flash.
7. DeepSeekAssist devuelve JSON corto, sanitizado, cacheable y validable.
8. LaIA devuelve JSON con plan recomendado.
9. X5 valida plan.
10. Si existe técnica registrada, X5 propone modo permitido.
11. Si falta herramienta/parser/template/panel/schema, X5 pide Hermes proposal.
12. Hermes genera en sandbox.
13. Hermes crea manifest.
14. Hermes crea docs.
15. Hermes crea fixtures.
16. Hermes crea tests estructurales.
17. Hermes marca lógica sensible como IMPLEMENTACION_USUARIO_REQUERIDA.
18. Mistral revisa proposal.
19. Panel muestra diff, riesgo, evidence demo y límites.
20. Usuario aprueba o rechaza.
21. Si aprueba, promotion pipeline mueve a promoted.
22. VersionLock registra.
23. Registry reload.
24. Knowledge Base refresh.
25. ScoringEngine aprende.

## Manifest CVE proposal

Cada proposal debe incluir:

- proposal_id;
- cve_id;
- title;
- affected_product;
- affected_versions;
- source_urls;
- source_hashes;
- module_id;
- technique_id propuesta;
- tool_id;
- permissions;
- requires_confirmation;
- requires_user_implementation;
- generated_files;
- modified_files;
- evidence_demo_path;
- tests;
- risk;
- limitations;
- rollback_plan;
- mistral_review_status;
- user_approval_status.

## Qué puede generar Hermes

- docs/tools/<tool_id>.md;
- docs/cve/<cve_id>.md si se decide crear carpeta futura;
- parser de salida en sandbox;
- wrapper en sandbox;
- panel fields en sandbox;
- schema de evidence;
- fixture;
- test estructural;
- template de detección controlada si aplica;
- mapeo CVE→Technique;
- recomendaciones de VersionLock;
- propuesta de registry entry.

## Qué no puede generar como funcional directamente

- exploit activo;
- ejecución contra objetivo real;
- bypass;
- persistencia;
- credenciales reales;
- evasión real;
- cambios en producción;
- autoaprobación;
- modificación de X5 core;
- técnica marcada como READY si falta lógica real.

## Estados de propuesta

- draft
- designed
- generated
- tested
- review_required
- approved_by_user
- promoted
- rejected
- archived

## Evidence de CVE

La evidence debe diferenciar:

- advisory_imported;
- cpe_match;
- surface_candidate;
- safe_detection_result;
- manual_required;
- false_positive

## Límites de seguridad

Hermes debe preferir detección segura, parsers, fixtures, schemas y documentación. Cuando una CVE requiera lógica sensible, explotación activa, credenciales, bypass, persistencia o interacción destructiva, la propuesta debe quedar con IMPLEMENTACION_USUARIO_REQUERIDA y permiso explícito.

## Cierre operativo

Una CVE nueva no se convierte automáticamente en capacidad funcional. Solo puede avanzar por X5, Hermes sandbox, revisión Mistral, aprobación de usuario, Promotion Pipeline, VersionLock, registry reload y EvidenceStore.


## DeepSeekAssist en respuesta CVE

DeepSeekAssist participa como Hermes Agent externo cuando esté habilitado: `deepseek-v4-pro` es el modelo principal de calidad y `deepseek-v4-flash` queda para healthcheck, resumen rápido, clasificación simple o fallback.

Toda consulta debe ser mínima y sanitizada. No se enviarán secretos, `.env`, cookies, tokens, contraseñas, credenciales reales, repo completo ni logs completos si basta un extracto.

La respuesta de DeepSeekAssist no convierte una CVE en capacidad funcional. Solo ayuda a LaIA/Mistral y Hermes Agent a preparar una proposal que X5/OjoRouter valida y que el usuario aprueba antes de promoción.
