# ARCHITECTURE LOCK — OJO DE DIOS

## Propósito

Este documento bloquea las decisiones de arquitectura de Ojo de Dios para evitar improvisación, cambios de dirección no revisados y pérdida de contexto entre asistentes, colaboradores o chats futuros.

## Decisiones no negociables

- Ojo de Dios es una plataforma modular local de auditoría interna/laboratorio.
- La primera versión oficial es Ojo de Dios v0.1 Lab Core.
- Son 16 módulos oficiales y visibles.
- DNS no es módulo independiente.
- El Módulo 9 no se cambia: Scraping Inteligente X4 + X5 + IA.
- X5/OjoRouter manda la ejecución y orquestación.
- LaIA/Mistral es cerebro operativo y debe devolver JSON validado.
- Hermes Agent Lab / Evolution Engine evoluciona el sistema en sandbox, no en producción directa.
- EvidenceStore, ScoringEngine, VersionLock, Kill Switch y Demo mode son obligatorios.
- La pantalla inicial es `/targets/new`, con nombre Nuevo objetivo.
- El Dashboard existe, pero no es la pantalla inicial.
- Windows 10 LTSC es entorno principal.
- SQLite va primero, PostgreSQL queda preparado.
- Web responsive va primero y la API debe quedar preparada para Android.
- X4/Cantera IQ se aprovecha como referencia y conector de scraping.
- X5 existente se aprovecha como referencia arquitectónica, no como copia directa.
- IMPLEMENTACION_USUARIO_REQUERIDA debe estar visible donde falte lógica privada o sensible.


## Decisiones bloqueadas de evolución

28. Ojo de Dios debe soportar expansión por plugins pip.
29. Ojo de Dios debe soportar promoción controlada de propuestas Hermes.
30. Ojo de Dios debe usar VersionLock para herramientas, plugins y creaciones promovidas.
31. Cambios incompatibles requieren migración y versión mayor.
32. Nuevas técnicas deben añadirse por contrato, no tocando 50 archivos.
33. Herramientas creadas por Hermes deben pasar por sandbox, manifest, evidence, review, approval y promotion.

Estas decisiones se detallan en:

- [FUTURE_UPDATES_AND_EVOLUTION.md](FUTURE_UPDATES_AND_EVOLUTION.md)
- [HERMES_PROMOTION_PIPELINE.md](HERMES_PROMOTION_PIPELINE.md)
- [PLUGIN_COMPATIBILITY_CONTRACT.md](PLUGIN_COMPATIBILITY_CONTRACT.md)
- [MODULE_EXTENSION_PLAYBOOK.md](MODULE_EXTENSION_PLAYBOOK.md)
- [TOOL_ADOPTION_PLAYBOOK.md](TOOL_ADOPTION_PLAYBOOK.md)
- [RELEASE_AND_MIGRATION_POLICY.md](RELEASE_AND_MIGRATION_POLICY.md)
- [BACKWARD_COMPATIBILITY_POLICY.md](BACKWARD_COMPATIBILITY_POLICY.md)
- [HERMES_CREATED_TOOLS_LIFECYCLE.md](HERMES_CREATED_TOOLS_LIFECYCLE.md)


## Decisiones bloqueadas de conocimiento LaIA

34. LaIA no dependerá solo del prompt.
35. LaIA usará Knowledge Base/RAG local.
36. LaIA consultará Registry, ToolHealth, VersionLock, Evidence, Scoring, Hermes Agent y plugins.
37. Fine-tuning no se hará en v0.1 salvo decisión futura.
38. Toda acción operativa de LaIA debe devolver JSON validado.
39. LaIA usará context packs por tarea.
40. Knowledge Base debe refrescarse cuando cambien docs, registry, tools, evidence, plugins o Hermes.

Estas decisiones se detallan en:

- [LAIA_KNOWLEDGE_BASE.md](LAIA_KNOWLEDGE_BASE.md)
- [LAIA_RAG_ARCHITECTURE.md](LAIA_RAG_ARCHITECTURE.md)
- [TOOL_DOCUMENTATION_INGESTION.md](TOOL_DOCUMENTATION_INGESTION.md)
- [LAIA_MEMORY_AND_SCORING.md](LAIA_MEMORY_AND_SCORING.md)
- [LOCAL_MODEL_BACKENDS.md](LOCAL_MODEL_BACKENDS.md)
- [FINE_TUNING_DECISION_POLICY.md](FINE_TUNING_DECISION_POLICY.md)
- [LAIA_EVALUATION_AND_GUARDRAILS.md](LAIA_EVALUATION_AND_GUARDRAILS.md)
- [KNOWLEDGE_REFRESH_PIPELINE.md](KNOWLEDGE_REFRESH_PIPELINE.md)
- [LAIA_CONTEXT_PACKS.md](LAIA_CONTEXT_PACKS.md)

## Índice oficial de módulos bloqueado

1. OSINT
2. Vulnerabilidades
3. Explotación servicios de red
4. Intrusión web avanzada
5. Credenciales
6. MITM / Red
7. Post-explotación
8. DoS / Resiliencia
9. Scraping Inteligente X4 + X5 + IA
10. Wireless / RF general
11. IoT / físicos
12. Orquestación X5 + IA + Hermes Agent Lab
13. Android
14. Phishing
15. Cloud / Containers / Kubernetes
16. Excelencia operativa / Evidence / Calidad / Mantenimiento

## Distribución DNS bloqueada

DNS queda repartido en:

- Módulo 1 OSINT: subdominios, AXFR, registros, reverse DNS.
- Módulo 2 Vulnerabilidades: subdomain takeover y DNS misconfig.
- Módulo 6 MITM / Red: DNS spoofing, túneles DNS y cache poisoning/SAD DNS.

No crear módulo DNS independiente.

## Capas transversales

- TargetFingerprint.
- Attack Surface Graph.
- Service Intelligence Graph.
- TechniqueRegistry.
- PolicyEngine.
- JobRunner.
- EvidenceStore.
- ScoringEngine.
- VersionLock.
- Kill Switch.
- Demo mode.
- Hermes Agent Lab.
- LaIA/Mistral.
- X5/OjoRouter.

## Modos operativos bloqueados

Primer arranque: `demo`.

Nuevos objetivos: `dry_run`.

Modos activables por admin: `controlled` y `expert`.

Nunca debe existir ejecución real por defecto.

## Reglas de cambio

Antes de cambiar arquitectura, un colaborador debe:

1. leer el README y los documentos raíz en el orden indicado;
2. comprobar que el cambio no contradice decisiones cerradas;
3. documentar el motivo;
4. mantener visibilidad de IMPLEMENTACION_USUARIO_REQUERIDA;
5. conservar compatibilidad con crecimiento de técnicas;
6. no añadir tests por palabras, categorías o juicios externos.

## Tests permitidos

Los tests solo deben validar funcionalidad real:

- contratos;
- imports;
- rutas;
- schemas;
- registry;
- workers;
- evidence;
- estados;
- permisos;
- comportamiento demo/dry_run;
- kill switch;
- healthcheck.

No se permiten tests moralizantes ni tests que bloqueen técnicas por nombre o categoría.


## Lock adicional — Conocimiento, CVE y evolución

El orden de verdad para conocimiento queda delegado a [KNOWLEDGE_SOURCE_PRECEDENCE.md](KNOWLEDGE_SOURCE_PRECEDENCE.md). LaIA/Mistral y Hermes Agent deben ingerir por Knowledge Base local, RAG, context packs, registry, ToolHealth, VersionLock, EvidenceStore, ScoringEngine, Attack Surface Graph, proposals/promoted Hermes Agent y CVE intelligence documentada.

Queda bloqueado:

- usar documentación aspiracional como funcionalidad real;
- permitir que LaIA ejecute comandos libres;
- permitir que Hermes se autoapruebe;
- declarar una CVE como explotable sin evidence;
- declarar una herramienta Kali como técnica disponible solo porque está documentada o instalada;
- saltarse X5/OjoRouter, permisos, scope, registry, EvidenceStore, VersionLock o Kill Switch.

Documentos de referencia: [LAIA_HERMES_INGESTION_AND_EVOLUTION_BLUEPRINT.md](LAIA_HERMES_INGESTION_AND_EVOLUTION_BLUEPRINT.md), [VULNERABILITY_INTELLIGENCE_PIPELINE.md](VULNERABILITY_INTELLIGENCE_PIPELINE.md), [KALI_TOOL_KNOWLEDGE_CATALOG.md](KALI_TOOL_KNOWLEDGE_CATALOG.md) y [HERMES_CVE_RESPONSE_PLAYBOOK.md](HERMES_CVE_RESPONSE_PLAYBOOK.md).


## Lock Ronda 0-G — Knowledge Bootstrap v1

Decisiones bloqueadas:

- Knowledge Bootstrap es requisito v1.
- LaIA no opera solo con prompt gigante.
- Hermes no crea proposals promocionables sin Knowledge Bootstrap OK.
- Fine-tuning no es requisito inicial.
- RAG/context packs/JSON/memoria/evidence/scoring son prioridad.
- El sistema debe degradar si Knowledge Base está STALE/FAILED.
- Panel IA/Hermes Agent debe mostrar estado de conocimiento.
- No se indexan secretos.

Referencias: [AI_KNOWLEDGE_BOOTSTRAP_V1_REQUIREMENT.md](AI_KNOWLEDGE_BOOTSTRAP_V1_REQUIREMENT.md), [AI_FIRST_RUN_KNOWLEDGE_LOAD.md](AI_FIRST_RUN_KNOWLEDGE_LOAD.md), [AI_KNOWLEDGE_REFRESH_AND_STATUS_PANEL.md](AI_KNOWLEDGE_REFRESH_AND_STATUS_PANEL.md), [HERMES_INITIAL_KNOWLEDGE_BOOTSTRAP.md](HERMES_INITIAL_KNOWLEDGE_BOOTSTRAP.md), [AI_TRAINING_VS_RAG_DECISION.md](AI_TRAINING_VS_RAG_DECISION.md).
