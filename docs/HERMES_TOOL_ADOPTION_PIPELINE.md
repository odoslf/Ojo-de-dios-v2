# Hermes Tool Adoption Pipeline

## Propósito

Este documento define el flujo oficial para adoptar técnicas, herramientas, repositorios o capacidades nuevas en Ojo de Dios v0.1 Lab Core sin ejecutar código externo directamente en producción y sin otorgar confianza automática a repositorios públicos, PoCs o respuestas de LLM.

Esto forma parte del diseño base de v0.1 Lab Core, no de una versión 2.

## Flujo oficial

Research → Quarantine → Analyze → Build → Sandbox Test → Evidence → Review → Approval → Promotion

## 1. Research

DeepSeekAssist y/o Mistral/LaIA investigan técnica, CVE, herramienta, repositorio, requisitos, riesgos, fuentes y compatibilidad.

Reglas:

- No se ejecuta nada.
- No se instala nada.
- No se descargan repos externos a producción.
- No se usan fuentes no verificadas como autoridad única.
- La salida obligatoria es JSON validado.
- Si la confianza es baja, el estado debe ser `MANUAL_REVIEW_REQUIRED`.

Salida esperada:

- resumen técnico;
- fuentes consultadas;
- candidates;
- requisitos;
- riesgos;
- unknowns;
- confianza;
- propuesta de siguiente gate.

## 2. Quarantine

Cualquier repo externo se descarga solo en zona de cuarentena.

Reglas:

- Nunca se descarga directo sobre `app/`, `workers/`, `modules/` ni producción.
- Se fija commit SHA.
- Se guarda manifest.
- No se ejecutan scripts del repo externo automáticamente.
- No se usa `.env` real.
- No se guardan secretos.

Ruta documental prevista:

```text
storage/hermes_lab/quarantine/<source>_<repo>_<commit_sha>/
```

Contenido esperado:

```text
source/
manifest.json
sources.json
repo_metadata.json
dependency_inventory.json
static_analysis/
supply_chain/
sandbox_results/
```

## 3. Analyze

La fase Analyze revisa el material en cuarentena antes de cualquier build o prueba.

Controles requeridos:

- Análisis estático.
- Detección de secretos.
- Revisión de dependencias.
- Revisión de licencias.
- Revisión de Dockerfile/scripts.
- Revisión de comportamiento esperado de red.
- Revisión de binarios desconocidos.
- Revisión de permisos requeridos.
- Revisión de mantenimiento del repositorio.

Herramientas documentales permitidas como referencias:

- GitHub REST API para consultar repositorios.
- CodeQL para análisis semántico cuando aplique.
- OpenSSF Scorecard para heurísticas de salud supply-chain.
- Trivy para filesystem/repo/container/SBOM/secrets/misconfig.
- pip-audit para dependencias Python.
- Semgrep como opción de SAST complementaria.
- Sigstore/Cosign/SLSA cuando haya firmas/provenance verificables.

Estas herramientas son referencias documentales para futuras rondas. Este documento no instala ni ejecuta ninguna de ellas.

## 4. Build

Build solo dentro de sandbox.

Reglas:

- Sin secretos.
- Sin `.env` real.
- Sin acceso al repo principal salvo copia controlada.
- Sin privilegios administrativos.
- Sin ejecución en host principal.
- Si necesita red, debe ser red limitada y registrada.
- Si falla, queda como `BUILD_FAILED` o `MANUAL_REVIEW_REQUIRED`.

Build no promociona. Build solo demuestra si el material puede prepararse bajo controles.

## 5. Sandbox Test

Pruebas permitidas:

- fixtures;
- laboratorio propio;
- contenedores vulnerables controlados;
- targets allowlist.

Reglas:

- Nunca contra terceros.
- Nunca en modo real por defecto.
- Debe registrar evidencia.
- Debe respetar kill switch.
- Debe soportar demo/dry_run cuando aplique.
- `controlled_real_test` exige aprobación explícita y activos propios autorizados.

## 6. Evidence

Toda prueba genera evidence manifest.

La evidencia debe indicar:

- `real_execution=false` para demo/fixtures;
- modo;
- target;
- worker;
- herramienta;
- versión;
- hash;
- timestamp;
- resultado;
- errores;
- límites;
- si hubo kill switch o bloqueo.

La evidencia no debe guardar secretos.

## 7. Review

Revisión obligatoria:

- Mistral/LaIA resume resultado.
- X5/OjoRouter valida permisos, scope y evidence contract.
- Hermes prepara diff/propuesta.
- Usuario revisa.

La review debe diferenciar:

- investigación;
- sandbox;
- demo;
- dry_run;
- controlled;
- producción.

## 8. Approval

Nada se promociona sin aprobación del usuario/Admin.

Reglas:

- La aprobación debe quedar registrada.
- El rechazo debe quedar registrado con motivo opcional.
- La aprobación puede limitar modo, targets, módulos o duración.
- La aprobación no elimina controles de scope, allowlist, kill switch ni evidencia.

## 9. Promotion

Reglas de promoción:

- Solo se promociona wrapper/adaptador controlado.
- Nunca se copia el repo externo entero a producción sin revisión.
- La técnica promocionada debe quedar desactivada, demo o dry_run por defecto salvo decisión explícita.
- Si la lógica sensible no está implementada por el usuario, estado obligatorio: `IMPLEMENTACION_USUARIO_REQUERIDA`.
- Promotion debe registrar VersionLock, ToolHealth, registry reload, docs, rollback y audit log.


## Tests dinámicos en adopción de herramientas

La adopción de herramientas debe obedecer [Dynamic Registry Testing Policy](DYNAMIC_REGISTRY_TESTING_POLICY.md).

El pipeline no debe introducir tests que fallen por conteo fijo de wrappers, capabilities, técnicas o proposals. El conteo puede registrarse como métrica informativa, pero la validación debe centrarse en contratos, permisos, estados honestos, evidence, sandbox, approvals, ausencia de secretos y carga por X5/OjoRouter.

Las proposals Hermes no cuentan como técnicas productivas hasta promoción. Los tests deben distinguir `proposal`, `sandbox`, `promoted` y `production`.

## Estados oficiales

- `RESEARCH_DISCOVERED`
- `RESEARCH_IN_PROGRESS`
- `RESEARCH_READY`
- `REPO_CANDIDATES_FOUND`
- `REPO_QUARANTINED`
- `SUPPLY_CHAIN_REVIEW_REQUIRED`
- `STATIC_ANALYSIS_PASSED`
- `STATIC_ANALYSIS_FAILED`
- `BUILD_TEST_PASSED`
- `BUILD_TEST_FAILED`
- `SANDBOX_TEST_PASSED`
- `SANDBOX_TEST_FAILED`
- `LAB_FUNCTIONAL`
- `PROMOTION_REVIEW_REQUIRED`
- `APPROVED_BY_USER`
- `INSTALLED_DISABLED`
- `PROMOTED_TO_REGISTRY`
- `REJECTED`
- `ARCHIVED`
- `MANUAL_REVIEW_REQUIRED`
- `IMPLEMENTACION_USUARIO_REQUERIDA`

## Riesgos oficiales

- `risk_supply_chain`
- `risk_destructive`
- `risk_credentials`
- `risk_persistence`
- `risk_cloud_mutation`
- `risk_rf_transmit`
- `risk_external_network`
- `risk_unknown_binary`
- `risk_untrusted_maintainer`
- `risk_unpinned_dependency`
- `risk_license`
- `risk_prompt_injection`
- `risk_insecure_output_handling`
- `risk_excessive_agency`
- `risk_sensitive_info_disclosure`

## Regla final

Un repo popular no equivale a confianza. Una PoC pública no equivale a instalación. Un hallazgo de DeepSeekAssist no equivale a ejecución. Todo pasa por:

Research → Quarantine → Analyze → Build → Sandbox Test → Evidence → Review → Approval → Promotion
