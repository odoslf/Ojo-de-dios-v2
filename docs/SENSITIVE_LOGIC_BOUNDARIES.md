# SENSITIVE LOGIC BOUNDARIES — OJO DE DIOS

## Principio

El proyecto separa claramente:

- chasis;
- conexión;
- panel;
- worker;
- evidence;
- IA;
- registry;
- lógica privada.

La parte asistida deja preparado el 90% estructural:

- archivos;
- clases;
- campos;
- schemas;
- workers;
- API;
- paneles;
- evidence;
- registry;
- scoring;
- LaIA;
- Hermes;
- X5.

La lógica privada queda para el usuario en:

IMPLEMENTACION_USUARIO_REQUERIDA

## Categorías que deben quedar como lógica privada

- payload generation operativo;
- C2 operativo;
- phishing delivery operativo;
- credential testing operativo;
- explotación real;
- evasión;
- persistencia;
- post-explotación;
- RF transmission;
- jamming;
- cloud mutation;
- Android device actions sensibles;
- parsers privados de entornos propios;
- conectores privados con credenciales;
- bypasses privados;
- cualquier capacidad que el usuario quiera implementar manualmente.

## Qué sí debe crear el chasis

Para esas técnicas el chasis sí debe crear:

- panel específico;
- campos específicos;
- validación de inputs;
- worker binding;
- evidence contract;
- dry_run;
- demo fixture si aplica;
- user_logic_hook;
- documentación;
- estado visible.

## Qué no debe hacer el chasis

No debe:

- fingir ejecución;
- devolver SUCCESS falso;
- ocultar que falta lógica;
- usar placeholders como resultado;
- marcar funcional lo que no lo es;
- ejecutar fuera de registry;
- saltarse permisos;
- saltarse kill switch.
