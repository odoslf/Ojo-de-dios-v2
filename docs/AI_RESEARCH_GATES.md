# AI Research Gates

## Propósito

Este documento define gates obligatorios para investigación IA, adopción de herramientas y conversión CVE-to-Technique en Ojo de Dios v0.1 Lab Core.

Los gates aplican a DeepSeekAssist, Mistral/LaIA, Hermes Agent Lab, X5/OjoRouter y cualquier agente futuro. Ningún gate autoriza ejecución por sí solo.

## Gate 0 — Input sanity

- Validar petición.
- Validar módulo.
- Validar técnica.
- Validar que no hay secretos en prompt.
- Validar que no se envían claves a DeepSeek/Mistral.

## Gate 1 — Source validation

- Cada afirmación importante debe tener fuente.
- Prioridad: vendor, NVD, CISA, GitHub oficial, advisory reconocido.
- Repos externos no son autoridad única.

## Gate 2 — JSON validation

- DeepSeek y Mistral devuelven JSON estructurado.
- Si JSON no valida, X5 bloquea.
- Si faltan campos obligatorios, X5 bloquea.
- Si hay baja confianza, pasa a review_required.

## Gate 3 — Policy validation

- Permisos.
- Scope.
- Target.
- Modo.
- Usuario.
- Kill switch.
- Estado de técnica.
- Hardware requerido.
- Credenciales prohibidas si no toca.
- Producción bloqueada si no hay aprobación.

## Gate 4 — Quarantine validation

- Repo externo solo en cuarentena.
- Commit fijado.
- Manifest creado.
- Escaneos pendientes o completados.
- Sin ejecución todavía.

## Gate 5 — Supply-chain validation

- Dependencias revisadas.
- Secretos revisados.
- Licencias revisadas.
- Scripts revisados.
- Binarios revisados.
- Dockerfile revisado.
- Mantenibilidad revisada.
- Riesgos documentados.

## Gate 6 — Sandbox validation

- Build/smoke/demo/lab según modo.
- Sin secretos.
- Logs.
- Timeout.
- Kill switch.
- Evidence.

## Gate 7 — Human approval

- Usuario/Admin aprueba, rechaza o archiva.
- Sin aprobación no hay promoción.

## Gate 8 — Promotion validation

- Promocionar wrapper/adaptador, no repo bruto.
- Estado correcto.
- Tests estructurales.
- Evidence contract.
- Panel fields.
- Registry.
- Docs.
- Changelog.
- Rollback documentado.

## Errores bloqueantes

- LLM output no validado.
- Fuente única no fiable.
- Repo sin commit fijo.
- Dependencia no fijada en propuesta.
- Script opaco.
- Binario desconocido.
- Requiere privilegios altos sin justificación.
- Intenta leer secretos.
- Intenta persistencia.
- Intenta red real sin aprobación.
- Falta kill switch.
- Falta evidence contract.
- Falta aprobación usuario.
- Contradice IMPLEMENTACION_USUARIO_REQUERIDA.

## Regla final

Los gates convierten investigación IA en decisiones controladas. No convierten outputs de LLM, PoCs, CVEs ni repositorios en ejecución automática.
