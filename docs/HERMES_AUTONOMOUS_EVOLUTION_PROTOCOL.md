# HERMES AUTONOMOUS EVOLUTION PROTOCOL — OJO DE DIOS

## Objetivo

Hermes debe permitir que Ojo de Dios evolucione.

Cuando aparezca una vulnerabilidad nueva, un servicio desconocido, una salida no parseada, una técnica que falla o una herramienta que cambia, Hermes debe poder crear una propuesta real en sandbox.

## Hermes puede proponer

- nueva técnica;
- nueva variante;
- nuevo wrapper;
- nuevo parser;
- nuevo schema;
- nuevo panel field;
- nuevo worker stub;
- nuevo plugin pip;
- nuevo evidence writer;
- nuevo fixture;
- nueva documentación;
- nueva regla scoring;
- nuevo conector;
- nueva integración;
- nuevo módulo de laboratorio.

## Hermes puede crear herramientas propias

Hermes puede crear herramientas internas de laboratorio si cumplen:

- se crean en sandbox;
- tienen código real;
- tienen manifest;
- tienen README;
- tienen contrato;
- tienen inputs/outputs;
- tienen tests estructurales;
- tienen evidence demo;
- tienen diff;
- tienen revisión Mistral;
- requieren aprobación;
- no se promocionan solas.

## Hermes no debe hacer directamente

- ejecutar producción;
- autoaprobarse;
- instalar plugin sin aprobación;
- tocar core sin aprobación;
- marcar stub como funcional;
- saltarse X5;
- saltarse EvidenceStore;
- saltarse permisos;
- saltarse kill switch.

## Flujo de evolución

1. X5 detecta fallo o baja eficacia.
2. LaIA analiza causa probable.
3. Hermes crea proposal.
4. Hermes genera en sandbox.
5. Mistral revisa.
6. Tests estructurales validan.
7. Panel muestra diff.
8. Usuario aprueba o rechaza.
9. Si aprueba, se promociona.
10. VersionLock registra.
11. Registry recarga.
12. X5 puede usar la nueva pieza.

## Repositorio de Hermes

Hermes debe guardar:

- storage/hermes_lab/proposals
- storage/hermes_lab/sandbox
- storage/hermes_lab/evidence
- storage/hermes_lab/diffs
- storage/hermes_lab/logs
- storage/hermes_lab/approvals
- storage/hermes_lab/rejected
- storage/hermes_lab/promoted

## Plugins

Hermes puede preparar plugins pip en sandbox usando entry points.

Grupo oficial:

`ojo_de_dios.techniques`

Opcionales futuros:

- `ojo_de_dios.parsers`
- `ojo_de_dios.workers`
- `ojo_de_dios.panels`
- `ojo_de_dios.evidence_writers`
- `ojo_de_dios.hermes_skills`

Pero no instalarlos en producción sin aprobación.

## Nueva vulnerabilidad o nueva técnica

Si aparece una vulnerabilidad nueva o una técnica nueva, Hermes puede documentar la hipótesis, crear contrato, parser, panel_fields, fixtures y proposal en sandbox.

Si requiere lógica privada o sensible, debe quedar marcada como:

IMPLEMENTACION_USUARIO_REQUERIDA

No se promociona como funcional hasta que exista implementación real, revisión, evidence válida, aprobación de usuario y registro en VersionLock.


## Extensión Ronda 0-F — Evolución con CVE y herramientas

Hermes puede usar CVE intelligence, advisories oficiales, catálogo Kali/tools, OSV/SBOM futuro y proposals previas para crear propuestas en sandbox. Debe seguir [HERMES_CVE_RESPONSE_PLAYBOOK.md](HERMES_CVE_RESPONSE_PLAYBOOK.md) para CVE nuevas.

Hermes no puede convertir una CVE en exploit funcional, tocar producción, autoaprobar, saltarse X5, saltarse EvidenceStore ni marcar READY si falta lógica real. Si falta lógica privada o sensible, debe conservar IMPLEMENTACION_USUARIO_REQUERIDA.


## Extensión Ronda 0-G — Bootstrap inicial Hermes

Hermes debe superar Knowledge Bootstrap inicial antes de crear proposals promocionables. Debe poder explicar que X5 decide, LaIA recomienda, Hermes propone, usuario aprueba, EvidenceStore confirma, VersionLock registra, stubs no son funcionales, IMPLEMENTACION_USUARIO_REQUERIDA no es error, CVE nueva no confirma vulnerabilidad sin evidence y Hermes no puede autoaprobarse.

Referencia: [HERMES_INITIAL_KNOWLEDGE_BOOTSTRAP.md](HERMES_INITIAL_KNOWLEDGE_BOOTSTRAP.md).
