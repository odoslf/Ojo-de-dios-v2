# LAIA MEMORY AND SCORING — OJO DE DIOS

## Objetivo

LaIA debe aprender de resultados reales mediante memoria estructurada y scoring.

No se trata de entrenar pesos al principio.

## Qué guardar por ejecución

Por cada ejecución:

- target_id;
- target_type;
- module_id;
- technique_id;
- tool_id;
- worker_id;
- parameters_hash;
- mode;
- status;
- evidence_quality;
- duration;
- failure_reason;
- blocked_reason;
- success_markers;
- scoring_before;
- scoring_after;
- LaIA_summary;
- next_recommended_techniques;
- hermes_requested;
- hermes_proposal_id si aplica.

## Cómo aprende

ScoringEngine ajusta:

- eficacia por técnica;
- eficacia por tipo de servicio;
- eficacia por módulo;
- eficacia por target_type;
- eficacia por herramienta;
- eficacia por versión;
- errores frecuentes;
- rutas que funcionan;
- rutas que fallan;
- cuándo conviene pedir Hermes.

## No inventar aprendizaje

Si no hay evidence:

LaIA no debe decir que aprendió.

Debe devolver:

NO_EVIDENCE_TO_LEARN
