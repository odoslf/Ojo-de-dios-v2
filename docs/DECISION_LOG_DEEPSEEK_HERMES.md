# Decision Log — DeepSeekAssist, Hermes Tool Adoption and CVE-to-Technique

## Propósito

Este decision log registra decisiones cerradas para DeepSeekAssist, Hermes Agent Lab, Mistral/LaIA, X5/OjoRouter, adopción de herramientas, supply-chain sandbox y CVE-to-Technique en Ojo de Dios v0.1 Lab Core.

Esto forma parte de Ojo de Dios v0.1 Lab Core desde el diseño inicial, no de una versión 2.

## Decisiones cerradas

1. DeepSeekAssist queda aceptado como cerebro externo opcional de investigación, bajo coste y JSON estructurado.
2. DeepSeekAssist no ejecuta, no instala, no toca producción y no decide promociones.
3. Mistral/LaIA sigue siendo cerebro operativo local y revisor contextual.
4. Hermes Agent Lab puede crear propuestas, wrappers, schemas, panel fields, docs, tests estructurales, fixtures y sandbox manifests.
5. Hermes Agent Lab no puede autoaprobarse ni promocionar producción sin usuario.
6. X5/OjoRouter sigue siendo autoridad de validación, permisos, scope, modo, evidence, policy y kill switch.
7. El pipeline oficial queda: Research → Quarantine → Analyze → Build → Sandbox Test → Evidence → Review → Approval → Promotion.
8. Toda herramienta externa entra primero en cuarentena.
9. Toda CVE/técnica nueva pasa por knowledge pack.
10. CISA KEV y NVD sirven para priorizar/informar, no para autorizar ejecución.
11. GitHub/repos públicos pueden servir como candidatos, no como fuente de confianza automática.
12. Tests reales solo en demo, fixtures, laboratorio autorizado o activos propios allowlist.
13. Producción nunca es modo por defecto.
14. Primer arranque sigue en demo; nuevos objetivos siguen en dry_run salvo cambio explícito de Admin.
15. La API key de DeepSeek se documenta solo como placeholder `ALAZAN_REEMPLAZAR_EN_ENV_LOCAL`.
16. No se guardan API keys reales ni casi reales en repo, chat, docs ni `.env.example`.
17. Si una técnica sensible no tiene lógica privada del usuario, queda como `IMPLEMENTACION_USUARIO_REQUERIDA`.
18. No se añaden tests moralizantes por nombres/categorías; solo tests de estructura, contrato, seguridad de ejecución, validación JSON, estados, permisos, evidence, sandbox y approvals.
19. Mano de Dios sigue siendo producto separado y no se mezcla con Ojo de Dios.
20. Esto forma parte de Ojo de Dios v0.1 Lab Core desde el diseño inicial, no de una versión 2.
21. El registry de Ojo de Dios es dinámico: los conteos son métricas informativas, no condiciones bloqueantes.
22. Los tests deben validar invariantes y contratos por técnica, módulo, capability, wrapper o proposal; no números rígidos.

## No desviarse

- No convertir DeepSeek en ejecutor.
- No convertir Hermes en atacante autónomo.
- No permitir comandos libres de modelos.
- No saltarse X5/OjoRouter.
- No descargar repos externos a producción.
- No instalar herramientas en host principal sin proceso.
- No ejecutar PoC contra terceros.
- No guardar secretos.
- No quitar `IMPLEMENTACION_USUARIO_REQUERIDA`.
- No renombrar módulos oficiales.
- No mover DNS a módulo independiente.
- No tocar Módulo 9: Scraping Inteligente X4 + X5 + IA.
- No mezclar Mano de Dios.
- No crear versión 2 para esta base: dejarlo preparado desde v0.1.
- No crear tests bloqueantes por conteo fijo de técnicas, módulos, capabilities, wrappers o proposals.

## Documentos vinculados

- [DeepSeekAssist + Hermes + Mistral/LaIA + X5/OjoRouter](DEEPSEEK_ASSIST_HERMES_PIPELINE.md)
- [Hermes Tool Adoption Pipeline](HERMES_TOOL_ADOPTION_PIPELINE.md)
- [CVE-to-Technique Pipeline](CVE_TO_TECHNIQUE_PIPELINE.md)
- [Supply Chain & Sandbox Policy](SUPPLY_CHAIN_SANDBOX_POLICY.md)
- [AI Research Gates](AI_RESEARCH_GATES.md)
- [Dynamic Registry Testing Policy](DYNAMIC_REGISTRY_TESTING_POLICY.md)

## Regla final

La arquitectura nace preparada para evolución controlada desde v0.1 Lab Core. No se pospone a una versión 2 y no se permite saltarse los gates para acelerar adopciones.
