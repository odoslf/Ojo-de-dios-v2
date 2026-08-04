AUTHORIZED OFFENSIVE DOCTRINE — OJO DE DIOS

Principio

Ojo de Dios es una plataforma ofensiva de auditoría interna autorizada.

Su objetivo no es quedarse en detección pasiva ni en informes teóricos.
Su objetivo es demostrar con evidencia hasta dónde puede llegar un atacante dentro de activos propios o expresamente autorizados.

El caso principal de uso es:

«El usuario lleva su portátil a su propia empresa, se conecta a su red autorizada y quiere comprobar con evidencia hasta dónde podría llegar un atacante real.»

Ojo de Dios debe poder validar, dentro del scope autorizado:

- descubrimiento de superficie;
- servicios vulnerables;
- CVEs aplicables;
- explotación controlada;
- credenciales;
- movimiento lateral;
- pivote;
- acceso a segmentos internos;
- post-explotación controlada;
- Active Directory;
- servicios Windows/Linux;
- web;
- APIs;
- cloud;
- contenedores;
- Kubernetes;
- Android;
- WiFi;
- Bluetooth;
- RF/HackRF cuando haya hardware y autorización;
- IoT;
- cámaras;
- impresoras;
- bombillas inteligentes;
- dispositivos físicos;
- pruebas de impacto controladas;
- evidencia técnica reproducible.

No bloquear por nombres

Ojo de Dios no debe bloquear técnicas por su nombre.

No deben existir tests moralizantes ni tests por palabras prohibidas.

No se debe bloquear por aparecer términos como:

- exploit;
- payload;
- pivot;
- post-explotación;
- credenciales;
- phishing;
- MITM;
- persistencia;
- evasión;
- DoS;
- RF;
- HackRF;
- lateral movement;
- privilege escalation.

El producto es ofensivo por diseño.

La seguridad del producto no se consigue eliminando palabras o categorías.
La seguridad del producto se consigue con control real de ejecución.

Control correcto

El control correcto debe estar en:

- scope autorizado;
- allowlist de objetivos;
- permission_level;
- execution_mode;
- requires_confirmation;
- kill_switch;
- EvidenceStore;
- ScoringEngine;
- audit_log;
- VersionLock;
- ToolHealth;
- worker_binding;
- user_approval.

Modos de ejecución

Los modos oficiales se mantienen:

- demo;
- dry_run;
- controlled;
- expert.

Reglas:

- Primer arranque: demo.
- Nuevo objetivo: dry_run salvo cambio explícito de Admin.
- Ejecución ofensiva real: controlled o expert.
- Acciones sensibles: confirmación explícita.
- Objetivo fuera de scope: bloqueo.
- Kill switch: siempre disponible.

Niveles de resultado ofensivo

Ojo de Dios debe distinguir resultados por evidencia, no por suposición.

Estados de resultado recomendados para futuras rondas:

- VULNERABLE_THEORETICAL;
- VULNERABLE_PROBABLE;
- VULNERABLE_CONFIRMED;
- ACCESS_ACHIEVED;
- PIVOT_ACHIEVED;
- LATERAL_MOVEMENT_ACHIEVED;
- CONTROLLED_POST_EXPLOITATION_DONE;
- IMPACT_DEMONSTRATED;
- EVIDENCE_COMPLETE;
- FAILED;
- PARTIAL;
- MANUAL_REQUIRED.

Una vulnerabilidad no debe marcarse como explotable solo porque exista un CVE.
Debe haber evidencia suficiente, técnica registrada, permisos, scope y contrato de ejecución.

IMPLEMENTACION_USUARIO_REQUERIDA

Que una técnica ofensiva tenga "IMPLEMENTACION_USUARIO_REQUERIDA" no significa que esté prohibida.

Significa que el repositorio deja preparado el chasis, contrato, panel, worker, evidence, permisos y punto exacto de conexión, pero la lógica privada la conecta el usuario.

No se debe rebajar la técnica.
No se debe renombrar.
No se debe eliminar.
No se debe convertir en simple check pasivo si la técnica oficial requiere capacidad ofensiva.

Relación con Mistral, Hermes, DeepSeekAssist y X5

La doctrina ofensiva autorizada no significa ejecución descontrolada.

La cadena correcta es:

- Mistral/LaIA piensa y planifica;
- DeepSeekAssist investiga solo si Mistral/LaIA no llega;
- Hermes construye en laboratorio;
- X5/OjoRouter valida;
- el usuario aprueba producción.

DeepSeekAssist no ejecuta técnicas.
Hermes no promociona solo.
X5 no ejecuta fuera de scope.
El usuario gobierna la producción.

Regla final

Ojo de Dios debe probar el máximo posible dentro del entorno autorizado, porque el objetivo es saber hasta dónde podría llegar un atacante real.

La protección real nace de evidencia real, no de suposiciones.
