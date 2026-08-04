# FINE TUNING DECISION POLICY — OJO DE DIOS

## Decisión inicial

No hacer fine-tuning en v0.1.

Usar primero:

- RAG;
- registry;
- evidence;
- scoring;
- prompts;
- JSON Schema;
- tool documentation;
- memory.

## Cuándo considerar fine-tuning

Solo considerar fine-tuning si:

- LaIA falla repetidamente en tareas repetitivas;
- RAG y memoria no bastan;
- hay dataset limpio;
- hay ejemplos suficientes;
- no contiene secretos;
- no contiene credenciales;
- no contiene evidence sensible;
- se puede evaluar antes/después;
- no rompe JSON;
- se mantiene modelo base alternativo.

## Dataset permitido

Solo usar:

- prompts internos sin secretos;
- ejemplos de JSON válidos;
- planes de técnicas;
- explanations;
- evidence summaries anonimizados;
- errores corregidos;
- decisiones de fallback;
- documentación técnica propia.

No usar:

- secretos;
- credenciales;
- datos sensibles reales;
- evidence privada no anonimizada;
- logs con tokens;
- datos de terceros no autorizados.

## Evaluación antes de aceptar fine-tune

Antes de aceptar un fine-tune:

- comparar contra modelo base;
- validar JSON;
- validar planning;
- validar no hallucination;
- validar no stubs funcionales falsos;
- validar registry adherence;
- validar que no ignora permissions;
- validar que no ignora kill switch.


## Extensión Ronda 0-G — Fine-tuning no es requisito inicial

Para v1, la decisión cerrada es: primero RAG local, Knowledge Bootstrap, embeddings cuando estén disponibles, context packs, JSON Schema, memoria estructurada, EvidenceStore, ScoringEngine, ToolHealth, VersionLock, Hermes proposals y evaluación.

Fine-tuning solo se considera después de que RAG/Bootstrap/context packs/evaluación funcionen y exista dataset limpio sin secretos ni datos sensibles. Fine-tuning nunca convierte documentación en funcionalidad ni sustituye X5, registry, permisos o EvidenceStore.

Referencia: [AI_TRAINING_VS_RAG_DECISION.md](AI_TRAINING_VS_RAG_DECISION.md).
