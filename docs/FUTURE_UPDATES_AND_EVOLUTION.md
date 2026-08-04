# FUTURE UPDATES AND EVOLUTION — OJO DE DIOS

## Objetivo

Ojo de Dios está diseñado para crecer continuamente.

Debe poder incorporar:

- nuevas técnicas;
- nuevas herramientas;
- nuevas versiones;
- nuevos parsers;
- nuevos wrappers;
- nuevos workers;
- nuevos panel fields;
- nuevos evidence schemas;
- nuevos plugins pip;
- nuevas skills Hermes;
- nuevas fuentes X4;
- nuevos modelos IA;
- nuevos backends LLM;
- nuevos dispositivos hardware.

## Regla de evolución

Nada nuevo debe romper:

- los 16 módulos oficiales;
- TechniqueRegistry;
- EvidenceStore;
- X5/OjoRouter;
- LaIA JSON;
- Hermes sandbox;
- VersionLock;
- Kill Switch;
- Demo mode;
- Windows first-run;
- tests funcionales.

## Tipos de actualización

### 1. Actualización de herramienta oficial

Ejemplo:
Nmap 7.99 → versión superior.

Debe:

- actualizar VersionLock;
- mantener technique_id;
- validar salida;
- actualizar parser si cambia formato;
- no romper evidence contract;
- documentar cambio.

### 2. Nueva técnica dentro de módulo existente

Ejemplo:
Nueva técnica HackRF o Android.

Debe:

- ir dentro del módulo oficial correspondiente;
- no crear módulo nuevo si encaja en uno existente;
- tener archivo propio;
- clase propia;
- panel_fields;
- input_schema;
- worker;
- evidence_contract;
- permission_level;
- demo/dry_run behavior.

### 3. Nueva herramienta alternativa superior

Solo se acepta si:

- mejora técnicamente;
- no elimina la herramienta oficial anterior sin aprobación;
- queda documentada;
- queda en VersionLock;
- tiene wrapper propio;
- tiene evidence contract.

### 4. Nuevo parser

Debe:

- vivir como parser separado;
- tener fixture;
- tener expected output;
- no cambiar técnica base;
- registrar versión;
- registrar evidence.

### 5. Nuevo plugin pip

Debe:

- cumplir Plugin Compatibility Contract;
- usar entry point oficial;
- pasar validación;
- no romper arranque si falla;
- poder desactivarse.

### 6. Nueva creación Hermes

Debe:

- generarse en sandbox;
- tener manifest;
- tener diff;
- tener evidence;
- tener revisión Mistral;
- tener approval;
- tener promoción controlada.

## Regla anti-caos

No se acepta una actualización que:

- cambie nombres oficiales sin migración;
- elimine técnicas;
- sustituya herramientas por otras más suaves;
- marque stubs como funcionales;
- rompa paneles;
- rompa registry;
- rompa evidence;
- rompa X5;
- rompa LaIA JSON.


## Extensión Ronda 0-F — Actualizaciones de conocimiento externo

Las actualizaciones futuras de CVE, herramientas Kali, OSV/SBOM, Nuclei templates o advisories de fabricantes deben entrar como conocimiento controlado, no como ejecución automática.

Proceso mínimo:

1. Ingesta documental o cache normalizada.
2. Precedencia de fuentes.
3. Context pack mínimo.
4. Validación X5/registry/permisos/scope.
5. EvidenceStore si hay resultado real.
6. ScoringEngine solo con evidence.
7. Hermes proposal si falta wrapper/parser/schema/panel/tool doc.
8. Approval + Promotion Pipeline + VersionLock para disponibilidad.

Referencias: [VULNERABILITY_INTELLIGENCE_PIPELINE.md](VULNERABILITY_INTELLIGENCE_PIPELINE.md), [KALI_TOOL_KNOWLEDGE_CATALOG.md](KALI_TOOL_KNOWLEDGE_CATALOG.md), [HERMES_CVE_RESPONSE_PLAYBOOK.md](HERMES_CVE_RESPONSE_PLAYBOOK.md).


## Extensión Ronda 0-G — Evolución dependiente de Knowledge Bootstrap

Toda evolución futura de LaIA/Hermes Agent, CVE intelligence, tools, plugins, templates o proposals debe refrescar Knowledge Base y actualizar el panel de estado. Una propuesta nueva no debe tratarse como disponible hasta que Knowledge Refresh, source precedence, approval, VersionLock y registry reload reflejen el cambio.

Fine-tuning sigue siendo posterior y condicionado a evaluación; no es vía inicial ni requisito v1.
