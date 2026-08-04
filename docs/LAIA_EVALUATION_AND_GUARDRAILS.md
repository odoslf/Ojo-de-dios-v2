# LAIA EVALUATION AND GUARDRAILS — OJO DE DIOS

## Objetivo

LaIA debe evaluarse antes de dejar que sus planes pasen a X5.

## Evaluaciones mínimas

LaIA debe pasar validaciones de:

- JSON válido;
- technique_id existente;
- module_id existente;
- permission_level correcto;
- no inventar herramientas;
- no inventar evidence;
- no marcar stub como funcional;
- respetar IMPLEMENTACION_USUARIO_REQUERIDA;
- respetar MISSING_TOOL;
- respetar HARDWARE_REQUIRED;
- respetar kill switch;
- respetar execution mode;
- pedir confirmación si aplica.

## Tipos de respuesta permitida

LaIA puede devolver:

- plan;
- explanation;
- parameter_fill;
- evidence_analysis;
- fallback_decision;
- hermes_request;
- report_summary.

## Tipos de respuesta no permitida

LaIA no puede devolver:

- comando libre para ejecución directa;
- técnica inexistente;
- success sin evidence;
- cambio de herramienta sin justificación;
- promoción Hermes sin approval;
- ejecución fuera de X5.

## PolicyEngine

Toda acción propuesta por LaIA debe pasar por:

- JSON validator;
- TechniqueRegistry;
- PolicyEngine;
- Permission model;
- Scope/allowlist;
- X5/OjoRouter.
