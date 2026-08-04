# AUTONOMOUS OPERATION ENDSTATE — OJO DE DIOS

## Objetivo final

Ojo de Dios debe llegar a operar como plataforma de automatización avanzada.

Cuando el usuario introduce un objetivo autorizado:

1. LaIA interpreta.
2. Attack Surface Graph entiende servicios.
3. X5/OjoRouter valida plan.
4. Workers ejecutan técnicas permitidas.
5. EvidenceStore guarda resultados.
6. LaIA analiza evidence.
7. ScoringEngine aprende.
8. X5 cambia estrategia.
9. Hermes propone mejoras si falta una pieza.
10. El panel gobierna y permite parar.

## No es un simple scanner

Ojo de Dios no debe limitarse a listar hallazgos.

Debe:

- detectar superficie;
- mapear servicios;
- mapear vulnerabilidades;
- seleccionar técnicas;
- preparar parámetros;
- ejecutar mediante X5 si está permitido;
- validar evidence;
- seguir ruta alternativa si falla;
- documentar impacto;
- aprender de resultados.

## Técnicas pendientes

Cuando una técnica requiera lógica privada:

- LaIA prepara parámetros;
- X5 llama al hook;
- el hook devuelve MANUAL_REQUIRED;
- EvidenceStore registra;
- panel muestra dónde implementar;
- Hermes puede proponer estructura/variante en sandbox.

## Realidad operativa

Ojo de Dios debe ser capaz de ejecutar lo que tenga implementado de verdad.

Si una técnica está pendiente, no debe fingir.

Si una técnica tiene lógica real conectada por el usuario, debe:

- ejecutarse mediante worker;
- respetar permisos;
- respetar modo;
- respetar kill switch;
- devolver evidence;
- actualizar scoring;
- permitir análisis de LaIA.

## Evidencia

Evidence puede incluir:

- acceso validado;
- sesión;
- artefacto generado;
- cambio controlado;
- lectura controlada;
- captura;
- reporte;
- señal;
- fichero;
- hash;
- salida de herramienta;
- análisis normalizado.

No se permite declarar éxito sin evidence.
