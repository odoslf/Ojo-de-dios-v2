MANO DE DIOS — PRODUCT SEPARATION POLICY

Principio

Mano de Dios es un producto separado de Ojo de Dios.

No debe integrarse dentro de Ojo de Dios.
No debe aparecer como módulo oficial de Ojo de Dios.
No debe mezclarse con X5/OjoRouter.
No debe mezclarse con Hermes.
No debe mezclarse con Mistral/LaIA.
No debe mezclarse con DeepSeekAssist.
No debe compartir runtime, registry, workers, rutas, paneles ni schemas funcionales dentro de este repositorio salvo que una ronda futura lo autorice de forma explícita y separada.

Estado normativo

Esta ronda solo documenta la separación.

No crea código para Mano de Dios.
No crea carpetas para Mano de Dios.
No crea rutas.
No crea módulos.
No crea workers.
No crea schemas.
No crea tests.
No crea fixtures.
No crea integraciones.
No modifica runtime.

Regla de producto

Ojo de Dios es la plataforma ofensiva de auditoría interna autorizada definida en este repositorio.

Mano de Dios debe considerarse producto independiente, con ciclo de vida, arquitectura, documentación, permisos, secretos, despliegue y aprobación propios.

Que ambos nombres compartan visión estratégica no significa que compartan implementación.

Separación obligatoria

Mano de Dios no debe usar automáticamente:

- TechniqueRegistry de Ojo de Dios;
- X5/OjoRouter de Ojo de Dios;
- Hermes Agent Lab de Ojo de Dios;
- LaIA/Mistral de Ojo de Dios;
- DeepSeekAssist de Ojo de Dios;
- EvidenceStore de Ojo de Dios;
- ScoringEngine de Ojo de Dios;
- VersionLock de Ojo de Dios;
- ToolHealth de Ojo de Dios;
- workers de Ojo de Dios;
- paneles de Ojo de Dios;
- rutas de Ojo de Dios;
- storage de Ojo de Dios;
- configuración de secretos de Ojo de Dios.

Prohibiciones en este repositorio

No se debe añadir Mano de Dios a:

- los 16 módulos oficiales de Ojo de Dios;
- el registry de técnicas;
- rutas web/API;
- paneles existentes;
- workers;
- pipelines Hermes;
- pipelines DeepSeekAssist;
- tests de runtime;
- scripts;
- tools;
- requirements;
- pyproject.toml;
- .env.example.

Límites de documentación

La documentación de Ojo de Dios puede mencionar Mano de Dios solo para afirmar separación de producto.

No debe definir capacidades operativas internas de Mano de Dios dentro de Ojo de Dios.
No debe convertir Mano de Dios en dependencia de Ojo de Dios.
No debe reservar nombres de módulos internos para Mano de Dios dentro de Ojo de Dios.

Futura relación posible

Si en una ronda futura el usuario decide que ambos productos se comuniquen, deberá hacerse mediante contrato externo explícito, nunca por acoplamiento interno.

Cualquier relación futura deberá definir antes:

- boundary de producto;
- API externa o contrato de intercambio;
- autenticación;
- autorización;
- secretos separados;
- auditoría separada;
- despliegue separado;
- ownership separado;
- aprobación explícita del usuario;
- rollback;
- impacto en scope y evidencias.

Hasta que eso exista, la regla es separación total.

Regla final

Mano de Dios no forma parte de Ojo de Dios.

Ojo de Dios no debe arrastrar, implementar ni simular Mano de Dios.

Cualquier agente futuro que trabaje en este repositorio debe mantener la separación salvo instrucción explícita del usuario en una ronda posterior.
