# CVE-to-Technique Pipeline

## Objetivo

Cuando aparezca una CVE nueva o una técnica nueva, Ojo de Dios debe poder investigarla, priorizarla, relacionarla con módulos/técnicas existentes, crear knowledge pack, crear propuesta Hermes Agent y dejarla lista para aprobación, sin ejecución real automática.

Esto forma parte del diseño base de v0.1 Lab Core, no de una versión 2.

## Fuentes permitidas

- NVD CVE API para CVE y metadatos.
- CISA KEV para vulnerabilidades explotadas activamente.
- GitHub API para repositorios candidatos.
- GitHub Security Advisories cuando aplique.
- Vendor advisories.
- Fuentes manuales aprobadas por el usuario.
- Fuentes internas del laboratorio.

No usar fuentes no verificadas como autoridad única.

## Flujo oficial

1. Ingesta CVE/técnica.
2. Normalización de ID.
3. Consulta NVD.
4. Consulta CISA KEV.
5. Consulta vendor advisory.
6. Búsqueda de repos candidatos.
7. Ranking por confianza.
8. Detección de módulo Ojo de Dios.
9. Creación de knowledge pack.
10. Revisión Mistral/LaIA.
11. Validación X5/OjoRouter.
12. Propuesta Hermes.
13. Sandbox si procede.
14. Aprobación usuario.
15. Promoción o archivo.

## Estructura documental prevista

```text
storage/runtime/technique_knowledge/<technique_id>/knowledge_pack.json
```

Este path es documental para futuras rondas. Esta ronda no crea storage, JSON runtime ni lógica de generación.

## Campos obligatorios del knowledge pack

- `technique_id`
- `module_id`
- `source_type`
- `cve_id`
- `title`
- `summary`
- `affected_products`
- `affected_versions`
- `severity`
- `cvss`
- `kev_known_exploited`
- `vendor_sources`
- `nvd_sources`
- `github_candidates`
- `exploit_maturity`
- `safe_lab_strategy`
- `required_permissions`
- `required_tools`
- `required_workers`
- `input_contract`
- `output_contract`
- `evidence_contract`
- `demo_fixture_available`
- `dry_run_supported`
- `controlled_mode_supported`
- `user_implementation_required`
- `recommended_status`
- `confidence`
- `unknowns`
- `created_by`
- `reviewed_by`
- `x5_validation_status`
- `user_approval_status`

## JSON de ejemplo documental

```json
{
  "technique_id": "vuln.example_cve_candidate",
  "module_id": 2,
  "source_type": "cve",
  "cve_id": "CVE-XXXX-YYYY",
  "title": "Example CVE candidate",
  "summary": "Research summary pending validation.",
  "affected_products": [],
  "affected_versions": [],
  "severity": null,
  "cvss": null,
  "kev_known_exploited": false,
  "vendor_sources": [],
  "nvd_sources": [],
  "github_candidates": [],
  "exploit_maturity": "unknown",
  "safe_lab_strategy": "demo_or_dry_run_only_until_approved",
  "required_permissions": [],
  "required_tools": [],
  "required_workers": [],
  "input_contract": {},
  "output_contract": {},
  "evidence_contract": {},
  "demo_fixture_available": false,
  "dry_run_supported": true,
  "controlled_mode_supported": false,
  "user_implementation_required": true,
  "recommended_status": "IMPLEMENTACION_USUARIO_REQUERIDA",
  "confidence": 0.0,
  "unknowns": [],
  "created_by": "DeepSeekAssist",
  "reviewed_by": "Mistral/LaIA",
  "x5_validation_status": "pending",
  "user_approval_status": "required"
}
```

## Reglas de prioridad y autorización

- Una CVE en CISA KEV sube prioridad, pero no autoriza ejecución.
- Una PoC pública no autoriza instalación.
- Un repo popular no autoriza confianza.
- Un exploit mencionado en fuentes públicas no convierte la técnica en funcional.
- Un knowledge pack no equivale a registry productivo.
- Todo pasa por quarantine, analysis, sandbox, evidence, review y approval.
- X5/OjoRouter manda antes de cualquier ejecución permitida.
- Si falta lógica privada del usuario, el estado correcto es `IMPLEMENTACION_USUARIO_REQUERIDA`.

## Salida esperada para Hermes

La propuesta Hermes derivada de un knowledge pack debe incluir:

- módulo candidato;
- técnica candidata;
- fuentes;
- confidence;
- risks;
- permisos;
- modo mínimo;
- evidence contract;
- fixtures requeridos;
- sandbox strategy;
- status recomendado;
- user approval status.


## Tests dinámicos para CVE-to-Technique

El pipeline CVE-to-Technique debe obedecer [Dynamic Registry Testing Policy](DYNAMIC_REGISTRY_TESTING_POLICY.md).

Una CVE nueva, un knowledge pack nuevo, una técnica candidata nueva o una proposal Hermes nueva no deben romper tests por aumentar conteos. El total de técnicas es métrica informativa. Los tests deben validar que cada entrada cumple contrato, estado, permisos, evidence_contract, ausencia de secretos, aprobación requerida y carga por X5/OjoRouter.

Las propuestas derivadas de CVE no cuentan como técnicas productivas hasta promoción controlada.

## Regla final

El pipeline CVE-to-Technique convierte conocimiento en propuesta controlada. No convierte CVEs, PoCs o repositorios en ejecución real automática.
