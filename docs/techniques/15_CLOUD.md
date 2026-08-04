# MÓDULO 15 — CLOUD / CONTENEDORES / KUBERNETES

## Ronda 1 — Base documental del módulo

### 1. Objetivo

Establecer la base documental del Módulo 15. Solo documentación. No implementar código, endpoints, workers, base de datos, tests, requirements ni scripts funcionales. Todo queda como especificación de producto y laboratorio.

### 2. Ubicación

Este contenido se registra en `docs/techniques/15_CLOUD.md` como primera sección documental del módulo.

### 3. Filosofía del módulo

Este módulo audita infraestructura cloud moderna: contenedores Docker, orquestadores Kubernetes y servicios en AWS, Azure y GCP. No se limita a escanear puertos por defecto. Utiliza fingerprinting real de servicios para identificar exactamente qué hay detrás de cada puerto, sin asumir nada.

La IA Mistral planifica los ataques, X5 ejecuta y Hermes evoluciona el arsenal si aparecen nuevas tecnologías o protecciones. El usuario puede elegir entre modo `Verificación` (sin dejar huella) y modo `Persistencia` (despliegue de mecanismos de permanencia), siempre con confirmación explícita.

### 4. Herramientas y versiones en Kali WSL2 con VersionLock

- Trivy 0.52: `sudo apt install trivy`
- kube-hunter 1.8: `sudo apt install kube-hunter`
- kubeletctl 1.0: `git clone https://github.com/cyberark/kubeletctl`
- CDK 1.0: `git clone https://github.com/cdk-team/CDK`
- Peirates 1.1: `git clone https://github.com/inguardians/peirates`
- Scout Suite 5.13: `sudo apt install scoutsuite`
- Prowler 4.0: `sudo apt install prowler`
- cloudsplaining 0.1: `pip install cloudsplaining`
- kubectl 1.30: `sudo apt install kubectl`
- docker 26.1: `sudo apt install docker.io`
- nmap 7.99: `sudo apt install nmap` (scripts NSE para fingerprinting)
- WhatWeb 0.5.5: `sudo apt install whatweb` (fingerprinting HTTP)
- Dolphin Mistral Nemo 12B (LaIA): planificación, relleno de parámetros y sugerencias.
- Hermes (DeepSeek API): creación de módulos para nuevas tecnologías.

### 5. Panel de control y subpáginas

La pestaña `Cloud` en Ojo de Dios se divide en tres subpestañas.

#### 5.1 Contenedores (Docker)

- Visor de APIs Docker detectadas por fingerprinting real, no por puerto por defecto. Muestra IP, puerto, versión de Docker y autenticación requerida.
- Botones: `Ejecutar comando`, `Breakout al host`, `Escanear imagen`, `Robar secretos`.
- Indicador del modo seleccionado: `Verificación` (por defecto) o `Persistencia`.

#### 5.2 Kubernetes

- Visor de clústeres K8s detectados, con pods, servicios, secretos y RBAC.
- Botones: `Robar secretos`, `Escalar privilegios`, `Desplegar pod persistente`.
- Indicador del modo seleccionado.

#### 5.3 Cloud (AWS / Azure / GCP)

- Visor de recursos cloud enumerados (instancias, buckets, usuarios IAM, etc.).
- Botones: `Extraer credenciales IMDS`, `Analizar IAM`, `Persistencia cloud`.
- Indicador del modo seleccionado.

### 6. Fingerprinting real de servicios

Antes de ejecutar cualquier técnica, el módulo identifica el servicio real detrás de cada puerto abierto, sin importar el número de puerto:

- Escaneo con nmap y scripts NSE (`http-title`, `ssl-cert`, `docker-version`).
- Análisis de banners y respuestas HTTP con WhatWeb.
- Para APIs, envío de peticiones de prueba, por ejemplo `GET /version` a una posible API Docker o `GET /api/v1` a una posible API K8s.
- El resultado del fingerprinting se muestra en el panel: `Puerto 1500 → API Docker v26.1`, `Puerto 4443 → kubelet K8s v1.30`.

### 7. Técnicas registradas y contrato JSON

- `cloud.docker.execute_command`: ejecutar comando en contenedor expuesto.
- `cloud.docker.breakout_host`: escalar desde contenedor al host.
- `cloud.docker.scan_image`: escanear imagen de contenedor con Trivy.
- `cloud.docker.steal_secrets`: extraer secretos de variables de entorno.
- `cloud.k8s.steal_secrets`: robar secretos de Kubernetes.
- `cloud.k8s.escalate_privileges`: escalar privilegios en el clúster.
- `cloud.k8s.deploy_pod`: desplegar pod malicioso para persistencia.
- `cloud.cloud.extract_imds`: extraer credenciales de metadatos cloud.
- `cloud.cloud.analyze_iam`: analizar políticas IAM con cloudsplaining.
- `cloud.cloud.persistence`: crear usuario backdoor en la nube.

Contrato JSON base (ejemplo breakout de contenedor):

```json
{
  "type": "cloud_action",
  "target_ip": "192.168.1.200",
  "target_port": 1500,
  "fingerprint": {
    "service": "docker_api",
    "version": "26.1",
    "auth_required": false
  },
  "technique_id": "cloud.docker.breakout_host",
  "params": {
    "mode": "verification",
    "command": "id"
  },
  "expected_evidence": ["host_shell", "command_output"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

### 8. Modos de operación (Verificación vs Persistencia)

- `Verificación` (por defecto): ejecuta la técnica mínima para comprobar el acceso, por ejemplo comando `id` en un contenedor. No modifica nada, no deja huella. Genera evidencia de `acceso conseguido`.
- `Persistencia`: despliega mecanismos de permanencia (pod malicioso, usuario backdoor, reverse shell). Requiere confirmación reforzada del usuario.
- El modo se selecciona en el panel antes de cada acción. Mistral sugiere siempre `Verificación` y advierte si se elige `Persistencia`.

## Ronda 15B — Flujo asistido, modos, preflight y recuperación

### 1. Objetivo

Definir el flujo de trabajo asistido, los modos de operación (`Verificación` vs `Persistencia`), el preflight checklist y la recuperación ante errores del Módulo 15. Solo documentación. No implementar código.

### 2. Ubicación

Esta ronda se añade después de la Ronda 15A en `docs/techniques/15_CLOUD.md` y complementa la base documental del módulo.

### 3. Flujo de trabajo asistido (Mistral + X5 + Hermes)

#### 3.1 Fingerprinting y sugerencia inicial

- El usuario introduce una IP o rango en la pestaña `Cloud`.
- El sistema ejecuta un escaneo de puertos con nmap y fingerprinting de servicios con WhatWeb y scripts NSE, según lo definido en la Ronda 15A. No asume que el puerto define el servicio.
- Para cada puerto abierto, el panel muestra el servicio real identificado: `Puerto 1500 → API Docker v26.1 (sin autenticación)`, `Puerto 4443 → kubelet K8s v1.30`, `Puerto 8080 → Consola de AWS`.
- Mistral analiza los resultados y sugiere en el chat contextual: `Se ha detectado una API Docker sin autenticación en el puerto 1500. ¿Deseas verificar el acceso?`.

#### 3.2 Selección de modo de operación (Verificación vs Persistencia)

- Antes de ejecutar cualquier técnica, el panel muestra un selector de modo:
  - `Verificación` (por defecto): solo comprueba el acceso, no modifica nada, no deja huella. Ejemplo: ejecutar `id` en un contenedor o leer un secreto sin extraerlo.
  - `Persistencia`: despliega mecanismos de permanencia (pod malicioso, usuario backdoor, reverse shell). Requiere confirmación reforzada.
- Mistral sugiere siempre `Verificación` y muestra una advertencia si el usuario selecciona `Persistencia`: `Esta acción modificará el entorno. ¿Está seguro?`.

#### 3.3 Ejecución de la técnica

- El usuario selecciona una técnica o escribe: `Accede a ese contenedor y dime si puedes ejecutar comandos`.
- Mistral rellena el contrato JSON con los parámetros (IP, puerto, modo y comando de verificación) y muestra el plan en una ventana modal.
- El usuario confirma. X5 valida contra Policy Engine, Kill Switch, scope, operador autorizado y VersionLock antes de ejecutar la técnica mediante un worker en Kali WSL2 (docker, kubectl, kubeletctl, CDK, etc.).
- El panel muestra el progreso en tiempo real. Si el modo es `Persistencia`, se solicita una segunda confirmación explícita.

#### 3.4 Intervención de Hermes (evolución del arsenal)

- Si el fingerprinting detecta un servicio desconocido, por ejemplo una nueva versión de Kubernetes con una API diferente, Mistral sugiere: `Servicio no catalogado. ¿Solicito a Hermes un módulo de análisis?`.
- El usuario acepta. Hermes investiga en fuentes abiertas (documentación, GitHub, foros), genera un módulo funcional en laboratorio (nuevo script de fingerprinting o nueva técnica de ataque) y lo prueba en sandbox.
- Si la prueba es exitosa, Hermes notifica: `Nuevo módulo para K8s v2.0 listo`. El usuario lo promociona al arsenal y X5 reanuda el ataque.
- Si Hermes no encuentra información, lo comunica y sugiere el hook `IMPLEMENTACION_USUARIO_REQUERIDA`.

### 4. Preflight checklist antes de ejecutar cualquier técnica

- [ ] IP objetivo dentro del scope del laboratorio.
- [ ] Fingerprinting del servicio completado y verificado.
- [ ] Modo de operación seleccionado (`Verificación` por defecto).
- [ ] Si es modo `Persistencia`: confirmación reforzada recibida.
- [ ] Kill Switch armado.
- [ ] Operador autorizado.
- [ ] VersionLock de herramientas verificado (docker, kubectl, CDK, etc.).

### 5. Errores y recuperación

#### 5.1 Servicio no reconocido tras fingerprinting

- El panel muestra `unknown_service`.
- No se ejecuta ninguna técnica.
- Mistral sugiere solicitar a Hermes un módulo de análisis.

#### 5.2 Acceso denegado (autenticación requerida)

- El panel muestra `auth_required`.
- Mistral sugiere probar credenciales por defecto si están autorizadas o pasar al Módulo 5 (Credenciales) para evaluación de credenciales dentro del laboratorio.

#### 5.3 Breakout fallido (contenedor a host)

- CDK o una herramienta equivalente no logra escalar.
- El panel muestra `breakout_failed`.
- Mistral sugiere verificar los privilegios del contenedor (capabilities, montajes) y solicitar a Hermes un módulo alternativo si es posible.

#### 5.4 Kill Switch activado

- Se detiene inmediatamente cualquier ejecución.
- Se guardan las evidencias pendientes.
- El estado cambia a `kill_switch_triggered`.

#### 5.5 Policy bloquea la acción

- El estado cambia a `blocked_by_policy`.
- Se muestra el motivo del bloqueo.
- La técnica no se ejecuta.

## Ronda 15C — Pantallas de trabajo por técnica y contratos JSON

### 1. Objetivo

Detallar las técnicas de ataque del Módulo 15 con sus pantallas de trabajo, parámetros y contratos JSON. Solo documentación. No implementar código.

### 2. Ubicación

Esta ronda se añade después de la Ronda 15B en `docs/techniques/15_CLOUD.md` y complementa lo ya documentado sobre fingerprinting, modos de operación, preflight y recuperación.

### 3. Pantallas de trabajo por técnica

#### 3.1 Ejecutar comando en contenedor (`cloud.docker.execute_command`)

- Requisito: API Docker detectada y fingerprinting completado.
- Campo `Comando a ejecutar`: autocompletado con `id` en modo `Verificación` o editable por el usuario.
- Campo `Modo`: desplegable `Verificación` / `Persistencia`.
- Botón `Ejecutar`: envía el comando vía docker remoto autorizado o API REST de laboratorio. Muestra la salida en un visor de texto.
- Contrato JSON:

```json
{
  "type": "cloud_action",
  "technique_id": "cloud.docker.execute_command",
  "params": {
    "target": "192.168.1.200:1500",
    "command": "id",
    "mode": "verification"
  },
  "expected_evidence": ["command_output"],
  "requires_confirmation": false
}
```

#### 3.2 Breakout de contenedor a host (`cloud.docker.breakout_host`)

- Requisito: acceso a un contenedor por `execute_command` u otro medio autorizado.
- Campo `Vector de breakout`: desplegable con opciones (`privileged`, `docker.sock`, `SYS_ADMIN`, `SYS_PTRACE`, `auto`). En modo `auto`, Mistral selecciona el más probable según los privilegios detectados.
- Campo `Modo`: `Verificación` (ejecuta `id` en el host) o `Persistencia` (despliega reverse shell). `Persistencia` requiere confirmación reforzada.
- Botón `Escalar`: ejecuta CDK o script personalizado dentro del laboratorio. Muestra el resultado (shell de host o fallo).
- Contrato JSON:

```json
{
  "type": "cloud_action",
  "technique_id": "cloud.docker.breakout_host",
  "params": {
    "target": "192.168.1.200:1500",
    "vector": "auto",
    "mode": "verification"
  },
  "expected_evidence": ["host_shell", "command_output"],
  "requires_confirmation": true
}
```

#### 3.3 Escanear imagen de contenedor (`cloud.docker.scan_image`)

- Requisito: acceso a la API Docker o a un registro de imágenes autorizado.
- Campo `Imagen`: nombre de la imagen, por ejemplo `nginx:latest`, o URL del registro.
- Botón `Escanear`: ejecuta Trivy contra la imagen. Muestra un informe de vulnerabilidades con CVEs, severidad y descripción.
- Contrato JSON:

```json
{
  "type": "cloud_action",
  "technique_id": "cloud.docker.scan_image",
  "params": {
    "image": "nginx:latest"
  },
  "expected_evidence": ["vulnerability_report"],
  "requires_confirmation": false
}
```

#### 3.4 Robar secretos de Docker (`cloud.docker.steal_secrets`)

- Requisito: acceso a un contenedor dentro del scope de laboratorio.
- Campo `Fuente`: desplegable (`env`, `files`, `auto`).
- Botón `Extraer`: ejecuta acciones autorizadas para volcar variables de entorno y archivos de configuración comunes (`.env`, `appsettings.json`). Muestra los secretos enmascarados por defecto.
- Botón `Enviar a Credenciales`: handoff a Módulo 5.
- Contrato JSON:

```json
{
  "type": "cloud_action",
  "technique_id": "cloud.docker.steal_secrets",
  "params": {
    "target": "192.168.1.200:1500",
    "source": "auto"
  },
  "expected_evidence": ["secrets_list"],
  "requires_confirmation": false
}
```

#### 3.5 Robar secretos de Kubernetes (`cloud.k8s.steal_secrets`)

- Requisito: acceso a la API de K8s o al kubelet dentro del scope autorizado.
- Campo `Namespace`: autocompletado con los namespaces disponibles.
- Botón `Listar secretos`: ejecuta kubectl o kubeletctl para enumerar secretos. Muestra una tabla con nombre, tipo y datos enmascarados.
- Botón `Decodificar y enviar a Credenciales`: decodifica los secretos base64 y los envía a M5 con redacción por defecto y AuditLog.
- Contrato JSON:

```json
{
  "type": "cloud_action",
  "technique_id": "cloud.k8s.steal_secrets",
  "params": {
    "target": "192.168.1.200:4443",
    "namespace": "default"
  },
  "expected_evidence": ["secrets_list"],
  "requires_confirmation": false
}
```

#### 3.6 Escalar privilegios en K8s (`cloud.k8s.escalate_privileges`)

- Requisito: acceso a un pod con una service account.
- Campo `Vector`: desplegable (`rbac_abuse`, `service_account_token`, `auto`).
- Botón `Escalar`: ejecuta Peirates dentro del entorno de laboratorio. Muestra los nuevos permisos obtenidos.
- Contrato JSON:

```json
{
  "type": "cloud_action",
  "technique_id": "cloud.k8s.escalate_privileges",
  "params": {
    "target": "192.168.1.200:4443",
    "vector": "auto"
  },
  "expected_evidence": ["privileges_report"],
  "requires_confirmation": true
}
```

#### 3.7 Extraer credenciales de metadatos cloud (`cloud.cloud.extract_imds`)

- Requisito: acceso a una instancia en AWS, Azure o GCP dentro del scope autorizado.
- Campo `Proveedor`: desplegable (`AWS`, `Azure`, `GCP`, `auto`).
- Botón `Extraer`: ejecuta peticiones autorizadas al endpoint de metadatos (`169.254.169.254`). Muestra las credenciales temporales enmascaradas por defecto.
- Botón `Enviar a Credenciales`: handoff a M5.
- Contrato JSON:

```json
{
  "type": "cloud_action",
  "technique_id": "cloud.cloud.extract_imds",
  "params": {
    "provider": "auto"
  },
  "expected_evidence": ["cloud_credentials"],
  "requires_confirmation": false
}
```

## Ronda 15D — Handoffs, scoring X5 y preparación M16

### 1. Objetivo

Definir los handoffs, el scoring X5 y la preparación para M16 del Módulo 15. Solo documentación. No implementar código.

### 2. Ubicación

Esta ronda se añade después de la Ronda 15C en `docs/techniques/15_CLOUD.md` y complementa lo ya documentado sobre pantallas de trabajo, parámetros y contratos JSON.

### 3. Handoff con otros módulos

El Módulo 15 no trabaja aislado. Sus hallazgos pueden enviarse a otros módulos mediante contratos auditados y con redacción por defecto.

#### 3.1 Handoff con Módulo 5 — Credenciales

- Las credenciales cloud extraídas (IMDS, secretos K8s, variables de entorno), tokens de servicio y claves API se empaquetan como `credential_handoff` y se envían a M5.
- Reglas:
  - `source_module = "cloud"`.
  - `source_evidence_id` es obligatorio.
  - Redacción por defecto con valores enmascarados.
  - M5 clasifica, deduplica y decide acciones posteriores.
  - Mostrar valores completos requiere confirmación explícita y registro en AuditLog.

#### 3.2 Handoff con Módulo 6 — Red / MITM

- Si se detecta tráfico de red entre contenedores o entre pods que requiere análisis profundo, se envía un PCAP a M6.
- Casos previstos: tráfico entre pods en diferentes namespaces, tráfico de un contenedor al exterior y flujos cloud que requieran inspección de red dentro del laboratorio.

#### 3.3 Handoff con Módulo 12 — Orquestación

- Todas las acciones `cloud.*` heredan el flujo M12:
  - LaIA/Mistral genera el plan y rellena parámetros.
  - X5 valida scope, Policy Engine, Kill Switch y VersionLock.
  - EvidenceStore guarda evidencias y artefactos.
  - AuditLog registra decisiones, confirmaciones y accesos.
  - El scoring X5 solo se calcula con evidencia válida.
  - Hermes Agent se activa si falta parser, aparece una nueva tecnología o se detecta una protección no catalogada.

### 4. Contrato JSON `cloud_handoff`

```json
{
  "type": "cloud_handoff",
  "source_module": "cloud",
  "target_ip": "192.168.1.200",
  "evidence_ids": ["ev-001", "ev-002"],
  "target_module": "M5",
  "handoff_reason": "cloud_credentials_extracted",
  "redaction_policy": "mask_all",
  "requires_confirmation": true,
  "operator": "admin",
  "created_at": "2026-06-03T10:00:00Z"
}
```

Campos obligatorios:

- `type`
- `source_module`
- `target_ip`
- `evidence_ids`
- `target_module`
- `handoff_reason`
- `redaction_policy`
- `requires_confirmation`
- `operator`
- `created_at`

### 5. Scoring X5 del Módulo 15

- Solo puntúa si hay evidencia válida: shell de host, secretos extraídos, credenciales cloud o informe de vulnerabilidades.
- `unknown_service` no penaliza la técnica.
- `blocked_by_policy` no penaliza la técnica.
- Un breakout exitoso sube el score de `cloud.docker.breakout_host`.
- Una extracción de credenciales IMDS sube el score de `cloud.cloud.extract_imds`.
- Técnicas en estado `IMPLEMENTACION_USUARIO_REQUERIDA` no puntúan hasta promoción.

### 6. Preparación para Módulo 16 (Evidencia / Ops / Calidad)

- Todas las evidencias del Módulo 15 deben cumplir:
  - SHA256 de cada archivo (`shell_output`, `secrets_list`, `vulnerability_report`).
  - Hashes encadenados en `timeline_json`.
  - Cadena de custodia interna (acceso, revelado, exportación y operador).
  - Exportación enmascarada por defecto.
  - Exportación completa solo con confirmación reforzada.
  - Metadatos: `target_ip`, `technique_id`, `scope`, `operator` y `VersionLock`.
- Tipos de evidencia:
  - `command_output.txt`: salida del comando ejecutado.
  - `secrets_list.json`: secretos extraídos, enmascarados por defecto.
  - `vulnerability_report.json`: informe de Trivy con CVEs.
  - `privileges_report.json`: permisos obtenidos tras escalada.
  - `cloud_credentials.json`: credenciales cloud extraídas, enmascaradas por defecto.

## Ronda 15E — Cierre documental, criterios de aceptación e índices

### 1. Objetivo

Cerrar la documentación del Módulo 15 con los criterios de aceptación, la actualización de índices y la nota final. Solo documentación. No implementar código.

### 2. Ubicación

Esta ronda se añade después de la Ronda 15D en `docs/techniques/15_CLOUD.md`. No borra, resume ni sustituye lo anterior.

### 3. Criterios de aceptación del Módulo 15

El Módulo 15 queda documentalmente cerrado si `docs/techniques/15_CLOUD.md` contiene:

- [ ] Propósito del módulo documentado.
- [ ] Herramientas nominales y VersionLock documentados (Trivy, kube-hunter, kubeletctl, CDK, Peirates, Scout Suite, Prowler, cloudsplaining, kubectl, docker, nmap, WhatWeb, Mistral, Hermes).
- [ ] Panel `Cloud` documentado con subpestañas (Contenedores, Kubernetes, Cloud).
- [ ] Fingerprinting real de servicios documentado (no puertos por defecto).
- [ ] Modos de operación (`Verificación` vs `Persistencia`) documentados.
- [ ] Técnicas `cloud.*` documentadas con sus `technique_id` y contrato JSON.
- [ ] Pantallas de trabajo por técnica documentadas (ejecución, breakout, escaneo, secretos, escalada, IMDS).
- [ ] Flujo de trabajo asistido (Mistral + X5 + Hermes) documentado.
- [ ] Preflight checklist y errores documentados.
- [ ] Handoffs con M5, M6 y M12 documentados, incluyendo el contrato `cloud_handoff`.
- [ ] Scoring X5 y preparación para M16 documentados.
- [ ] No se afirma implementación real.

### 4. Actualización de índices globales

Los índices globales del repositorio se actualizan, si existen, con la información indicada para el Módulo 15:

- `docs/MODULE_TOOL_INVENTORY.md`
- `docs/MODULE_ACCEPTANCE_CRITERIA.md`
- `AI_HANDOFF_OJO_DE_DIOS.md`

### 5. Nota final

El Módulo 15 queda definido como especificación de producto/laboratorio. Esta documentación no crea lógica funcional ni afirma ejecución real. Las partes sensibles permanecen marcadas como:

- `IMPLEMENTACION_USUARIO_REQUERIDA`
