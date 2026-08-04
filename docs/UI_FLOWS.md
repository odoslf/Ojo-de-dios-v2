# UI FLOWS — OJO DE DIOS

## Flujo principal

1. Usuario abre Ojo de Dios.

2. Pantalla inicial: Nuevo objetivo.

3. Usuario introduce:

   - dominio;
   - IP;
   - rango;
   - URL;
   - Android;
   - HackRF;
   - WiFi;
   - Bluetooth;
   - Cloud;
   - Kubernetes;
   - Docker;
   - Scraping;
   - IoT;
   - repositorio;
   - custom.

4. LaIA interpreta.

5. TargetFingerprint normaliza.

6. Attack Surface Graph se crea si aplica.

7. X5/OjoRouter consulta TechniqueRegistry.

8. LaIA propone plan.

9. Panel muestra:

   - técnicas recomendadas;
   - permisos;
   - evidence esperada;
   - campos que faltan;
   - estado de cada técnica;
   - qué se puede ejecutar;
   - qué requiere lógica privada;
   - qué requiere herramienta;
   - qué requiere hardware.

10. Usuario confirma o ajusta.

11. X5 ejecuta en modo permitido.

12. EvidenceStore guarda.

13. LaIA analiza.

14. ScoringEngine aprende.

15. X5 decide siguiente paso.

16. Hermes puede proponer mejora si falta una pieza.

## Flujo dominio/IP/URL

Cuando el usuario introduce dominio/IP/URL:

- resolver objetivo;
- descubrir superficie;
- detectar puertos;
- detectar servicios;
- detectar tecnologías;
- detectar versiones;
- crear ServiceFingerprint;
- crear Attack Surface Graph;
- mapear técnicas candidatas;
- generar plan LaIA;
- validar con X5;
- ejecutar o dejar pendiente según permisos y estado.

## Flujo Attack Surface

La pestaña Attack Surface debe mostrar:

- hosts;
- puertos;
- servicios;
- productos;
- versiones;
- CPE;
- CVEs candidatas;
- técnicas candidatas;
- permisos;
- estado;
- bloqueos;
- evidence asociada;
- siguiente paso recomendado;
- botón ejecutar con X5;
- botón pedir propuesta Hermes.

## Flujo HackRF

Pantalla HackRF debe tener:

- dispositivo;
- modo automático;
- modo asistido;
- modo experto;
- frecuencia central;
- sample rate;
- ganancia RX;
- ganancia TX;
- modulación;
- duración;
- archivo IQ;
- waterfall;
- evidence;
- confirmación adicional para transmisión.

## Flujo Android

Pantalla Android debe tener:

- análisis APK;
- permisos;
- perfil de laboratorio;
- versión Android;
- APK input;
- parámetros asistidos;
- listener profile;
- output path;
- evidence;
- estado IMPLEMENTACION_USUARIO_REQUERIDA cuando toque.

## Flujo Scraping

Pantalla Scraping debe tener:

- petición en lenguaje natural;
- fuente;
- URL base;
- selectores CSS/XPath;
- límites;
- concurrencia;
- export JSON/CSV;
- usar X4;
- planificar con X5;
- results preview;
- evidence.

## Flujo Hermes

Panel Hermes debe mostrar:

- proposals;
- sandbox;
- diffs;
- evidence;
- Mistral review;
- aprobar;
- rechazar;
- promover;
- archivar;
- rollback.

Hermes nunca debe tocar producción sin aprobación.


## Extensión Ronda 0-G — Panel de estado IA/Hermes Agent

La UI futura de v1 debe incluir panel de estado para Knowledge Base, Mistral/Ollama, embeddings backend, registry index, tools indexed, context packs, JSON schema status, Hermes Agent knowledge, CVE cache, ToolHealth, VersionLock, warnings, stale sources y botones de refresh/rebuild/validate.

El panel puede mostrar rutas y estados, pero no secretos. Sin Knowledge Bootstrap válido, debe avisar que la IA operativa no está lista aunque el sistema arranque en demo.
