# DeepSeekAssist + Hermes + Mistral/LaIA + X5/OjoRouter

## Propósito

Este documento define la arquitectura normativa para que DeepSeekAssist, Hermes Agent Lab, Mistral/LaIA y X5/OjoRouter puedan investigar, preparar, probar en sandbox, validar y promocionar nuevas técnicas, herramientas y CVEs de forma controlada dentro de Ojo de Dios v0.1 Lab Core.

Esto forma parte del diseño base de v0.1 Lab Core, no de una versión 2.

## Principios cerrados

- DeepSeekAssist no es ejecutor.
- DeepSeekAssist no instala herramientas.
- DeepSeekAssist no toca producción.
- DeepSeekAssist investiga, compara fuentes, resume, estructura y devuelve JSON.
- DeepSeekAssist debe integrarse como cerebro externo opcional de mínimo coste, no como autoridad final.
- Mistral/LaIA revisa localmente la coherencia con Ojo de Dios.
- Hermes Agent Lab crea propuestas, wrappers, schemas, panel fields, docs, fixtures, tests estructurales y expedientes de sandbox.
- X5/OjoRouter valida permisos, scope, modo, target, evidence contract, policy, kill switch y aprobación.
- El usuario aprueba o rechaza promociones.
- Ningún modelo puede ejecutar comandos libres.
- Ningún modelo puede promocionar código a producción por sí solo.

## API key de DeepSeek

La API key real de DeepSeek nunca debe documentarse ni almacenarse en el repositorio.

No debe guardarse en:

- documentación;
- `.env.example`;
- commits;
- logs;
- fixtures;
- prompts;
- outputs de LLM;
- expedientes de sandbox;
- evidence.

Placeholder permitido para documentación y futuras variables locales privadas:

```env
DEEPSEEK_API_KEY=ALAZAN_REEMPLAZAR_EN_ENV_LOCAL
```

`ALAZAN_REEMPLAZAR_EN_ENV_LOCAL` no es una clave real. El usuario la sustituirá solo en su entorno local privado cuando exista implementación futura.

## Tabla de responsabilidades

| Actor | Responsabilidades permitidas | Prohibiciones |
| --- | --- | --- |
| DeepSeekAssist | `research_cve_or_technique`, `compare_sources`, `find_candidate_repositories`, `summarize_requirements`, `produce_strict_json`, `estimate_confidence`, `flag_unknowns` | `no_execute`, `no_install`, `no_promote` |
| Mistral/LaIA | `local_project_context_review`, `module_mapping`, `explain_to_user`, `evidence_summary`, `false_positive_reasoning`, `plan_simplification` | `no_free_command_execution` |
| Hermes Agent Lab | `create_proposal`, `create_wrapper_stub`, `create_schema`, `create_panel_fields`, `create_evidence_contract`, `create_docs`, `create_structural_tests`, `create_sandbox_manifest`, `prepare_diff`, `request_user_approval` | `never_auto_approve`, `never_write_production_directly` |
| X5/OjoRouter | `validate_registry_state`, `validate_permission_level`, `validate_scope`, `validate_target_allowlist`, `validate_execution_mode`, `validate_evidence_contract`, `enforce_kill_switch`, `block_if_unapproved`, `decide_execution_allowed` | No debe saltarse scope, allowlist, permisos, policy, evidence ni aprobación |
| Usuario/Admin | `approve_reject`, `configure_allowlists`, `enable_controlled_mode`, `promote_or_archive`, `provide_private_logic_where_required` | No debe guardar secretos reales en el repositorio |

## Flujo de coordinación

1. El usuario/Admin define una necesidad autorizada: técnica, herramienta, CVE, integración o mejora.
2. Mistral/LaIA revisa primero documentación local, Knowledge Base, registry, EvidenceStore, ToolHealth y VersionLock.
3. Si falta conocimiento moderno, Mistral/LaIA puede solicitar investigación externa mínima a DeepSeekAssist.
4. DeepSeekAssist devuelve JSON estructurado, corto, con fuentes, confianza y unknowns.
5. Mistral/LaIA revisa si el JSON encaja con módulos, técnicas, políticas y arquitectura de Ojo de Dios.
6. Hermes Agent Lab prepara proposal, wrapper/adaptador documental, schemas, panel fields, evidence contract, docs, fixtures, tests estructurales y sandbox manifest cuando proceda.
7. X5/OjoRouter valida registry state, permission_level, scope, target allowlist, execution_mode, evidence contract, policy y kill switch.
8. El usuario/Admin aprueba, rechaza o archiva.
9. Solo tras aprobación puede entrar en flujo de promoción controlada.
10. Si falta lógica privada sensible, la técnica queda en `IMPLEMENTACION_USUARIO_REQUERIDA`.

## Salida JSON mínima de DeepSeekAssist

Toda respuesta futura de DeepSeekAssist debe ser JSON estructurado y validable.

Campos mínimos recomendados para rondas futuras:

```json
{
  "kind": "deepseek_research_result",
  "topic": "cve_or_technique_or_tool",
  "summary": "",
  "sources": [],
  "candidate_repositories": [],
  "requirements": [],
  "module_mapping_candidates": [],
  "confidence": 0.0,
  "unknowns": [],
  "risks": [],
  "recommended_next_gate": "review_required",
  "requires_hermes_proposal": true,
  "requires_user_approval": true
}
```

Este JSON no autoriza ejecución. X5/OjoRouter debe validarlo antes de cualquier acción posterior.

## Reglas finales

- DeepSeekAssist investiga, no ejecuta.
- Mistral/LaIA revisa coherencia local, no ejecuta comandos libres.
- Hermes Agent Lab propone y construye en sandbox, no autoaprueba.
- X5/OjoRouter manda en validación, scope, permisos, evidencia, kill switch y ejecución permitida.
- El usuario/Admin decide promoción o archivo.
- Producción nunca es modo por defecto.
- Todo lo sensible sin lógica privada del usuario queda como `IMPLEMENTACION_USUARIO_REQUERIDA`.
