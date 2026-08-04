# Módulo 13bis — Apple (iOS y macOS)

## Ronda 13bis-0 — Base documental del módulo Apple

### Alcance y regla de no implementación

Esta sección establece la base documental del **Módulo 13bis — Apple** como especificación de producto y laboratorio para auditoría de seguridad de dispositivos Apple, incluyendo iOS, iPadOS y macOS. Esta documentación no implementa código, no crea endpoints, no define workers ejecutables, no modifica bases de datos, no añade tests, no introduce requirements y no crea scripts funcionales. Toda capacidad sensible queda descrita como diseño documental y, cuando aplique, marcada como `IMPLEMENTACION_USUARIO_REQUERIDA` antes de cualquier promoción operativa futura.

### Filosofía del módulo

El Módulo 13bis cubre la auditoría de seguridad de dispositivos Apple dentro de un laboratorio controlado. No se limita a un simple escaneo: aplica una estrategia de capas para verificar la resistencia del sistema operativo frente a accesos no autorizados, abuso de emparejamiento, extracción de datos, ataques de red, perfiles de configuración, acceso remoto y técnicas asistidas sobre aplicaciones.

La IA **Mistral** asiste al operador en la selección de técnicas, prioriza rutas viables según el estado del dispositivo y genera planes documentales. **X5** valida el contexto de ejecución frente a `Policy Engine`, `Kill Switch`, scope de laboratorio, permisos y `VersionLock` antes de cualquier ejecución futura. **Hermes** evoluciona el arsenal si se encuentra una nueva versión de iOS/macOS, una protección no catalogada o un método que requiera investigación adicional, siempre bajo revisión y promoción controlada.

### Herramientas y versiones nominales — Kali WSL2

Las siguientes herramientas quedan registradas como referencias nominales de inventario y `VersionLock` para futuras rondas. No se instalan ni se ejecutan desde esta documentación.

- `libimobiledevice-utils 1.3.0`: referencia de instalación `sudo apt install libimobiledevice-utils`; uso documental para comunicación con dispositivos iOS/iPadOS emparejados.
- `ideviceinstaller 1.1.1`: referencia de instalación `sudo apt install ideviceinstaller`; uso documental para inventario e interacción con apps instaladas.
- `checkra1n 0.12.4`: referencia de instalación `sudo apt install checkra1n`; uso documental limitado a chips A5-A11 y condicionado por laboratorio, hardware compatible y autorización expresa.
- `Sliver 1.0`: referencia de obtención `git clone https://github.com/s0uthwest/sliver`; uso documental para bypass de código en escenarios autorizados.
- `ipwndfu 1.0`: referencia de obtención `git clone https://github.com/axi0mx/ipwndfu`; uso documental para investigación de modos DFU compatibles.
- `Evilginx3 3.3`: referencia de obtención `git clone https://github.com/kgretzky/evilginx2`; uso documental para campañas controladas de phishing Apple ID en laboratorio.
- `SET 8.0`: referencia de instalación `sudo apt install setoolkit`; uso documental para generación asistida de campañas en laboratorio.
- `Bettercap 2.34`: referencia de instalación `sudo apt install bettercap`; uso documental para escenarios MITM WiFi autorizados.
- `mitmproxy 10.2`: referencia de instalación `sudo apt install mitmproxy`; uso documental para inspección de tráfico bajo consentimiento y scope válido.
- `Hydra 9.7`: referencia de instalación `sudo apt install hydra`; uso documental para validación de resistencia de servicios autorizados.
- `Frida 16.5`: referencia de instalación `pip install frida-tools`; uso documental para instrumentación dinámica controlada.
- `objection 1.13`: referencia de instalación `pip install objection`; uso documental para automatización de tareas Frida en laboratorio.
- `Dolphin Mistral Nemo 12B`: generación asistida de scripts de Frida, perfiles maliciosos documentales y guía del flujo de ataque.
- `Hermes (DeepSeek API)`: creación de módulos para nuevas versiones de iOS/macOS o protecciones no catalogadas, bajo revisión humana y promoción explícita.

### Panel de control — Pestaña independiente "Apple"

El panel de Ojo de Dios incorpora una pestaña independiente **Apple**. La pestaña se divide en dos subpestañas principales, **iOS** y **macOS**, que comparten una estructura lógica común: detección, selección de objetivo, validación de preflight, confirmación explícita, ejecución futura mediada por X5, evidencias, historial y acceso a Hermes Agent Lab.

#### Subpestaña "iOS"

- **Visor de Dispositivo Conectado (USB)**: se activa al conectar un iPhone o iPad. Muestra modelo, versión de iOS/iPadOS, estado de jailbreak, estado de emparejamiento, identificador interno de dispositivo y elegibilidad documental de técnicas.
- **Sección "Recuperación de Acceso"**:
  - Botón "Extraer Backup (si emparejado)".
  - Botón "Fuerza Bruta Código (HID)".
  - Botón "Phishing Apple ID".
  - Botón "Buscar Exploit con Hermes".
- **Sección "Ataques de Red"**:
  - Botón "MITM WiFi".
  - Botón "Instalar Perfil Malicioso".
- **Visor de Evidencias y Hermes Agent Lab**: muestra evidencias generadas, estado de redacción, metadatos del dispositivo, historial/AuditLog y acceso a solicitudes de evolución del arsenal.

#### Subpestaña "macOS"

- **Visor de Dispositivos en Red**: escanea documentalmente objetivos autorizados y expone estado de servicios SSH, VNC y SMB dentro del scope de laboratorio.
- **Sección "Acceso Remoto"**:
  - Botón "Fuerza Bruta SSH".
  - Botón "Robar Token iCloud".
- **Sección "Gestión Avanzada"**:
  - Botón "Forzar Perfil MDM".
  - Botón "Keylogging (si hay acceso)".
- **Visor de Evidencias y Hermes Agent Lab**: centraliza resultados, artefactos, capturas del panel, solicitudes Hermes Agent y AuditLog.

### Estados visuales del panel "Apple"

El panel refleja uno de los siguientes estados globales:

- `idle`: esperando instrucciones del usuario.
- `scanning`: buscando dispositivos en la red o por USB.
- `device_connected`: dispositivo conectado por USB, mostrando su perfil.
- `extracting`: realizando una copia de seguridad.
- `jailbreaking`: ejecutando una ruta de jailbreak documentada y autorizada.
- `brute_forcing`: aplicando una técnica de fuerza bruta documentada bajo scope de laboratorio.
- `phishing_active`: campaña de phishing en curso dentro de un entorno controlado.
- `mitm_active`: ataque de hombre en el medio en ejecución dentro del laboratorio.
- `success`: técnica completada con éxito, evidencia generada.
- `error`: fallo en la ejecución o en la validación documental.
- `blocked_by_policy`: acción denegada por el `Policy Engine`.

### Técnicas registradas

Las técnicas siguientes quedan registradas como catálogo documental inicial. No afirman implementación real ni disponibilidad operativa.

| Técnica | Descripción documental | Evidencia esperada | Estado sensible |
| --- | --- | --- | --- |
| `ios.access.extract_backup` | Extraer copia de seguridad con `idevicebackup2` cuando el dispositivo esté emparejado y el scope lo permita. | `backup_complete`, `files_extracted`, metadatos de backup. | `IMPLEMENTACION_USUARIO_REQUERIDA` |
| `ios.access.bruteforce_code` | Validar resistencia del código mediante HID en laboratorio y con autorización explícita. | intentos, resultado, límites de política, AuditLog. | `IMPLEMENTACION_USUARIO_REQUERIDA` |
| `ios.access.phishing_apple_id` | Campaña controlada de phishing Apple ID para entrenamiento o validación defensiva. | captura de campaña, indicadores, resultados redactados. | `IMPLEMENTACION_USUARIO_REQUERIDA` |
| `ios.network.mitm_wifi` | Ataque MITM WiFi en red controlada con Bettercap/mitmproxy. | trazas de red, capturas del panel, PCAP si aplica. | `IMPLEMENTACION_USUARIO_REQUERIDA` |
| `ios.network.install_profile` | Instalación documentada de perfil `.mobileconfig` en laboratorio con confirmación explícita. | perfil, estado de instalación, AuditLog. | `IMPLEMENTACION_USUARIO_REQUERIDA` |
| `macos.access.bruteforce_ssh` | Validación de credenciales SSH autorizadas con controles de rate-limit y política. | intentos, resultado, bloqueo o éxito documentado. | `IMPLEMENTACION_USUARIO_REQUERIDA` |
| `macos.access.steal_token` | Extracción documental de tokens iCloud del llavero en escenarios autorizados y con acceso previo. | tokens enmascarados, cadena de custodia, AuditLog. | `IMPLEMENTACION_USUARIO_REQUERIDA` |

### Contrato JSON base para una acción de iOS

```json
{
  "type": "ios_action",
  "device_id": "dev-iphone-13",
  "technique_id": "ios.access.extract_backup",
  "params": {
    "backup_path": "/evidence/iphone_backup",
    "encryption": false
  },
  "expected_evidence": ["backup_complete", "files_extracted"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Campos obligatorios del contrato `ios_action`:

- `type`
- `device_id`
- `technique_id`
- `params`
- `expected_evidence`
- `scope`
- `operator`
- `requires_confirmation`

Reglas documentales del contrato:

- `scope` debe ser `laboratory` o un scope equivalente aprobado por el `Policy Engine`.
- `requires_confirmation` debe ser `true` para acciones de acceso, red, phishing, fuerza bruta, perfil de configuración o extracción sensible.
- `technique_id` debe pertenecer al catálogo `ios.*` o `macos.*` del Módulo 13bis.
- La evidencia debe enviarse a `EvidenceStore` con redacción por defecto, metadatos mínimos y AuditLog asociado.
- Cualquier dato sensible, credencial, token, backup, perfil o hallazgo exportable requiere confirmación reforzada antes de revelar contenido completo.

### Nota de cierre de la ronda

Con esta ronda, el Módulo 13bis queda inicializado como especificación documental de producto/laboratorio para Apple. No se ha implementado lógica funcional, no se afirma ejecución real y no se han creado endpoints, workers, bases de datos, tests, requirements ni scripts funcionales. Las partes sensibles permanecen marcadas como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta una promoción futura auditada.

## Ronda 13bis-1 — Flujo asistido, preflight y recuperación ante errores

### Alcance documental de la ronda

Esta ronda define el flujo de trabajo asistido, el checklist de preflight y la recuperación ante errores del Módulo 13bis. No implementa código, no crea endpoints, no crea workers reales, no modifica bases de datos, no añade tests, no introduce requirements y no crea scripts funcionales. Las referencias a ejecución, workers, herramientas o módulos se mantienen como especificación de producto/laboratorio para rondas futuras auditadas.

### Flujo de trabajo asistido — Mistral + X5 + Hermes

#### Detección y sugerencia inicial

- El usuario accede a la pestaña **Apple > iOS** o **Apple > macOS**.
- Al conectar un dispositivo por USB o al detectar uno en la red, el panel muestra automáticamente su perfil: modelo, versión, estado de emparejamiento, estado de jailbreak cuando aplique, servicios expuestos y compatibilidad documental con las técnicas registradas.
- Mistral analiza el perfil y sugiere en el chat contextual una ruta viable. Ejemplo documental: "iPhone 13 bloqueado detectado. No tiene jailbreak, pero está emparejado con este PC. ¿Extraer copia de seguridad?".
- La sugerencia de Mistral no ejecuta acciones por sí sola: solo propone una técnica, explica supuestos, enumera evidencias esperadas y avisa si se requiere confirmación explícita adicional.

#### Ejecución de una técnica

- El usuario selecciona una técnica desde el panel o escribe una petición en lenguaje natural, por ejemplo: "Sácale todo lo que puedas a este iPhone bloqueado".
- Mistral traduce la petición a una intención auditada, selecciona las técnicas adecuadas, rellena el contrato JSON con parámetros documentales como ruta de backup, método de fuerza bruta, interfaz de red, paquete objetivo o timeout, y muestra el plan en una ventana modal.
- El usuario confirma el plan. X5 valida contra `Policy Engine`, `Kill Switch`, scope de laboratorio, permisos disponibles y `VersionLock` de herramientas antes de permitir cualquier ejecución futura.
- La técnica queda asociada a una capa de ejecución futura en Kali WSL2, representada documentalmente como worker controlado por X5 para herramientas como `idevicebackup2`, `checkra1n`, `Frida`, `Bettercap`, `mitmproxy` o `Hydra`. Esta documentación no crea dicho worker ni afirma que exista.
- El panel muestra progreso en tiempo real como requisito de producto. Si la técnica implica emisión de red, phishing, jailbreak, fuerza bruta, instalación de perfil o acceso sensible, se solicita confirmación explícita adicional y aviso de responsabilidad.
- EvidenceStore y AuditLog deben recibir los metadatos del intento, el resultado, el operador, el scope y los identificadores de evidencia cuando existan artefactos válidos.

#### Intervención de Hermes — Evolución del arsenal

- Si una técnica falla porque la versión de iOS es demasiado reciente, el dispositivo no es vulnerable a checkm8, la versión de macOS incorpora una protección nueva, el Apple ID usa defensa no catalogada o falta un parser, Mistral sugiere: "No hay técnica disponible para este caso. ¿Solicito a Hermes un módulo personalizado?".
- Si el usuario acepta, Mistral envía a Hermes una solicitud con el perfil del dispositivo: modelo, versión de iOS/macOS, estado de emparejamiento, estado de jailbreak, servicios detectados, errores observados y evidencias parciales disponibles.
- Hermes puede buscar en fuentes abiertas, GitHub, foros especializados o documentación técnica una PoC, exploit o técnica documentada. Si encuentra una ruta viable, propone un módulo de laboratorio, por ejemplo script Frida, perfil de configuración, parser, técnica de extracción o wrapper controlado.
- Cualquier módulo propuesto por Hermes debe probarse en sandbox, revisarse por el usuario y promocionarse explícitamente al arsenal antes de que X5 pueda reanudar el flujo original con la nueva técnica.
- Si Hermes no encuentra información suficiente, lo comunica y sugiere aportar manualmente un 0-day, PoC o investigación propia mediante el hook `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Preflight checklist — Antes de ejecutar cualquier técnica

Antes de ejecutar cualquier técnica del Módulo 13bis, el panel debe verificar documentalmente:

- [ ] Dispositivo conectado por USB o detectado en red.
- [ ] Perfil del dispositivo verificado: modelo, versión, estado de emparejamiento, estado de jailbreak si aplica y servicios expuestos.
- [ ] Técnica seleccionada compatible con el perfil del dispositivo.
- [ ] Permisos necesarios disponibles según la técnica: emparejamiento USB, acceso a backup, jailbreak, acceso SSH, privilegios locales, accesibilidad de red o autorización equivalente.
- [ ] `Kill Switch` armado.
- [ ] Operador autenticado y autorizado.
- [ ] Scope de laboratorio válido y aprobado por `Policy Engine`.
- [ ] Confirmación explícita del usuario y aviso de responsabilidad para técnicas de jailbreak, phishing, fuerza bruta, instalación de perfil, MITM o extracción sensible.
- [ ] `VersionLock` de herramientas verificado: `libimobiledevice`, `ideviceinstaller`, `checkra1n`, `Frida`, `objection`, `Bettercap`, `mitmproxy`, `Hydra` u otras herramientas nominales aplicables.
- [ ] Redacción por defecto activa para backups, tokens, credenciales, perfiles, PCAP, capturas y cualquier dato sensible.

Si cualquier ítem obligatorio falla, el panel debe bloquear el botón de ejecución, mostrar el motivo, mantener el estado correspondiente y registrar el intento en AuditLog si el usuario intentó ejecutar la acción.

### Errores y recuperación

#### Dispositivo no emparejado — iOS

- El panel muestra `device_not_paired`.
- No se puede extraer backup mediante rutas que requieran confianza USB previa.
- Mistral sugiere: "El dispositivo no confía en este PC. Prueba fuerza bruta al código o phishing del Apple ID".
- Si existe sesión o evidencia parcial, se conserva con estado de bloqueo y redacción por defecto.

#### Jailbreak fallido — checkra1n

- El panel muestra `jailbreak_failed`.
- Se detiene el proceso documental asociado a la ruta de jailbreak.
- Mistral sugiere verificar cable USB, modo DFU, compatibilidad del chip, versión de iOS y restricciones del laboratorio.
- Hermes puede recibir el perfil del fallo si se requiere investigar una variante o protección no catalogada.

#### Fuerza bruta bloqueada

- Tras varios intentos o ante un retraso impuesto por iOS/macOS, el panel muestra `bruteforce_blocked`.
- La técnica se pausa y no debe insistir sin nueva validación de Policy y confirmación del usuario.
- Mistral sugiere esperar, revisar límites de rate-limit o probar otro vector documental como phishing controlado, extracción emparejada o análisis de red.

#### Dispositivo se desconecta durante el ataque

- El panel marca el dispositivo como `disconnected`.
- Se guardan las evidencias parciales con metadatos de interrupción, timestamp, operador y estado final.
- Si el ataque era automatizado, se pausa y se notifica al usuario.
- No se reanuda automáticamente sin nuevo preflight.

#### Kill Switch activado

- El estado global cambia a `kill_switch_triggered`.
- Se detiene inmediatamente cualquier extracción, jailbreak, emisión de red, phishing, fuerza bruta, instalación de perfil, hook o captura.
- Se guardan las evidencias pendientes con prioridad de integridad y se registra AuditLog prioritario.
- El panel no permite reanudar hasta que el operador autorizado restablezca el estado conforme a Policy.

#### Policy bloquea la acción

- El estado cambia a `blocked_by_policy`.
- Se muestra el motivo del bloqueo: scope inválido, operador no autorizado, técnica prohibida, VersionLock no verificado, Kill Switch no armado o falta de confirmación explícita.
- La técnica no se ejecuta.
- AuditLog registra el intento si el usuario había solicitado la acción.

### Nota de cierre de la ronda

Con esta ronda, el Módulo 13bis dispone de flujo asistido, preflight y recuperación ante errores como especificación documental. No se ha implementado lógica funcional ni se afirma ejecución real. Cualquier ruta sensible permanece bajo `IMPLEMENTACION_USUARIO_REQUERIDA` y requiere validación futura, confirmación explícita, Policy, Kill Switch, EvidenceStore y AuditLog.

## Ronda 13bis-2 — Handoffs, scoring X5 y preparación M16

### Alcance documental de la ronda

Esta ronda define los handoffs, el scoring X5 y la preparación para M16 del Módulo 13bis. Solo documenta contratos, reglas y criterios de evidencia. No implementa código, no crea endpoints, no crea workers, no modifica bases de datos, no añade tests, no introduce requirements y no crea scripts funcionales. Toda referencia a credenciales, tokens, perfiles, backups, phishing, jailbreak o extracción se mantiene como especificación de laboratorio con redacción por defecto y `IMPLEMENTACION_USUARIO_REQUERIDA` cuando aplique.

### Handoff con otros módulos

El Módulo 13bis puede enviar hallazgos a otros módulos mediante contratos auditados, con redacción por defecto y confirmación explícita cuando el contenido sea sensible.

#### Handoff con Módulo 5 — Credenciales

- Las contraseñas de Apple ID, tokens de sesión, cookies de iCloud y claves extraídas del llavero se empaquetan como `credential_handoff` y se envían a M5.
- Reglas:
  - `source_module = "apple"`.
  - `source_vector = "ios"` o `source_vector = "macos"`.
  - `source_evidence_id` obligatorio.
  - Redacción por defecto con valores enmascarados.
  - M5 clasifica, deduplica y decide acciones.
  - Mostrar contenido completo requiere confirmación reforzada y AuditLog.

#### Handoff con Módulo 12 — Orquestación

- Todas las acciones `ios.*` y `macos.*` heredan el flujo M12:
  - LaIA/Mistral genera el plan y rellena parámetros.
  - X5 valida permisos, scope, Policy, Kill Switch, VersionLock y confirmaciones.
  - EvidenceStore guarda artefactos, metadatos, estado de redacción e integridad.
  - AuditLog registra intento, operador, resultado, bloqueo, revelado y exportación.
  - Scoring X5 solo se calcula con evidencia válida.
  - Hermes Agent se activa si falta parser, bypass de protección, técnica compatible o soporte para una nueva versión de iOS/macOS.

#### Handoff con Módulo 13 — Android

- Si se encuentra un archivo APK en un backup de iOS, por ejemplo una app de Android almacenada como artefacto o adjunto, se transfiere al Módulo 13 para su análisis documental.
- Si durante un escaneo de red se detecta un dispositivo Android en el mismo laboratorio, se notifica al Módulo 13 con el identificador de dispositivo, evidencia de descubrimiento y motivo del handoff.
- El Módulo 13 recibe únicamente evidencias enmascaradas por defecto y debe aplicar sus propios contratos, Policy, Kill Switch, EvidenceStore y AuditLog antes de continuar.

### Contrato JSON `apple_handoff`

Cuando se envían hallazgos a otros módulos, se utiliza el contrato documental `apple_handoff`:

```json
{
  "type": "apple_handoff",
  "source_module": "apple",
  "source_vector": "ios",
  "session_id": "sess-7890",
  "device_id": "dev-iphone-13",
  "evidence_ids": ["ev-001", "ev-002"],
  "target_module": "M5",
  "handoff_reason": "apple_id_credentials_extracted",
  "redaction_policy": "mask_all",
  "requires_confirmation": true,
  "operator": "admin",
  "created_at": "2026-06-03T10:00:00Z"
}
```

Campos obligatorios:

- `type`
- `source_module`
- `source_vector`
- `session_id`
- `device_id`
- `evidence_ids`
- `target_module`
- `handoff_reason`
- `redaction_policy`
- `requires_confirmation`
- `operator`
- `created_at`

Reglas documentales del contrato:

- `type` debe ser `apple_handoff`.
- `source_module` debe ser `apple`.
- `source_vector` debe identificar `ios` o `macos`.
- `evidence_ids` no debe estar vacío cuando exista evidencia material.
- `redaction_policy` debe ser `mask_all` por defecto para credenciales, tokens, llaveros, backups, perfiles y capturas.
- `requires_confirmation` debe ser `true` para cualquier handoff que pueda revelar credenciales, tokens, datos personales, backups o material sensible.

### Scoring X5 del Módulo 13bis

- Solo puntúa si hay evidencia válida, verificable y asociada a una técnica registrada, por ejemplo backup extraído, código descifrado, token de sesión, credenciales de Apple ID, jailbreak exitoso o evidencia de red válida.
- `device_not_paired` no penaliza la técnica porque representa una precondición no satisfecha.
- `blocked_by_policy` no penaliza la técnica porque no se ejecutó por decisión de gobernanza.
- Un jailbreak exitoso sube el score de `ios.access.jailbreak_checkra1n` solo si la técnica fue promovida y existe evidencia válida.
- Una extracción de backup exitosa sube el score de `ios.access.extract_backup`.
- Un phishing exitoso sube el score de `ios.access.phishing_apple_id` únicamente con evidencia autorizada, redactada por defecto y trazabilidad completa.
- Técnicas en estado `IMPLEMENTACION_USUARIO_REQUERIDA` no puntúan hasta promoción auditada.
- Evidencia ausente, corrupta, no atribuible a `session_id` o sin cadena de custodia no aumenta score.
- Falsos positivos o evidencia no reproducible reducen la confianza de la técnica y deben quedar registrados en AuditLog.

Campos recomendados para scoring:

- `technique_id`
- `session_id`
- `device_id`
- `device_type`
- `evidence_valid`
- `blocked_by_policy`
- `false_positive`
- `score_before`
- `score_after`
- `score_delta`
- `operator`

### Preparación para Módulo 16 — Evidencia / Ops / Calidad

Todas las evidencias del Módulo 13bis deben quedar preparadas para M16 con integridad verificable, trazabilidad interna y redacción por defecto.

Requisitos documentales:

- SHA256 de cada archivo de evidencia, incluyendo backups, tokens, perfiles, reportes, PCAP, capturas y logs.
- Hashes encadenados en `timeline_json` para reconstruir el orden de eventos.
- Cadena de custodia interna con acceso, revelado, exportación, modificación, operador y timestamp.
- Exportación enmascarada por defecto.
- Exportación completa solo con confirmación reforzada, motivo documentado y AuditLog.
- Metadatos mínimos: `session_id`, `device_id`, `technique_id`, `scope`, `operator`, `VersionLock`, `source_vector`, estado de redacción y timestamps.
- Integridad verificable antes de handoff, exportación o compilación de informe.
- Compatibilidad con el compilador final de M16 y con los informes de calidad/ops.

Tipos de evidencia relevantes:

- `ios_backup`: copia de seguridad extraída.
- `jailbreak_log`: registro documental del proceso de jailbreak.
- `phishing_campaign_report`: resultado de la campaña de phishing controlada.
- `token_session.txt`: token de sesión extraído, siempre enmascarado por defecto.
- `profile.mobileconfig`: perfil instalado o preparado en laboratorio.
- `mitm_pcap`: captura de tráfico de red.
- `icloud_cookie_dump`: cookies de iCloud enmascaradas por defecto.
- `keychain_extract_report`: reporte de llavero con valores redactados.
- `panel_capture`: captura del panel Apple.
- `audit_log`: registro de acciones, bloqueos, revelados y exportaciones.

### Nota de cierre de la ronda

Con esta ronda, el Módulo 13bis documenta handoffs auditados, scoring X5 y preparación de evidencia para M16. No se ha implementado lógica funcional ni se afirma ejecución real de extracción, phishing, jailbreak, MITM, fuerza bruta o manipulación. Cualquier acción sensible permanece bajo `IMPLEMENTACION_USUARIO_REQUERIDA`, redacción por defecto, confirmación explícita, Policy, Kill Switch, EvidenceStore y AuditLog.

## Ronda 13bis-3 — iOS > Acceso Físico (USB)

### Alcance documental de la ronda

Esta ronda define las técnicas de ataque físico vía USB para dispositivos iOS/iPadOS como especificación de producto y laboratorio. No implementa código, no crea endpoints, no crea workers, no modifica bases de datos, no añade tests, no introduce requirements y no crea scripts funcionales. Las acciones sensibles quedan documentadas como `IMPLEMENTACION_USUARIO_REQUERIDA` y requieren laboratorio autorizado, confirmación explícita, Policy, Kill Switch, EvidenceStore y AuditLog antes de cualquier promoción futura.

### Subpestaña "iOS > Acceso Físico (USB)"

Cuando se conecta un iPhone o iPad por USB, esta sección del panel se activa y muestra únicamente las opciones compatibles con el estado detectado del dispositivo. El panel no ejecuta acciones por sí solo: presenta disponibilidad, preflight, contratos JSON documentales, riesgos y evidencias esperadas.

#### Visor de Dispositivo Conectado

El visor debe mostrar:

- Modelo del dispositivo.
- Versión de iOS/iPadOS.
- Estado de jailbreak: `sí` o `no`.
- Estado de emparejamiento: `pareado` o `no_pareado`.
- Tipo de chip: `A5-A11` o `A12+`.
- `device_id`, `session_id`, operador, scope y estado de `VersionLock`.

Reglas de habilitación documental:

- Si el chip es `A5-A11`, se habilita el botón **"Jailbreak (checkra1n)"**.
- Si el dispositivo está `pareado`, se habilita el botón **"Extraer Backup"**.
- En cualquier caso, el panel muestra los botones **"Fuerza Bruta Código (HID)"** y **"Buscar Exploit con Hermes"**, pero ambos permanecen sujetos a Policy, Kill Switch, confirmación explícita y `IMPLEMENTACION_USUARIO_REQUERIDA`.
- Si falta una precondición, el botón correspondiente aparece deshabilitado con motivo visible y AuditLog si hubo intento de ejecución.

### Técnicas de ataque físico

#### Jailbreak con checkra1n

- Técnica: `ios.access.jailbreak_checkra1n`.
- Requisito documental: chip `A5-A11`; el usuario debe poner el dispositivo en modo DFU dentro del laboratorio autorizado.
- Parámetros: ninguno adicional; la especificación asume configuración estándar de checkra1n sin documentar pasos operativos.
- Confirmación: requerida antes de iniciar la técnica y antes de registrar cualquier acceso sensible.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON documental:

```json
{
  "type": "ios_action",
  "device_id": "dev-iphone-x",
  "technique_id": "ios.access.jailbreak_checkra1n",
  "params": {},
  "expected_evidence": ["jailbreak_success", "ssh_access"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Evidencia esperada:

- Captura de pantalla o registro del terminal mostrando resultado exitoso.
- Acceso SSH verificado como evidencia documental, enmascarado por defecto cuando contenga identificadores o credenciales.
- `jailbreak_log`, `panel_capture`, `audit_log` y metadatos `session_id`, `device_id`, `VersionLock`.

#### Extraer Backup — idevicebackup2

- Técnica: `ios.access.extract_backup`.
- Requisito documental: dispositivo pareado con el PC y confianza establecida.
- Parámetros: ruta de destino del backup y estado de cifrado.
- Confirmación: requerida antes de iniciar extracción y antes de revelar contenido completo.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON documental:

```json
{
  "type": "ios_action",
  "device_id": "dev-iphone-13",
  "technique_id": "ios.access.extract_backup",
  "params": {
    "backup_path": "/evidence/iphone_backup",
    "encryption": false
  },
  "expected_evidence": ["backup_complete", "files_extracted"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Evidencia esperada:

- Archivos del backup, incluyendo contactos, fotos, mensajes y datos de apps cuando estén disponibles dentro del scope autorizado.
- `ios_backup`, índice de archivos, hashes SHA256, `timeline_json`, `panel_capture` y `audit_log`.
- Exportación enmascarada por defecto; exportación completa solo con confirmación reforzada.

#### Fuerza Bruta al Código — HID

- Técnica: `ios.access.bruteforce_code`.
- Requisito documental: laboratorio autorizado, dispositivo conectado por USB y aceptación de los límites de seguridad del dispositivo.
- Descripción: validación de resistencia mediante pulsaciones por USB emulando un teclado, sin incluir implementación ni secuencia operativa.
- Parámetros: longitud del código, 4 o 6 dígitos, y diccionario opcional.
- Confirmación: requerida antes de iniciar y antes de continuar si iOS impone retrasos.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON documental:

```json
{
  "type": "ios_action",
  "device_id": "dev-iphone-13",
  "technique_id": "ios.access.bruteforce_code",
  "params": {
    "code_length": 6,
    "dictionary": "default"
  },
  "expected_evidence": ["code_found", "access_granted"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Evidencia esperada:

- Código descifrado solo si el scope y la confirmación reforzada permiten revelarlo.
- Captura del springboard desbloqueado con redacción cuando contenga datos personales.
- Registro de intentos, bloqueos, retrasos, `audit_log`, `panel_capture` y metadatos de sesión.

#### Buscar Exploit con Hermes

- Técnica: `ios.access.hermes_exploit_search`.
- Activación: si jailbreak, backup o fuerza bruta fallan, el usuario puede solicitar a Hermes la búsqueda de un exploit de kernel o técnica documentada para esa versión de iOS.
- Hermes investiga en fuentes abiertas y documentación técnica. Si encuentra una PoC, puede proponer convertirla en módulo de laboratorio y probarla en sandbox.
- El exploit no se aplica automáticamente: requiere revisión humana, promoción explícita al arsenal, Policy, Kill Switch, VersionLock y confirmación reforzada.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON documental para solicitud a Hermes:

```json
{
  "type": "hermes_request",
  "action": "search_exploit",
  "params": {
    "device_model": "iPhone13,2",
    "ios_version": "17.4"
  }
}
```

Resultado esperado:

- Si Hermes encuentra una ruta viable, genera una propuesta documental de módulo de laboratorio, evidencia de sandbox y requisitos de promoción.
- Si Hermes no encuentra información suficiente, notifica el bloqueo y sugiere aportar investigación manual mediante `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Errores y recuperación

- `checkra1n_failed`: verificar cable, modo DFU, compatibilidad del chip, versión de iOS y estado de `VersionLock`; se detiene la ruta de jailbreak y se preservan logs parciales.
- `backup_failed`: verificar emparejamiento y confianza del dispositivo; el panel puede recomendar validación de emparejamiento, sin ejecutar comandos desde la documentación.
- `bruteforce_blocked`: iOS impone retrasos o límites; el sistema pausa la técnica, espera decisión del operador y registra el evento.
- `device_disconnected`: se guardan evidencias parciales, se marca el dispositivo como desconectado y no se reanuda sin nuevo preflight.
- `blocked_by_policy`: la técnica no se ejecuta; se muestra el motivo y AuditLog registra el intento si hubo solicitud del usuario.
- `kill_switch_triggered`: se detiene cualquier extracción, jailbreak, HID, búsqueda activa o captura; se preservan evidencias pendientes y se bloquea la reanudación hasta autorización.

### Nota de cierre de la ronda

Con esta ronda, la subpestaña **iOS > Acceso Físico (USB)** queda definida como especificación documental. No se implementan técnicas de jailbreak, extracción, fuerza bruta, búsqueda de exploits ni lógica de ejecución. Todas las rutas sensibles permanecen bajo `IMPLEMENTACION_USUARIO_REQUERIDA`, confirmación explícita, Policy, Kill Switch, EvidenceStore y AuditLog.

## Ronda 13bis-4 — iOS > Ataques de Red y Phishing

### Alcance documental de la ronda

Esta ronda define técnicas remotas para iOS como especificación de producto y laboratorio: MITM en red WiFi, phishing de Apple ID e instalación de perfiles `.mobileconfig`. No implementa código, no crea endpoints, no crea workers, no modifica bases de datos, no añade tests, no introduce requirements y no crea scripts funcionales. Las técnicas descritas requieren scope de laboratorio, autorización explícita, redacción por defecto, Policy, Kill Switch, EvidenceStore, AuditLog y permanecen bajo `IMPLEMENTACION_USUARIO_REQUERIDA` antes de cualquier promoción futura.

### Subpestaña "iOS > Ataques de Red y Phishing"

Esta sección se activa cuando se detecta un dispositivo Apple en la red WiFi local por MAC OUI, mDNS u otros metadatos de inventario, o cuando el usuario introduce manualmente un objetivo autorizado. No requiere acceso físico ni emparejamiento previo, pero sí exige scope de laboratorio válido, operador autorizado y confirmación explícita para cualquier técnica que implique interceptación, captura de credenciales, perfil de configuración o redirección de tráfico.

#### Visor de Dispositivos en Red

El visor muestra una tabla unificada con los dispositivos Apple detectados:

- IP del dispositivo.
- MAC y OUI estimado.
- Nombre anunciado por mDNS cuando esté disponible.
- Modelo estimado.
- Estado de alcance de red.
- `device_id`, `session_id`, operador, scope y estado de `VersionLock`.

Botones contextuales:

- **"MITM WiFi"**.
- **"Phishing Apple ID"**.
- **"Instalar Perfil"**.

Reglas de habilitación documental:

- Los botones solo se habilitan si el objetivo está dentro del scope autorizado y el `Policy Engine` permite la acción.
- Las acciones que puedan capturar credenciales, tokens, cookies, tráfico o instalar perfiles requieren confirmación explícita reforzada.
- El panel debe mostrar que la ejecución real no está implementada en esta ronda y que la técnica permanece como `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Técnicas de ataque remoto

#### MITM WiFi — Bettercap + mitmproxy

- Técnica: `ios.network.mitm_wifi`.
- Requisito documental: el dispositivo objetivo debe estar en la misma red WiFi que Ojo de Dios o en una red alcanzable dentro del laboratorio.
- Parámetros: IP del objetivo, puerta de enlace, interfaz de red y duración; Mistral puede rellenarlos automáticamente desde el perfil de red.
- Confirmación: requerida antes de iniciar cualquier interceptación o captura.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON documental:

```json
{
  "type": "ios_action",
  "device_id": "dev-iphone-wifi",
  "technique_id": "ios.network.mitm_wifi",
  "params": {
    "target_ip": "192.168.1.50",
    "gateway": "192.168.1.1",
    "interface": "wlan0",
    "duration_seconds": 120
  },
  "expected_evidence": ["pcap", "credentials"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Evidencia esperada:

- Tráfico PCAP dentro del scope autorizado.
- Credenciales capturadas, cookies, tokens o HTTP Basic Auth solo como hallazgos enmascarados por defecto.
- `mitm_pcap`, `panel_capture`, `audit_log`, hashes SHA256, `timeline_json` y metadatos `session_id`, `device_id`, `VersionLock`.

#### Phishing de Apple ID — Evilginx3 / SET

- Técnica: `ios.access.phishing_apple_id`.
- Requisito documental: el operador debe disponer de un dominio o IP accesible para alojar el portal controlado de laboratorio; si no existe, Mistral puede sugerir conceptualmente un servicio de tunneling local, sin configurarlo ni ejecutarlo desde esta documentación.
- Parámetros: plantilla de phishing, URL del dominio falso, duración y contexto de campaña.
- Confirmación: requerida antes de generar, activar o registrar cualquier campaña; el revelado completo de credenciales requiere confirmación reforzada y AuditLog.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON documental:

```json
{
  "type": "ios_action",
  "device_id": "dev-iphone-phishing",
  "technique_id": "ios.access.phishing_apple_id",
  "params": {
    "template": "icloud",
    "phishing_url": "https://icloud-seguro.com",
    "duration_hours": 24
  },
  "expected_evidence": ["credentials_captured", "mfa_token"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Evidencia esperada:

- Credenciales de Apple ID, usuario, contraseña y token 2FA solo enmascarados por defecto.
- `phishing_campaign_report`, capturas del panel, eventos de interacción, `audit_log`, hashes SHA256 y `timeline_json`.
- Handoff a M5 como `credential_handoff` si aparecen credenciales o tokens, siempre con redacción por defecto.

#### Instalar Perfil Malicioso — `.mobileconfig`

- Técnica: `ios.network.install_profile`.
- Requisito documental: el usuario objetivo debe aceptar la instalación del perfil dentro de un ejercicio autorizado; puede combinarse con una campaña de laboratorio, pero no se ejecuta desde esta documentación.
- Parámetros: tipo de perfil, URL de descarga, host proxy, puerto proxy y metadatos de campaña.
- Confirmación: requerida antes de preparar, distribuir o registrar la instalación del perfil.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON documental:

```json
{
  "type": "ios_action",
  "device_id": "dev-iphone-profile",
  "technique_id": "ios.network.install_profile",
  "params": {
    "profile_type": "proxy",
    "profile_url": "https://evil-server.com/profile.mobileconfig",
    "proxy_host": "192.168.1.100",
    "proxy_port": 8080
  },
  "expected_evidence": ["profile_installed", "traffic_redirected"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Evidencia esperada:

- Confirmación de instalación del perfil dentro del laboratorio.
- Evidencia de tráfico redirigido a través del proxy autorizado.
- `profile.mobileconfig`, `mitm_pcap` si aplica, `panel_capture`, `audit_log`, hashes SHA256 y `timeline_json`.

### Errores y recuperación

- `mitm_failed`: verificar que el objetivo está en la misma red o en una red alcanzable; si existe protección ARP o segmentación, el panel muestra el bloqueo y conserva evidencias parciales.
- `phishing_no_credentials`: Mistral sugiere revisar plantilla, dominio, contexto de campaña o canal de entrega dentro del laboratorio, sin reenviar automáticamente mensajes ni ejecutar campañas.
- `profile_rejected`: el usuario objetivo rechazó la instalación; el panel registra el rechazo, no insiste automáticamente y sugiere revisar el pretexto o combinar con una campaña autorizada.
- `anti_phishing_updated`: Hermes puede intervenir si Apple actualiza mecanismos anti-phishing o anti-perfil, proponiendo nuevas plantillas o bypasses solo como módulos de laboratorio sujetos a sandbox y promoción explícita.
- `blocked_by_policy`: la técnica no se ejecuta; se muestra el motivo y AuditLog registra el intento si hubo solicitud del usuario.
- `kill_switch_triggered`: se detiene cualquier campaña, captura, perfil, redirección o solicitud Hermes activa y se preservan evidencias pendientes.

### Nota de cierre de la ronda

Con esta ronda, la subpestaña **iOS > Ataques de Red y Phishing** queda definida como especificación documental. No se implementan MITM, phishing, instalación de perfiles, campañas, proxies, capturas ni lógica de ejecución. Todas las rutas sensibles permanecen bajo `IMPLEMENTACION_USUARIO_REQUERIDA`, confirmación explícita, redacción por defecto, Policy, Kill Switch, EvidenceStore y AuditLog.

## Ronda 13bis-5 — macOS, criterios de aceptación, índices y cierre documental

### Alcance documental de la ronda

Esta ronda define las técnicas de ataque a macOS, los criterios de aceptación del Módulo 13bis, la actualización de índices globales y la nota final de cierre. Solo documenta especificaciones de producto/laboratorio: no implementa código, no crea endpoints, no crea workers, no modifica bases de datos, no añade tests, no introduce requirements y no crea scripts funcionales. Toda técnica sensible permanece bajo `IMPLEMENTACION_USUARIO_REQUERIDA`, confirmación explícita, Policy, Kill Switch, EvidenceStore y AuditLog.

### Subpestaña "macOS"

La subpestaña **macOS** se activa cuando se detectan ordenadores Mac en la red local por servicios expuestos autorizados, como SSH/22, VNC/5900 o SMB/445, o cuando el usuario introduce manualmente una IP dentro del scope de laboratorio. El panel muestra únicamente opciones documentales compatibles con el perfil detectado y no afirma ejecución real.

#### Visor de Dispositivos macOS en Red

El visor muestra una tabla con los Mac detectados:

- IP del objetivo.
- MAC y OUI estimado.
- Nombre de host anunciado por mDNS cuando esté disponible.
- Puertos abiertos: SSH/22, VNC/5900, SMB/445 u otros servicios autorizados.
- Estado de alcance de red.
- `device_id`, `session_id`, operador, scope y `VersionLock`.

Botones contextuales:

- **"Fuerza Bruta SSH"**.
- **"Robar Token iCloud"**.
- **"Forzar Perfil MDM"**.
- **"Keylogging (si hay acceso)"**.

Reglas de habilitación documental:

- Los botones solo se habilitan si el objetivo está dentro del scope autorizado y el `Policy Engine` permite la acción.
- Las técnicas que impliquen credenciales, tokens, perfiles, acceso remoto, keylogging o control persistente requieren confirmación explícita reforzada.
- El panel debe mostrar que la ejecución real no está implementada en esta ronda y que las técnicas permanecen como `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Técnicas de ataque a macOS

#### Fuerza Bruta SSH — Hydra

- Técnica: `macos.access.bruteforce_ssh`.
- Requisito documental: puerto 22 abierto en el Mac objetivo y autorización expresa dentro del laboratorio.
- Parámetros: IP, puerto y diccionario: `rockyou.txt`, generado por IA o personalizado.
- Confirmación: requerida antes de iniciar cualquier validación de credenciales.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON documental:

```json
{
  "type": "macos_action",
  "device_id": "dev-mac-001",
  "technique_id": "macos.access.bruteforce_ssh",
  "params": {
    "target_ip": "192.168.1.20",
    "port": 22,
    "dictionary": "rockyou"
  },
  "expected_evidence": ["ssh_credentials", "shell_access"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Evidencia esperada:

- Credenciales SSH válidas solo enmascaradas por defecto.
- Captura de pantalla de la shell remota como evidencia documental, con redacción cuando contenga datos sensibles.
- `audit_log`, `panel_capture`, hashes SHA256, `timeline_json` y metadatos `session_id`, `device_id`, `VersionLock`.

#### Robar Token iCloud — Frida + objection

- Técnica: `macos.access.steal_token`.
- Requisito documental: acceso SSH o local al Mac y Frida disponible en el Mac objetivo dentro de un entorno autorizado.
- Parámetros: ruta de extracción del token del llavero o ruta documental de evidencia.
- Confirmación: requerida antes de cualquier intento y antes de revelar contenido completo.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON documental:

```json
{
  "type": "macos_action",
  "device_id": "dev-mac-001",
  "technique_id": "macos.access.steal_token",
  "params": {
    "extraction_path": "/tmp/token_extracted.txt"
  },
  "expected_evidence": ["icloud_token"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Evidencia esperada:

- Token de sesión de iCloud extraído, siempre enmascarado por defecto.
- `token_session.txt`, `keychain_extract_report`, `audit_log`, hashes SHA256, `timeline_json` y metadatos de cadena de custodia.
- Handoff a M5 como `credential_handoff` si se detectan tokens o credenciales.

#### Forzar Perfil MDM

- Técnica: `macos.access.force_mdm_profile`.
- Requisito documental: acceso SSH o local al Mac y SIP deshabilitado dentro de un laboratorio controlado.
- Parámetros: URL del perfil MDM preparado para el ejercicio autorizado.
- Confirmación: requerida antes de preparar, distribuir, instalar o registrar el perfil.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON documental:

```json
{
  "type": "macos_action",
  "device_id": "dev-mac-001",
  "technique_id": "macos.access.force_mdm_profile",
  "params": {
    "profile_url": "https://evil-server.com/mdm_profile.mobileconfig"
  },
  "expected_evidence": ["profile_installed", "remote_control_granted"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Evidencia esperada:

- Perfil MDM instalado dentro del laboratorio autorizado.
- Acceso remoto verificado como evidencia documental, sin afirmar persistencia real.
- `profile.mobileconfig`, `panel_capture`, `audit_log`, hashes SHA256 y `timeline_json`.

#### Keylogging — Frida + objection

- Técnica: `macos.access.keylogging`.
- Requisito documental: acceso SSH o local al Mac y Frida disponible en el objetivo, siempre bajo autorización explícita.
- Parámetros: duración del keylogging y filtro de aplicaciones.
- Confirmación: requerida antes de activar la captura y antes de revelar contenido completo.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON documental:

```json
{
  "type": "macos_action",
  "device_id": "dev-mac-001",
  "technique_id": "macos.access.keylogging",
  "params": {
    "duration_minutes": 30,
    "filter_apps": ["com.apple.mail", "com.apple.safari"]
  },
  "expected_evidence": ["keylog.csv"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Evidencia esperada:

- `keylog.csv` con pulsaciones registradas, enmascarado por defecto.
- Capturas del panel, `audit_log`, hashes SHA256, `timeline_json` y metadatos de acceso/revelado/exportación.
- Handoff a M5 si aparecen contraseñas, tokens o secretos en el registro.

### Errores y recuperación

- `ssh_unreachable`: el puerto 22 no está abierto o no es alcanzable; el panel bloquea la técnica y muestra el motivo.
- `bruteforce_blocked`: Policy, rate-limit, lockout o protección del servicio impide continuar; se pausa y se registra AuditLog.
- `token_extract_failed`: no existe acceso suficiente, Frida no está disponible o el llavero no permite extracción; Mistral sugiere revisar permisos o solicitar análisis Hermes.
- `mdm_profile_failed`: el perfil no se instala o SIP bloquea la ruta; se conserva evidencia parcial y se sugiere revisar preflight.
- `keylogging_blocked`: falta acceso local/SSH, Frida no está disponible o Policy deniega la técnica; no se ejecuta captura.
- `blocked_by_policy`: se muestra el motivo y se registra el intento si hubo solicitud del usuario.
- `kill_switch_triggered`: se detiene cualquier validación, captura, perfil, extracción o solicitud Hermes activa y se preservan evidencias pendientes.

### Criterios de aceptación del Módulo 13bis

El Módulo 13bis queda documentalmente cerrado si `docs/techniques/13bis_APPLE.md` contiene:

- [ ] Propósito del módulo documentado.
- [ ] Herramientas nominales y VersionLock documentados.
- [ ] Panel **Apple** documentado con subpestañas **iOS** y **macOS**.
- [ ] Estados visuales del panel documentados.
- [ ] Técnicas `ios.*` y `macos.*` documentadas con sus `technique_id` y contratos JSON.
- [ ] Técnicas de ataque físico USB documentadas.
- [ ] Técnicas de ataque remoto y phishing documentadas.
- [ ] Técnicas de ataque a macOS documentadas.
- [ ] Flujo de trabajo asistido (Mistral + X5 + Hermes) documentado.
- [ ] Handoffs con M5, M12 y M13 documentados.
- [ ] Scoring X5 y preparación para M16 documentados.
- [ ] Preflight checklist y manejo de errores documentados.
- [ ] No se afirma implementación real.

### Actualización de índices globales

Los índices globales existentes deben reflejar que el Módulo 13bis queda documentado como especificación de producto/laboratorio:

- `docs/MODULE_TOOL_INVENTORY.md`: añadir herramientas nominales de Apple: `libimobiledevice-utils`, `ideviceinstaller`, `checkra1n`, `Sliver`, `ipwndfu`, `Evilginx3`, `SET`, `Bettercap`, `mitmproxy`, `Hydra`, `Frida`, `objection`, `Dolphin Mistral Nemo 12B` y `Hermes (DeepSeek API)`.
- `docs/MODULE_ACCEPTANCE_CRITERIA.md`: añadir criterios de aceptación del Módulo 13bis.
- `AI_HANDOFF_OJO_DE_DIOS.md`: añadir nota de handoffs del módulo con M5, M12, M13 y M16.

### Nota final

El Módulo 13bis queda definido como especificación de producto/laboratorio. Esta documentación no crea lógica funcional ni afirma ejecución real sobre iOS o macOS. Las partes sensibles permanecen como `IMPLEMENTACION_USUARIO_REQUERIDA`, con redacción por defecto, confirmación explícita, Policy, Kill Switch, EvidenceStore y AuditLog.

## Ronda 13bis-6 — Handoff interno iOS/macOS e índices globales explícitos

### Alcance documental de la ronda

Esta ronda define los handoffs internos entre las subpestañas **iOS** y **macOS** del Módulo 13bis y deja documentada la actualización explícita de índices globales. Solo documentación: no implementa código, no crea endpoints, no crea workers, no modifica bases de datos, no añade tests, no introduce requirements y no crea scripts funcionales. Los handoffs descritos son contratos de producto/laboratorio con redacción por defecto, confirmación explícita, Policy, Kill Switch, EvidenceStore y AuditLog.

### Handoff interno entre iOS y macOS

El Módulo 13bis puede transferir hallazgos entre sus propias subpestañas para maximizar el valor de las evidencias obtenidas sin romper cadena de custodia ni asumir ejecución real. Todo valor sensible se transfiere enmascarado por defecto y el revelado completo requiere confirmación reforzada.

#### Handoff de iOS a macOS

- Si durante un ataque a iOS se obtienen credenciales de iCloud por phishing autorizado o extracción de backup, estas pueden usarse como insumo documental para evaluar un Mac vinculado a la misma cuenta.
- Flujo de panel: desde la subpestaña **iOS**, el usuario pulsa **"Usar en macOS"**. El sistema transfiere las credenciales a la subpestaña **macOS** y las rellena automáticamente, como valores enmascarados, en la técnica **"Robar Token iCloud"** o **"Fuerza Bruta SSH"** del Mac detectado en la red.
- Antes de activar cualquier técnica destino, X5 debe repetir preflight, validar Policy, Kill Switch, scope, operador, VersionLock, evidencia origen y confirmación explícita.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON interno:

```json
{
  "type": "apple_internal_handoff",
  "source_submodule": "ios",
  "target_submodule": "macos",
  "device_id_source": "dev-iphone-13",
  "device_id_target": "dev-mac-001",
  "evidence_ids": ["ev-icloud-cred"],
  "handoff_reason": "icloud_credentials_obtained",
  "operator": "admin"
}
```

Reglas documentales:

- `evidence_ids` debe apuntar a evidencia existente en EvidenceStore.
- Las credenciales se muestran enmascaradas por defecto.
- M5 conserva la clasificación de credenciales si el hallazgo fue enviado como `credential_handoff`.
- AuditLog registra origen, destino, operador, motivo, timestamp y estado de redacción.

#### Handoff de macOS a iOS

- Si durante un ataque a macOS se obtiene un token de sesión de iCloud desde el llavero o mediante keylogging autorizado, este token puede usarse como insumo documental para evaluar un iPhone vinculado a la misma cuenta, por ejemplo mediante funciones asociadas a iCloud como localización o control de bloqueo en un laboratorio controlado.
- Flujo de panel: desde la subpestaña **macOS**, el usuario pulsa **"Usar en iOS"**. El sistema transfiere el token a la subpestaña **iOS** como valor enmascarado y lo asocia al dispositivo iOS objetivo para una técnica autorizada posterior.
- Antes de usar el token, X5 debe repetir preflight, validar Policy, Kill Switch, scope, operador, VersionLock, evidencia origen y confirmación explícita reforzada.
- Estado sensible: `IMPLEMENTACION_USUARIO_REQUERIDA`.

Contrato JSON interno:

```json
{
  "type": "apple_internal_handoff",
  "source_submodule": "macos",
  "target_submodule": "ios",
  "device_id_source": "dev-mac-001",
  "device_id_target": "dev-iphone-13",
  "evidence_ids": ["ev-icloud-token"],
  "handoff_reason": "icloud_token_obtained",
  "operator": "admin"
}
```

Reglas documentales:

- El token se transfiere enmascarado por defecto y no se revela completo sin confirmación reforzada.
- La subpestaña iOS debe mostrar el origen del token, el `session_id`, la evidencia asociada y el estado de custodia.
- M5 debe recibir o conservar el token como credencial si procede.
- AuditLog registra el handoff interno y cualquier intento de uso posterior.

### Actualización explícita de índices globales

Los índices globales existentes deben incluir el Módulo 13bis como especificación cerrada de producto/laboratorio:

- `docs/MODULE_TOOL_INVENTORY.md`: añadir al final la lista explícita de herramientas nominales de Apple.
- `docs/MODULE_ACCEPTANCE_CRITERIA.md`: añadir al final los criterios explícitos del Módulo 13bis.
- `AI_HANDOFF_OJO_DE_DIOS.md`: añadir al final la nota operativa de handoffs del Módulo 13bis.

### Nota final

El Módulo 13bis queda completamente cerrado como especificación de producto y laboratorio. No se ha implementado lógica funcional ni se afirma ejecución real. Las partes sensibles permanecen marcadas como `IMPLEMENTACION_USUARIO_REQUERIDA`, con redacción por defecto, confirmación explícita, Policy, Kill Switch, EvidenceStore y AuditLog.
