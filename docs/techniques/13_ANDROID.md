# Módulo 13 — Ataques a Dispositivos Android

Documento base del Módulo 13 Android. Esta versión define la arquitectura documental esperada para el panel Android, los Vectores 1-6 y la herencia operativa desde el Módulo 12. No implementa lógica, endpoints, workers, base de datos, tests, dependencias ni cambios de Python.

## Índice del Módulo 13 Android

- [Filosofía heredada del Módulo 12](#filosofía-heredada-del-módulo-12)
- [Panel Android](#panel-android)
- [Vector 1: Interfaz, USB Directo y Red Móvil](#vector-1-interfaz-usb-directo-y-red-móvil)
- [Vector 2 — Generar Payload](#vector-2--generar-payload)
- [Vector 3 — Control Remoto Avanzado](#vector-3--control-remoto-avanzado)
- [Vector 4 — Ataque físico USB](#vector-4--ataque-físico-usb)
- [Vector 5 — Red Móvil / MITM](#vector-5--red-móvil--mitm)
- [Vector 6 — Análisis de Apps](#vector-6--análisis-de-apps)
- [Vector 7 — IMSI Catcher / BTS / RF Móvil](#vector-7--imsi-catcher--bts--rf-móvil)
- [Vector 8 — Servicio de Accesibilidad y Registro de Eventos](#vector-8--servicio-de-accesibilidad-y-registro-de-eventos)
- [Vector 9 — Capa de Conectividad](#vector-9--capa-de-conectividad)
- [Vector 10 — Carteras de Criptomonedas y Apps Financieras](#vector-10--carteras-de-criptomonedas-y-apps-financieras)
- [Vector 11 — Mensajería](#vector-11--mensajería)
- [Vector 12 pendiente](#vectores-futuros-pendientes)

## Filosofía heredada del Módulo 12

Android hereda la arquitectura del Módulo 12 y debe operar como un módulo técnico conectado al cerebro de orquestación de Ojo de Dios, no como una colección de comandos sueltos. La página Android debe traducir intención humana, contexto del dispositivo y estado de autorización en planes revisables antes de cualquier ejecución.

La arquitectura esperada del Módulo 13 funciona con los siguientes roles:

- **LaIA/Mistral como cerebro táctico contextual**: interpreta la intención del usuario, el estado del dispositivo, las evidencias disponibles y el objetivo autorizado para proponer planes JSON claros, ordenados y explicables.
- **X5/OjoRouter como validador/ejecutor**: recibe planes preparados por LaIA, valida scope, políticas, estado del Kill Switch, disponibilidad de herramientas y condiciones de ejecución antes de enrutar cualquier acción autorizada.
- **Hermes Agent como constructor de capacidades faltantes**: identifica huecos de capacidades Android y, cuando proceda, propone artefactos de laboratorio. Cualquier lógica sensible futura debe marcarse como `IMPLEMENTACION_USUARIO_REQUERIDA` y no debe asumirse como funcional hasta su promoción explícita.
- **DeepSeek como arquitecto avanzado**: apoya el diseño de capacidades complejas, flujos de laboratorio, parsers, contratos y propuestas técnicas avanzadas, sin sustituir validaciones de Policy Engine ni promoción humana.
- **Policy Engine, Scope, Kill Switch, EvidenceStore, AuditLog y scoring**: gobiernan autorización, límites, parada inmediata, preservación de evidencias, trazabilidad y evaluación de resultados.

El usuario opera desde panel, web o app usando lenguaje natural, botones y planes revisables. El flujo esperado no debe depender de comandos manuales: el usuario solicita una acción, LaIA prepara una propuesta técnica, X5 valida, el Policy Engine decide si está permitido, el Kill Switch puede detener y EvidenceStore/AuditLog registran lo ocurrido cuando exista una implementación futura.

Esta documentación no afirma que las técnicas descritas estén ya implementadas. Describe la base esperada para futuras rondas del Módulo 13 y conserva la misma filosofía de autonomía supervisada del Módulo 12.

## Panel Android

La página Android vive en la barra lateral de Ojo de Dios como módulo propio. Su función documental esperada es centralizar descubrimiento, análisis, planificación, acciones revisables, evidencias y evolución de capacidades Android bajo la cadena de control heredada del Módulo 12.

El panel Android contiene subpestañas iniciales:

- **USB Directo**: detección y análisis de dispositivos Android conectados físicamente.
- **Red Móvil**: detección de dispositivos Android o relacionados dentro de redes locales, WiFi o entornos de prueba autorizados.

El panel también reserva futuras secciones:

- **Generar Payload**.
- **Control Remoto**.
- **Ataque físico USB**.
- **Red Móvil / MITM**.
- **Análisis de Apps**.
- **Evidencias**.
- **Hermes Agent Lab**.

Estas secciones futuras son arquitectura documental. No implican endpoints activos, workers nuevos, ejecución real ni capacidades ya disponibles. Cualquier capacidad sensible que requiera implementación operativa deberá quedar marcada como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta que exista revisión, autorización y promoción explícita.

## Vector 1: Interfaz, USB Directo y Red Móvil

El Vector 1 establece la primera capa de interfaz Android: detectar dispositivos por conexión física USB y por presencia en red local, mostrar contexto técnico en tarjetas comprensibles y ofrecer acciones visibles según estado. Ningún botón ejecuta acciones directamente. Cada acción activa primero a LaIA para preparar un plan JSON revisable; después X5/OjoRouter valida scope, Policy Engine y Kill Switch antes de cualquier ejecución futura.

### USB Directo

La subpestaña **USB Directo** documenta la detección de dispositivos conectados físicamente al host de Ojo de Dios. Las fuentes previstas de detección son:

- `pyudev` en Linux/WSL para eventos y metadatos USB.
- WMI en Windows nativo para inventario y estado de dispositivos conectados.
- `adb devices` para dispositivos Android visibles por ADB.
- `fastboot devices` para dispositivos en modo bootloader/fastboot.
- `lsusb` para identificación USB de bajo nivel.
- Cruce VID/PID con `usb.ids` para enriquecer fabricante, familia o clase del dispositivo.

La tarjeta del dispositivo debe mostrar, cuando la información esté disponible:

- modelo/fabricante;
- tipo: móvil, tablet, TV Box, Android Auto, IoT, vehículo;
- Android/parche si está disponible;
- ADB activo/inactivo y autorizado/no autorizado;
- pantalla bloqueada/desbloqueada;
- bootloader bloqueado/desbloqueado.

Las acciones visibles se calculan según el estado detectado y deben aparecer como botones de planificación, no como ejecución directa:

- **Extraer Datos**;
- **Instalar Payload**;
- **Bypass Pantalla**;
- **Forzar ADB**;
- **Rootear si bootloader desbloqueado**;
- **Flashear Magisk**;
- **Desbloquear Bootloader**.

Regla operativa documental: ningún botón ejecuta directo. Al pulsar una acción, LaIA prepara un plan JSON revisable con técnica, herramienta, parámetros, evidencias esperadas, riesgo y criterios de parada. X5/OjoRouter solo ejecutaría tras validación de Policy Engine, scope y Kill Switch en una implementación futura. Las rutas sensibles como bypass, forzar ADB, root, flasheo o desbloqueo deben tratarse como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta que exista una implementación real, autorizada y auditada.

### Red Móvil

La subpestaña **Red Móvil** documenta la detección de dispositivos en WiFi local o redes de laboratorio autorizadas. Su objetivo inicial es identificar activos Android o relacionados, enriquecerlos con metadatos y permitir que el usuario pulse **Analizar** para obtener una propuesta LaIA revisable.

Fuentes previstas de detección y análisis:

- `arp-scan` para descubrimiento local de IP/MAC y fabricante.
- `tcpdump` para observar tráfico mDNS/SSDP en entornos autorizados.
- `nmap` con scripts `http-title`, `mdns-query` y `upnp-info` para títulos HTTP, nombres multicast, UPnP y servicios expuestos.

Por cada dispositivo detectado, la interfaz debe mostrar:

- IP;
- MAC;
- fabricante;
- modelo si se identifica;
- puertos abiertos;
- botón **Analizar**.

Acciones previstas para futuras rondas:

- **MITM**;
- **Explotar Servicios**;
- **IMSI Catcher si HackRF conectado**.

Estas acciones deben mostrarse como rutas de planificación y análisis, no como afirmaciones de ejecución actual. MITM, explotación de servicios e IMSI Catcher son capacidades sensibles y deben marcarse como `IMPLEMENTACION_USUARIO_REQUERIDA` cuando requieran lógica operativa, hardware, permisos específicos, laboratorio controlado o validaciones adicionales.

### Asistencia LaIA

Al pulsar una acción dentro del Vector 1, LaIA muestra un modal de revisión antes de cualquier ejecución. El modal debe incluir:

- técnica propuesta;
- herramienta prevista;
- versión o familia de herramienta cuando esté disponible;
- parámetros propuestos;
- evidencias esperadas;
- riesgo operativo;
- precondiciones y criterios de parada;
- botón **Ejecutar**.

El botón **Ejecutar** no equivale a ejecución libre. X5/OjoRouter debe validar Policy Engine, scope, Kill Switch, disponibilidad de herramientas, requisitos de confirmación y trazabilidad. Si alguna condición falla, la acción queda bloqueada, se explica el motivo al usuario y se registra en AuditLog cuando exista la implementación correspondiente.

## Vector 2 — Generar Payload

El Vector 2 documenta la arquitectura asistida para generación de payload Android dentro del flujo autorizado de Ojo de Dios. Esta sección amplía el diseño del panel, contratos, técnicas registradas y evidencias esperadas, pero no crea generadores funcionales, comandos operativos, endpoints, workers, base de datos, dependencias ni pruebas. Toda lógica operativa sensible queda marcada como `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Ubicación en panel

El bloque **Generar Payload** vive dentro de:

```text
Android > USB Directo > Generar Payload
```

Este bloque debe ser un panel asistido por LaIA, no una consola manual. El usuario puede completar campos guiados o pulsar **Generar con IA** para que LaIA proponga una configuración desde el contexto autorizado del laboratorio, el dispositivo conectado, las herramientas disponibles y las técnicas registradas.

El panel no debe presentar comandos crudos ni asumir que una técnica ya funciona. La interacción esperada es: formulario, explicación contextual, plan JSON revisable, validación X5/OjoRouter y evidencia trazable si en el futuro existe un worker autorizado.

### Campos del formulario

El formulario documental de **Generar Payload** debe exponer estos campos:

- **tipo payload**: `reverse_tcp`, `reverse_https`, `bind_tcp`.
- **LHOST**: autocompletado por LaIA desde el contexto de laboratorio autorizado, editable por el usuario antes de confirmar.
- **LPORT**: autocompletado por LaIA desde el contexto de laboratorio autorizado, editable por el usuario antes de confirmar.
- **ofuscación**:
  - Ninguna;
  - ProGuard/R8;
  - Obfuscapk;
  - Donut+ScareCrow;
  - Polimórfico IA.
- **inyectar en APK señuelo**: ON/OFF, con opción de seleccionar una biblioteca controlada por el sistema o subir APK propia para análisis autorizado.
- **firma APK**:
  - certificado de prueba;
  - certificado autorizado del EvidenceStore;
  - generar automático.
- **objetivo**:
  - dispositivo conectado/autorizado;
  - artefacto APK sin instalación.
- **modo**:
  - generar;
  - generar+firmar;
  - generar+instalar por ADB autorizado.

Los valores autocompletados por LaIA deben mostrarse como propuesta revisable, no como imposición. Cualquier selección que active generación, firma, instalación, ofuscación avanzada, inyección en APK señuelo o variantes polimórficas queda sujeta a `IMPLEMENTACION_USUARIO_REQUERIDA`, scope explícito, Policy Engine, Kill Switch y aprobación humana.

### Flujo asistido

El flujo documental esperado es:

1. El usuario pulsa **Generar con IA** dentro del bloque **Generar Payload**.
2. LaIA analiza el dispositivo, versión Android/parche, estado ADB, Play Protect si el dato está disponible, herramientas presentes en el entorno y técnicas registradas para Android.
3. LaIA genera un `attack_plan` con parámetros propuestos, técnica elegida, riesgos, precondiciones, criterios de parada y evidencias esperadas.
4. El panel muestra un modal revisable con resumen técnico, campos editables, riesgo, evidencia prevista y botón de confirmación.
5. El usuario confirma o cancela.
6. X5/OjoRouter valida Policy Engine, Kill Switch, scope, permisos, estado del dispositivo, modo seleccionado, disponibilidad de herramientas y compatibilidad con VersionLock.
7. Si la validación es positiva y existe implementación futura aprobada, X5 enruta la tarea mediante un worker futuro.
8. El progreso se reporta por WebSocket al panel.
9. La APK final, si se genera, queda registrada como artefacto/evidencia en EvidenceStore junto con metadatos, hash, configuración y AuditLog.

Este flujo mantiene la potencia como arquitectura asistida LaIA/X5/Hermes sin exponer instrucciones operativas de abuso ni comandos de payload. La generación real, la firma real, la instalación por ADB y cualquier canal de sesión resultante permanecen como `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Herramientas objetivo y VersionLock

Las herramientas objetivo se documentan como capacidades posibles del ecosistema, sin instalación ni ejecución en esta ronda:

- **Metasploit/msfvenom**: framework 6.x, con versión exacta resuelta por VersionLock/Kali antes de cualquier implementación.
- **Apktool**: preferir versión verificada actual por VersionLock; `2.9.3` queda solo como referencia histórica si el entorno ya la trae.
- **Android SDK Build Tools**: `zipalign` y `apksigner` para alineación y firma cuando exista flujo autorizado.
- **keytool / JDK**: gestión de claves y certificados dentro de un flujo auditado.
- **ProGuard/R8**: ofuscación compatible con proyectos Android y pipelines permitidos.
- **Obfuscapk**: ofuscación de APK como capacidad futura controlada.
- **Donut y ScareCrow**: capacidad avanzada/laboratorio Windows para escenarios autorizados y aislados.
- **fatrat**: alternativa documentada para evaluación técnica futura, sin habilitación operativa en esta ronda.

Toda versión final debe pasar por VersionLock antes de implementación. VersionLock debe registrar versión detectada, fuente, compatibilidad, decisión de uso y bloqueo de ejecución si la versión no cumple los criterios aprobados. La presencia de una herramienta en esta lista no implica que esté instalada, soportada ni autorizada para ejecución.

### Técnicas registradas

Las siguientes técnicas quedan documentadas como registros esperados de catálogo. Cada una debe tratarse como contrato de arquitectura hasta que exista implementación aprobada, sandbox, revisión y promoción:

#### `android.payload.msfvenom_basic`

- **description**: generación básica de payload Android para laboratorio autorizado y artefacto APK controlado.
- **tool**: Metasploit/msfvenom bajo VersionLock.
- **required_inputs**: tipo payload, LHOST, LPORT, objetivo, modo, scope autorizado y política aplicable.
- **expected_evidence**: APK generada, hash SHA256, configuración usada, log de generación, versión de herramienta y AuditLog de aprobación.
- **risk_level**: alto.
- **worker_future**: `android_payload_worker` o equivalente futuro aprobado.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.payload.backdoor_apk`

- **description**: inyección controlada en APK señuelo seleccionada o subida por el usuario dentro de scope autorizado.
- **tool**: Apktool, Android SDK Build Tools, keytool/JDK y motor de payload validado por VersionLock.
- **required_inputs**: APK señuelo, tipo payload, LHOST, LPORT, política de firma, objetivo, modo y autorización explícita.
- **expected_evidence**: APK original referenciada, APK modificada, hash SHA256 de ambos artefactos, configuración usada, log de reconstrucción, firma/certificado usado y AuditLog.
- **risk_level**: crítico.
- **worker_future**: `android_payload_worker` con parser de artefactos APK futuro.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.payload.obfuscation_proguard`

- **description**: aplicación de ofuscación ProGuard/R8 sobre artefacto Android autorizado cuando el flujo técnico sea compatible.
- **tool**: ProGuard/R8 bajo VersionLock.
- **required_inputs**: APK/proyecto autorizado, perfil de ofuscación, modo de firma, objetivo y política aplicable.
- **expected_evidence**: artefacto ofuscado, configuración de ofuscación, hash SHA256, log de transformación, firma usada y AuditLog.
- **risk_level**: medio-alto.
- **worker_future**: `android_obfuscation_worker` o etapa futura dentro de `android_payload_worker`.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.payload.obfuscation_obfuscapk`

- **description**: ofuscación de APK con Obfuscapk para variantes autorizadas y trazables.
- **tool**: Obfuscapk bajo VersionLock y sandbox.
- **required_inputs**: APK autorizado, perfil de ofuscación, firma, objetivo, modo y scope.
- **expected_evidence**: APK ofuscada, hash SHA256, perfil aplicado, log de ofuscación, firma/certificado usado y AuditLog.
- **risk_level**: alto.
- **worker_future**: `android_obfuscation_worker` con evidencia normalizada futura.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.payload.fileless_donut`

- **description**: capacidad avanzada de laboratorio para estudiar variantes sin archivo o cargadores en entorno Windows controlado.
- **tool**: Donut y ScareCrow como laboratorio Windows, con restricciones de sandbox y aprobación reforzada.
- **required_inputs**: artefacto de laboratorio autorizado, perfil de carga, objetivo de prueba, entorno aislado y aprobación explícita.
- **expected_evidence**: artefacto de laboratorio, hash SHA256, configuración usada, log de generación, entorno de sandbox, resultado de validación y AuditLog.
- **risk_level**: crítico.
- **worker_future**: módulo de laboratorio Hermes Agent, no producción directa.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.payload.polymorphic_ai`

- **description**: generación de variantes polimórficas asistidas por IA para investigación controlada, medición de detección y pruebas defensivas autorizadas.
- **tool**: LaIA/Hermes Agent con herramientas de empaquetado Android validadas por X5 y VersionLock.
- **required_inputs**: técnica base, restricciones de laboratorio, objetivo autorizado, límites de variación, política de firma, criterios de parada y aprobación humana.
- **expected_evidence**: variante generada, hash SHA256, diff o manifiesto de transformación, configuración usada, scoring, log del laboratorio y AuditLog de aprobación.
- **risk_level**: crítico.
- **worker_future**: Hermes Agent Lab en `modules/laboratory/<technique_id>/` con promoción controlada.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Hermes Agent para capacidades faltantes

Si falta soporte para una versión Android, una protección concreta, una ofuscación nueva, una variante de payload, un parser o una integración de herramienta, LaIA debe activar Hermes Agent como constructor de capacidades faltantes. Hermes Agent trabaja en laboratorio, no en producción directa.

La estructura documental esperada para una técnica creada por Hermes Agent es:

```text
modules/laboratory/<technique_id>/
  technique.json
  worker.py
  parser
  evidence_schema.json
  requirements.generated.txt
  README.md
```

La promoción desde laboratorio solo puede ocurrir tras sandbox, revisión humana, validación X5/OjoRouter, VersionLock, aprobación de dependencias, compatibilidad con Policy Engine, pruebas de evidencias y registro en AuditLog. Hermes Agent no instala dependencias, no modifica workers productivos y no habilita payloads reales por sí mismo.

### Evidencias

El Vector 2 debe registrar evidencias completas cuando exista implementación futura autorizada. El paquete mínimo de evidencia esperado incluye:

- APK generada como artefacto;
- hash SHA256;
- configuración usada;
- log de generación;
- firma/certificado usado;
- estado de instalación ADB si aplica;
- captura de panel;
- sesión resultante si se produce;
- AuditLog de aprobación.

Estas evidencias deben asociarse al scope, dispositivo o artefacto APK, usuario aprobador, técnica registrada, versiones VersionLock, riesgos aceptados y resultado final. La ausencia de evidencia suficiente debe bloquear scoring positivo y promoción de capacidades.

## Nota común para Vectores 2-5 — Herramientas, VersionLock y Hermes Agent

Las versiones citadas por el usuario o por esta documentación en los Vectores 2-5 son referencias nominales. La implementación futura debe resolver la versión real mediante VersionLock y `tool_healthcheck`; no se deben fijar como definitivas versiones antiguas si existe una versión actual más adecuada, compatible y aprobada. Para cada herramienta se debe registrar fuente, versión, hash si aplica, compatibilidad, decisión de uso y motivo de bloqueo o uso.

Cuando falte técnica, wrapper, parser, canal C2, WebRTC, `evidence_schema`, integración de herramienta o soporte por versión, modelo o app, Mistral/LaIA debe activar Hermes Agent. Hermes Agent genera en `modules/laboratory/<technique_id>/` los artefactos documentales esperados: `technique.json`, `worker.py`, `parser`, `evidence_schema.json`, `requirements.generated.txt` y `README`. Nada se promociona sin sandbox, revisión, aprobación humana, VersionLock, Policy Engine, Kill Switch, EvidenceStore y AuditLog.

## Vector 3 — Control Remoto Avanzado

El Vector 3 documenta el centro de control remoto avanzado para dispositivos Android comprometidos o autorizados dentro de scope explícito. Esta sección define panel, sesiones, contratos, técnicas nominales y evidencias; no implementa capacidades operativas, canales C2, workers, endpoints, persistencia, listeners, dependencias ni comandos. Toda lógica sensible de control remoto queda marcada como `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Ubicación y propósito

La subpestaña/sección **Android > Control Remoto** solo aparece cuando existe un dispositivo comprometido/autorizado por USB, payload o red y cuando el contexto de autorización permite visualizar sesiones remotas. No debe mostrarse como una lista simple de botones: debe funcionar como centro de mando interactivo asistido por LaIA, con estado de sesión, telemetría, evidencias, acciones revisables y cierre seguro.

El objetivo documental del panel es permitir que el usuario opere mediante lenguaje natural, tarjetas de estado y acciones confirmables. LaIA traduce intención en contratos `remote_action`; X5/OjoRouter valida Policy Engine, Scope, Kill Switch y estado de sesión; un worker futuro ejecutaría solo si existe implementación aprobada.

### Páginas internas del Control Remoto

El Control Remoto debe organizarse en páginas internas, no en botones sueltos. Cada página muestra contexto, plan LaIA, estado, riesgo, progreso, evidencias esperadas y acciones permitidas bajo Policy Engine, Scope, Kill Switch, EvidenceStore y AuditLog:

- **Dashboard del dispositivo**: online/offline, batería, operador, conectividad WiFi/4G/5G, ubicación cuando esté permitida, miniatura periódica, sensores activos y canal remoto vigente.
- **Sesiones activas**: tabla con dispositivo, estado, canal C2, última actividad, operador y acciones **Ver detalles**, **Abrir control** y **Cerrar sesión**.
- **Consola LaIA**: convierte lenguaje natural en contrato `remote_action`; LaIA/Mistral prepara el plan, X5/OjoRouter lo valida, un worker futuro lo ejecutaría solo si existe implementación aprobada y EvidenceStore normaliza el resultado.
- **Streaming**: cámara, micrófono y pantalla en vivo como capacidades documentales bajo confirmación reforzada. `scrcpy` y WebRTC son opciones documentales sujetas a VersionLock, `tool_healthcheck`, soporte por versión/modelo y promoción humana.
- **Árbol de archivos**: navegación de carpetas, descarga de archivos o directorios, subida de artefactos autorizados y guardado de `file_tree_json` como evidencia.
- **Evidencias**: imagen, audio, vídeo, ubicación, SMS, contactos, cookies, `command_log`, `timeline` y metadatos de aprobación asociados a dispositivo, sesión, técnica y operador.
- **Hermes Agent Lab**: creación de canal C2, parser, WebRTC, `evidence_schema` o soporte de modelo/app cuando falte capacidad; todo queda en laboratorio hasta sandbox, revisión, aprobación humana y promoción controlada.


### Dashboard del dispositivo

El dashboard del dispositivo debe mostrar tarjetas o widgets de estado con datos disponibles y trazables:

- **online/offline**;
- **batería**;
- **operador**;
- **conexión WiFi/4G/5G**;
- **ubicación en mapa si está disponible**;
- **captura periódica**;
- **sensores activos**: cámara, micrófono, GPS;
- **canal activo**: ADB, WebSocket, FCM, DNS, DoH, WebRTC.

La disponibilidad de estas tarjetas no implica que los sensores puedan activarse libremente. Cada dato sensible debe depender de autorización, consentimiento/scope aplicable, técnica registrada, evidencia esperada, confirmación cuando proceda y validación X5 antes de cualquier ejecución futura.

### Consola asistida por LaIA

La sección **Control Remoto** incluye un campo de lenguaje natural asistido por LaIA/Mistral. No es una terminal manual ni un shell crudo. El usuario describe una intención de alto nivel; LaIA/Mistral la convierte en una técnica registrada, rellena parámetros mínimos, estima riesgo, define evidencias esperadas y genera un contrato `remote_action` revisable.

Flujo documental esperado:

1. El usuario escribe una intención en lenguaje natural o selecciona una acción guiada.
2. LaIA/Mistral identifica la técnica registrada aplicable y completa parámetros desde el contexto del dispositivo, la sesión, el scope y las evidencias existentes.
3. El panel muestra un modal con contrato `remote_action`, riesgo, confirmación requerida, permisos y evidencias esperadas.
4. El usuario confirma o cancela.
5. X5/OjoRouter valida Policy Engine, Scope, Kill Switch, estado de sesión, canal activo, permisos, técnica registrada y necesidad de confirmación reforzada.
6. Un worker futuro ejecutaría la acción solo si existe implementación aprobada y el resultado vuelve al panel con evidencias normalizadas.

Cualquier acción sobre cámara, micrófono, pantalla, accesibilidad, 2FA, cookies, persistencia o C2 debe permanecer como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta existir implementación real, revisión, sandbox, aprobación y controles de evidencia.

### Técnicas registradas nominales

Las siguientes técnicas quedan documentadas como registros nominales de catálogo. No son capacidades activas y no deben interpretarse como implementación disponible. Cada técnica conserva `implementation_status: IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.rat.camera_stream`

- **description**: transmisión o captura controlada de cámara en dispositivo autorizado.
- **required_inputs**: device_id, session_id, canal activo, cámara objetivo, duración/límite, scope y confirmación explícita.
- **expected_evidence**: `image_file` o `video_file`, metadatos de sesión, timestamp, permisos validados y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí, reforzada.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.rat.mic_stream`

- **description**: transmisión o captura controlada de micrófono en dispositivo autorizado.
- **required_inputs**: device_id, session_id, canal activo, duración/límite, scope y confirmación explícita.
- **expected_evidence**: `audio_file`, metadatos de sesión, timestamp, permisos validados y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí, reforzada.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.rat.screen_stream`

- **description**: visualización o captura de pantalla autorizada para soporte, auditoría o laboratorio.
- **required_inputs**: device_id, session_id, canal activo, modo de visualización, duración/límite, scope y confirmación.
- **expected_evidence**: `image_file` o `video_file`, estado de stream, metadatos, timestamp y AuditLog.
- **risk_level**: alto.
- **confirmation_required**: sí.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.rat.accessibility_keylogging`

- **description**: captura controlada de eventos de accesibilidad para auditoría de exposición en entorno autorizado.
- **required_inputs**: device_id, session_id, servicio de accesibilidad autorizado, ventana temporal, filtros, scope y confirmación reforzada.
- **expected_evidence**: `command_log`, eventos normalizados, metadatos de permisos, timestamp y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí, reforzada.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.rat.accessibility_2fa_theft`

- **description**: técnica nominal de laboratorio para modelar abuso de accesibilidad contra códigos 2FA en pruebas defensivas autorizadas.
- **required_inputs**: device_id, session_id, app/flujo autorizado, ventana temporal, scope, justificación y confirmación reforzada.
- **expected_evidence**: `command_log`, evidencia de bloqueo/permitido por política, timestamp, riesgo aceptado y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí, reforzada y con bloqueo por defecto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.rat.accessibility_touch_simulation`

- **description**: simulación de interacción táctil mediante canal autorizado para pruebas controladas y soporte.
- **required_inputs**: device_id, session_id, objetivo de pantalla, acción solicitada, límites, scope y confirmación.
- **expected_evidence**: `command_log`, captura antes/después si procede, timestamp y AuditLog.
- **risk_level**: alto.
- **confirmation_required**: sí.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.rat.overlay_attack`

- **description**: técnica nominal de laboratorio para estudiar superposiciones maliciosas y validar controles defensivos.
- **required_inputs**: device_id, session_id, app objetivo autorizada, plantilla de laboratorio, límites, scope y confirmación reforzada.
- **expected_evidence**: `image_file`, `command_log`, metadatos de política, timestamp y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí, reforzada y con bloqueo por defecto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.rat.cookie_theft`

- **description**: técnica nominal de laboratorio para modelar extracción no autorizada de cookies y validar protección de datos.
- **required_inputs**: device_id, session_id, contenedor/app autorizada, scope de datos, justificación y confirmación reforzada.
- **expected_evidence**: `cookie_json` solo si está permitido por política, `command_log`, timestamp y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí, reforzada y con bloqueo por defecto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.rat.c2_over_fcm`

- **description**: canal C2 nominal sobre FCM para laboratorio autorizado y telemetría controlada.
- **required_inputs**: device_id, session_id, proyecto autorizado, canal, límites de mensajes, scope y confirmación.
- **expected_evidence**: `command_log`, metadatos de canal, última actividad, errores y AuditLog.
- **risk_level**: alto.
- **confirmation_required**: sí.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.rat.c2_over_websocket`

- **description**: canal C2 nominal sobre WebSocket para sesiones de laboratorio y control interactivo autorizado.
- **required_inputs**: device_id, session_id, endpoint autorizado, canal, límites, scope y confirmación.
- **expected_evidence**: `command_log`, metadatos de sesión, latencia/estado, última actividad y AuditLog.
- **risk_level**: alto.
- **confirmation_required**: sí.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.rat.c2_over_doh`

- **description**: canal C2 nominal sobre DoH para investigación controlada de evasión y detección defensiva.
- **required_inputs**: device_id, session_id, resolver autorizado, canal, límites, scope y confirmación reforzada.
- **expected_evidence**: `command_log`, metadatos de resolución, errores, última actividad y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí, reforzada.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.rat.persistence_system_app`

- **description**: persistencia nominal como app de sistema para laboratorio Android controlado, nunca producción directa.
- **required_inputs**: device_id, session_id, estado root/bootloader, artefacto autorizado, plan de reversión, scope y confirmación reforzada.
- **expected_evidence**: `command_log`, estado de instalación, plan de retirada, hash de artefacto, timestamp y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí, reforzada y con plan de retirada obligatorio.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Herramientas nominales y VersionLock

Las herramientas nominales se documentan sin instalación, sin fijar versiones obligatorias y sin asumir disponibilidad:

- **scrcpy**: versión nominal; versión real a resolver con VersionLock.
- **AhMyth**: versión nominal; resolver disponibilidad, compatibilidad y riesgo por VersionLock antes de cualquier laboratorio.
- **SpyNote**: versión nominal; resolver disponibilidad, compatibilidad y riesgo por VersionLock antes de cualquier laboratorio.
- **Frida + objection**: versión nominal; versión real a resolver con VersionLock.
- **Python websockets**: versión nominal; resolver por VersionLock y política de dependencias antes de implementación.
- **dnscat2**: versión nominal; resolver por VersionLock y sandbox antes de uso.
- **Firebase Admin SDK**: versión nominal; resolver por VersionLock, credenciales autorizadas y Policy Engine.
- **Hermes/DeepSeek para C2 personalizado**: capacidad de laboratorio para diseño de canales o parsers, nunca promoción automática.

VersionLock debe resolver versión real, fuente, compatibilidad, riesgo, dependencias y estado de soporte antes de cualquier implementación futura. La documentación de una herramienta nominal no equivale a instalación, soporte ni autorización operativa.

### Sesiones remotas

Las sesiones remotas deben modelarse con estados claros:

- `disconnected`;
- `connecting`;
- `online`;
- `streaming`;
- `recording`;
- `file_browsing`;
- `command_running`;
- `error`;
- `closed`.

El panel de sesiones activas debe mostrar:

- dispositivo modelo+IP;
- estado;
- canal C2;
- última actividad;
- acciones: **Ver detalles**, **Abrir control**, **Cerrar sesión**.

El cambio de estado debe ser auditable y reflejarse en el panel en tiempo real cuando exista implementación futura. Los estados `streaming`, `recording`, `file_browsing` y `command_running` deben tener límites, evidencia esperada, confirmación y criterios de parada.

### Contrato JSON `remote_action`

El contrato documental `remote_action` debe contener estos campos:

- `type: remote_action`;
- `device_id`;
- `session_id`;
- `action_type`;
- `technique_id`;
- `params`;
- `expected_evidence`;
- `permissions_check`;
- `scope`;
- `operator`;
- `requires_confirmation`;
- `risk_level`;
- `timeout`;
- `stop_conditions`.

Ejemplo documental no ejecutable:

```json
{
  "type": "remote_action",
  "device_id": "android-device-autorizado",
  "session_id": "session-documental",
  "action_type": "screen_stream",
  "technique_id": "android.rat.screen_stream",
  "params": {
    "duration_seconds": 60,
    "quality": "documental"
  },
  "expected_evidence": ["video_file", "command_log", "timeline"],
  "permissions_check": ["scope_valid", "device_authorized", "session_online"],
  "scope": "laboratorio_autorizado",
  "operator": "operador_autorizado",
  "requires_confirmation": true,
  "risk_level": "alto",
  "timeout": 120,
  "stop_conditions": ["kill_switch", "scope_revoked", "operator_cancelled"]
}
```

Este contrato es una especificación documental, no un endpoint ni un schema implementado. X5/OjoRouter debe rechazar cualquier `remote_action` sin scope válido, operador, técnica registrada, confirmación requerida cuando aplique, permisos suficientes, estado de sesión compatible, `risk_level`, `timeout`, `stop_conditions` y Kill Switch desactivado. Cámara, micrófono, accesibilidad, cookies, 2FA, persistencia y C2 requieren confirmación reforzada y permanecen como `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Evidencias de control remoto

Los tipos de evidencia esperados para Vector 3 son:

- `image_file`;
- `audio_file`;
- `video_file`;
- `location_json`;
- `sms_csv`;
- `contacts_csv`;
- `file_tree_json`;
- `command_log`;
- `cookie_json`.

Cada evidencia debe asociarse a device_id, session_id, technique_id, action_type, operador, timestamp, scope, canal activo, riesgo aceptado y estado de aprobación. Las evidencias de mayor sensibilidad, como audio, video, ubicación, SMS, contactos o cookies, deben requerir confirmación reforzada y validación de política antes de cualquier recolección futura.

### Cierre seguro

El cierre seguro de una sesión remota debe incluir:

- parar streams;
- guardar evidencias pendientes;
- cerrar canal C2;
- retirar persistencia si el usuario lo solicita;
- AuditLog con timestamp/operador;
- scoring X5;
- estado `closed`.

El cierre debe estar disponible desde el panel de sesiones y desde el Kill Switch cuando aplique. Si se solicita retirar persistencia, esa retirada también debe pasar por plan revisable, validación X5/OjoRouter y evidencia de resultado.

### Hermes Agent para control remoto

Hermes Agent entra cuando falta canal C2, parser, WebRTC, técnica concreta, soporte por versión/modelo, bypass específico o compatibilidad con un entorno Android particular. LaIA puede solicitar a Hermes Agent un módulo funcional de laboratorio, pero no una promoción directa.

Hermes Agent debe generar la capacidad en `modules/laboratory/<technique_id>/`, probarla en sandbox, documentar evidencias, declarar dependencias generadas, permitir revisión humana y promocionar solo tras aprobación explícita, validación X5/OjoRouter, VersionLock, Policy Engine y AuditLog. Hasta esa promoción, cualquier capacidad de control remoto avanzada permanece como `IMPLEMENTACION_USUARIO_REQUERIDA`.

## Vector 4 — Ataque físico USB

El Vector 4 documenta la arquitectura asistida para escenarios físicos USB autorizados: identificación, comunicación, bypass/desbloqueo, root/escalada, extracción forense, persistencia física, consentimiento informado y evidencias. Esta sección no implementa comandos, exploits, flujos de flasheo, workers, endpoints, dependencias ni lógica operativa. Toda lógica sensible queda marcada como `IMPLEMENTACION_USUARIO_REQUERIDA` y subordinada a LaIA/Mistral, X5/OjoRouter, EvidenceStore, AuditLog, Policy Engine, Scope y Kill Switch.

### Filosofía

Al conectar un dispositivo por USB, Ojo de Dios no debe asumir que se trata de un móvil genérico. LaIA/Mistral debe clasificar el dispositivo conectado como uno de estos tipos, cuando el contexto y la identificación técnica lo permitan:

- móvil;
- tablet;
- TV Box;
- Android Auto;
- IoT;
- vehículo;
- embebido.

El flujo se organiza por capas, de menor a mayor invasividad:

- **Capa 0: identificación y comunicación**. Detectar VID/PID, fabricante, modelo, modo USB, ADB, fastboot, MTP/PTP, recovery y señales de dispositivo embebido.
- **Capa 1: bypass/desbloqueo**. Evaluar rutas nominales de desbloqueo o recuperación solo bajo autorización, consentimiento y política vigente.
- **Capa 2: root/escalada**. Analizar si existe bootloader desbloqueado, recovery compatible, CVE aplicable o técnica de escalada documentada por modelo/parche.
- **Capa 3: extracción y persistencia física**. Preparar extracción forense, preservación de evidencias y persistencia física únicamente cuando aplique, con doble confirmación si modifica sistema.

LaIA debe ordenar alternativas por invasividad y riesgo antes de proponer cualquier plan. X5/OjoRouter valida cada transición de capa contra scope, Policy Engine, Kill Switch, estado del dispositivo, evidencias requeridas y consentimiento.

### Páginas dentro de USB Directo

Dentro de **Android > USB Directo**, el Vector 4 debe documentarse como una barra lateral interna con páginas especializadas:

- **Dispositivo conectado**;
- **Identificación y comunicación**;
- **Bypass / Desbloqueo**;
- **Root / Escalada**;
- **Extracción forense**;
- **Persistencia física**;
- **Consentimiento y riesgos**;
- **Evidencias**;
- **Historial / AuditLog**;
- **Hermes Agent Lab si dispositivo no soportado**.

Estas páginas deben mostrar planes revisables, estado, riesgos, evidencias y acciones guiadas. No deben convertirse en terminal manual ni ejecutar acciones directas sin `attack_plan`, validación X5/OjoRouter y controles de política.

### Estados visuales

La barra superior del Vector 4 debe mostrar, como mínimo, modelo, Android/parche, estado ADB, estado bootloader y estado root. Los estados visuales esperados son:

- `Detectando`;
- `Identificado`;
- `ADB autorizado`;
- `ADB no autorizado`;
- `Fastboot`;
- `Recovery`;
- `Bloqueado`;
- `Desbloqueado`;
- `Root disponible`;
- `Extracción en curso`;
- `Evidencia generada`;
- `Error`;
- `Bloqueado por Policy/Kill Switch`.

Cada cambio de estado debe quedar asociado a fuente de detección, timestamp, operador, dispositivo y evento de AuditLog cuando exista implementación futura. El estado `Bloqueado por Policy/Kill Switch` debe prevalecer sobre cualquier acción en cola.

### Identificación y comunicación

La fase de identificación debe combinar varias fuentes para clasificar el dispositivo y su modo de conexión:

- `lsusb` o WMI para VID/PID;
- cruce VID/PID con `usb.ids`;
- `adb devices` para presencia ADB y autorización;
- `fastboot devices` para modo bootloader/fastboot;
- MTP/PTP para exposición de almacenamiento o modo multimedia;
- UART para IoT/embebidos si el pinout es conocido y el alcance autorizado lo permite.

La interfaz debe mostrar, cuando esté disponible:

- modelo;
- fabricante;
- tipo;
- ADB;
- bootloader;
- Android/parche.

La identificación no autoriza por sí sola bypass, root, extracción o modificación. Solo aporta contexto a LaIA/Mistral para preparar planes y a X5/OjoRouter para validar viabilidad y límites.

### Bypass / desbloqueo

Las técnicas nominales de bypass/desbloqueo quedan documentadas como rutas de análisis, no como implementación disponible:

- **Android-PIN-Bruteforce**;
- **crackeo offline de archivos de bloqueo si hay root/recovery**;
- **recovery/TWRP temporal si bootloader desbloqueado**;
- **exploits de kernel por CVE/modelo/parche**;
- **Find My Device si el usuario dispone de cuenta vinculada**.

La lógica sensible de bypass/desbloqueo queda `IMPLEMENTACION_USUARIO_REQUERIDA`. LaIA/Mistral debe proponer alternativas por invasividad, explicar precondiciones y evidencias, y bloquear rutas no autorizadas. X5/OjoRouter debe validar scope, Policy Engine, Kill Switch, modelo, parche, estado ADB/recovery/bootloader y consentimiento antes de cualquier ejecución futura.

### Root / escalada

Las rutas nominales de root/escalada quedan documentadas como arquitectura futura:

- **Magisk por bootloader desbloqueado**;
- **módulos Magisk de persistencia**;
- **mtk-su**;
- **Dirty Pipe**;
- **exploits específicos por fabricante vía Hermes Agent**.

Versiones reales de herramientas, exploits y compatibilidad por modelo/parche se resolverán por VersionLock. Magisk `26.4` puede mantenerse únicamente como referencia histórica si aparece en entornos o documentación previa, pero no debe fijarse como versión definitiva ni obligatoria.

Toda escalada, flasheo, modificación de bootloader, instalación de módulos o persistencia requiere `IMPLEMENTACION_USUARIO_REQUERIDA`, consentimiento informado, doble confirmación cuando modifica sistema, validación X5/OjoRouter, EvidenceStore y AuditLog.

### Extracción y persistencia física

Las técnicas nominales de extracción y persistencia física quedan documentadas como capacidades futuras sujetas a autorización:

- **Andriller**;
- **backup ADB**;
- **volcado de particiones**;
- **extracción de bases de datos/apps/wallets**;
- **LiME/Frida para memoria de app**;
- **persistencia física por Magisk/recovery/ROM si aplica**.

La extracción debe diferenciar entre adquisición lógica, adquisición de archivos, extracción de app, memoria, particiones e imágenes forenses. La persistencia física debe tratarse como altamente invasiva y solo proponerse si existe justificación, consentimiento, plan de retirada y validación de política. Toda lógica operativa sensible queda `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Herramientas objetivo y VersionLock

Las herramientas objetivo del Vector 4 se documentan sin instalación, sin ejecución y sin fijar versiones obligatorias:

- **Android SDK Platform Tools**: `adb`, `fastboot`;
- **hashcat**;
- **Magisk**;
- **TWRP específico por modelo**;
- **Andriller**;
- **LiME**;
- **mtk-su**;
- **Dirty Pipe PoC**;
- **Android-PIN-Bruteforce**.

Toda versión final debe pasar por VersionLock y `tool_healthcheck` antes de cualquier implementación futura. VersionLock debe resolver versión real, fuente, compatibilidad por modelo/parche, estado de soporte, riesgos, dependencias, hashes de herramienta cuando aplique y decisión de bloqueo si no cumple política.

### Consentimiento informado

Antes de root, flasheo, exploit o modificación permanente, Mistral debe mostrar un modal de consentimiento informado. El modal debe explicar:

- qué hará;
- riesgos;
- requisitos;
- alternativas ordenadas por invasividad;
- evidencias esperadas;
- doble confirmación si modifica sistema.

AuditLog debe registrar opción elegida, riesgo aceptado, timestamp y operador. El consentimiento no sustituye Policy Engine, Scope ni Kill Switch: si la política bloquea, la acción no se ejecuta aunque el usuario confirme.

### Evidencias físicas y forenses

El Vector 4 debe registrar evidencias completas cuando exista implementación futura autorizada. Tipos de evidencia esperados:

- PIN/patrón si aplica;
- captura post-bypass;
- Android/parche;
- estado ADB/root;
- volcados;
- hashes;
- imágenes forenses;
- logs;
- capturas del panel;
- timeline.

Las evidencias deben vincularse a device_id, modelo, VID/PID, técnica, capa, operador, timestamp, scope, versión de herramienta, resultado, riesgo aceptado y AuditLog. Los hashes deben permitir verificar integridad de volcados, imágenes, artefactos y logs.

### Hermes Agent para soporte físico USB

Si falta soporte por modelo, parche, CVE, herramienta, recovery, pinout, parser, formato de evidencia o ruta de comunicación, Mistral activa Hermes Agent. Hermes Agent crea un módulo en laboratorio bajo `modules/laboratory/<technique_id>/`, lo prueba en sandbox, documenta riesgos y evidencias, declara dependencias generadas y propone promoción solo tras revisión humana, VersionLock, `tool_healthcheck`, validación X5/OjoRouter, Policy Engine, Kill Switch y AuditLog.

Hasta esa promoción, el soporte específico permanece como `IMPLEMENTACION_USUARIO_REQUERIDA` y no debe asumirse funcional.

## Vector 5 — Red Móvil / MITM

El Vector 5 documenta la arquitectura asistida para operaciones autorizadas de red móvil/local, MITM controlado, perfilado de dispositivos Android en WiFi, evidencias de tráfico y cierre seguro. Esta sección no implementa captura, spoofing, inyección, Evil Twin, SSL bypass, explotación, endpoints, workers, base de datos, dependencias ni comandos. La lógica sensible queda marcada como `IMPLEMENTACION_USUARIO_REQUERIDA` y subordinada a LaIA/Mistral, X5/OjoRouter, Policy Engine, Scope, Kill Switch, EvidenceStore, AuditLog y scoring.

### Panel Red Móvil

La subpestaña **Android > Red Móvil** debe mostrar dispositivos detectados en redes locales o laboratorios autorizados, con refresco documental cada 30s. El refresco no implica ejecución agresiva: el panel debe distinguir entre perfilado de solo lectura y acciones activas que requieren confirmación explícita.

Por cada dispositivo, el panel debe mostrar:

- IP, MAC, OUI/fabricante;
- nombre mDNS/NetBIOS;
- servicios expuestos;
- estado visual;
- botones: **MITM**, **Credenciales**, **DNS Spoof**, **Inyectar Payload**, **ADB WiFi**, **Evil Twin**, **SSL/Frida**, **Evidencias**, **Hermes Agent Lab**.

Los botones son entradas de planificación asistida. No ejecutan directo: LaIA/Mistral prepara un `network_action`, el usuario revisa, X5/OjoRouter valida scope, Policy Engine, Kill Switch, interfaz, gateway, técnica registrada, confirmación requerida y evidencias esperadas.

### Bloques internos de Android > Red Móvil

La sección **Android > Red Móvil** debe dividirse en bloques internos. En cada bloque el usuario ve tarjeta de objetivo, plan LaIA, estado, riesgo, progreso, evidencias y acciones permitidas; ninguna acción sensible se ejecuta sin `network_action`, confirmación cuando aplique, validación X5/OjoRouter, Policy Engine, Scope, Kill Switch, EvidenceStore y AuditLog:

- **Dispositivos detectados**: lista IP/MAC/OUI, nombre de red, servicios, confianza de fingerprint y acciones permitidas de perfilado o selección de objetivo.
- **Perfil del dispositivo**: tarjeta consolidada con sistema estimado, fabricante, servicios, historial, relación con USB Directo y evidencias de descubrimiento.
- **MITM activo**: preparación, estado, duración, interfaz, gateway, operador, riesgo, progreso, evidencia acumulada y cierre seguro.
- **Credenciales/cookies**: visualización normalizada y protegida de hallazgos autorizados, origen, sensibilidad, uso permitido y bloqueo de uso automático sin confirmación explícita.
- **DNS Spoof**: dominios autorizados, respuestas previstas, estado, riesgo, progreso, evidencias DNS/PCAP y restauración segura.
- **Inyección de payload**: artefacto autorizado, canal de entrega, hash, plan LaIA, riesgo crítico, progreso, evidencias y acciones de cancelación/cierre.
- **ADB WiFi**: estado ADB, autorización del dispositivo, interfaz, conexión, evidencias de sesión y desconexión segura.
- **Evil Twin**: SSID autorizado, perfil AP, clientes asociados, límites temporales, evidencias, riesgo crítico y apagado seguro.
- **SSL/Frida**: app autorizada, canal MITM, estado de Frida/objection, compatibilidad, evidencias HTTPS y rollback.
- **Evidencias**: PCAP, logs, cookies/credenciales JSON, capturas de panel, sesión ADB, tráfico descifrado, Evil Twin logs y `timeline`.
- **Historial/AuditLog**: eventos por objetivo, operador, técnica, interfaz, timestamp, confirmaciones, bloqueos y cierre seguro.
- **Hermes Agent Lab**: parsers, wrappers, soporte de herramienta, soporte por modelo/app, DPI/pinning/canal C2 faltante y `evidence_schema` en laboratorio.


### Detección y perfilado

Las herramientas nominales de detección y perfilado son:

- `arp-scan`;
- `tcpdump`;
- `tshark`;
- `nmap` con scripts `http-title`, `mdns-query`, `upnp-info` y `broadcast-dns-service-discovery`.

Las versiones finales se resolverán con VersionLock y `tool_healthcheck`. El perfilado debe registrar fuente, interfaz, timestamp, alcance autorizado, IP/MAC, OUI, nombres descubiertos, servicios expuestos y confianza del fingerprint.

### Estados visuales

Los estados visuales del Vector 5 son:

- `detected`;
- `profiled`;
- `mitm_prepared`;
- `mitm_active`;
- `capturing_traffic`;
- `credentials_found`;
- `dns_spoof_active`;
- `payload_injected`;
- `adb_wifi_connected`;
- `evil_twin_active`;
- `ssl_bypass_active`;
- `error`;
- `blocked_by_policy`;
- `closed`.

El estado `blocked_by_policy` debe prevalecer sobre cualquier acción preparada o en cola. Los estados activos deben mostrar duración, técnica, operador, interfaz, objetivo, evidencia acumulada y botón de cierre seguro cuando exista implementación futura.

### Técnicas registradas nominales

Las siguientes técnicas son registros nominales de catálogo. No son capacidades activas y no deben interpretarse como implementación disponible. Cada técnica conserva `implementation_status: IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.network.arp_spoof`

- **description**: preparación y ejecución controlada de MITM por ARP spoof en red autorizada.
- **tools**: Bettercap, mitmproxy/mitmdump y herramientas de captura compatibles con VersionLock.
- **required_inputs**: target_ip, mac, gateway, interface, scope, límites temporales y confirmación explícita.
- **expected_evidence**: PCAP, logs Bettercap/mitmproxy, timeline JSON, capturas del panel y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.network.dns_spoof`

- **description**: redirección DNS controlada para laboratorio autorizado y validación de defensas.
- **tools**: dnschef, Bettercap, dnsmasq y parsers de evidencia aprobados.
- **required_inputs**: target_ip, mac, gateway, interface, dominios autorizados, respuestas previstas, scope y confirmación explícita.
- **expected_evidence**: dominios redirigidos, logs DNS, PCAP, timeline JSON, capturas del panel y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.network.capture_credentials`

- **description**: captura y normalización de credenciales o cookies observadas en laboratorio autorizado.
- **tools**: net-creds, PCredz, mitmproxy/mitmdump y parsers EvidenceStore.
- **required_inputs**: target_ip, mac, interface, técnica de captura autorizada, filtros de evidencia, scope y confirmación cuando exista uso automático.
- **expected_evidence**: cookies/credenciales JSON, logs de captura, PCAP, timeline JSON, capturas del panel y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí para captura/uso automático de credenciales; perfilado pasivo no sensible puede quedar como solo lectura.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.network.inject_payload`

- **description**: inyección controlada de payload en flujo o entrega de artefacto dentro de laboratorio autorizado.
- **tools**: Bettercap, mitmproxy/mitmdump, módulos Android de payload aprobados y parsers de evidencia.
- **required_inputs**: target_ip, mac, gateway, interface, payload autorizado, canal de entrega, scope, evidencias esperadas y confirmación explícita.
- **expected_evidence**: registro de inyección, hash del artefacto, logs Bettercap/mitmproxy, PCAP, captura del panel, timeline JSON y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.network.adb_wifi`

- **description**: conexión ADB por WiFi cuando el dispositivo está autorizado y el estado ADB lo permite.
- **tools**: adb/platform-tools y validadores X5/OjoRouter.
- **required_inputs**: target_ip, device_id si existe, interface, estado ADB, autorización del dispositivo, scope y confirmación explícita.
- **expected_evidence**: sesión ADB, estado de conexión, logs, capturas del panel, timeline JSON y AuditLog.
- **risk_level**: alto.
- **confirmation_required**: sí.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.network.evil_twin`

- **description**: Evil Twin de laboratorio para validación de exposición WiFi y entrenamiento defensivo autorizado.
- **tools**: aircrack-ng/airbase-ng, hostapd, dnsmasq y parsers de logs.
- **required_inputs**: SSID autorizado, interface, perfil AP, límites temporales, objetivo, scope y confirmación explícita reforzada.
- **expected_evidence**: logs Evil Twin, asociaciones, PCAP si aplica, capturas del panel, timeline JSON y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí, reforzada.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.network.ssl_bypass`

- **description**: bypass SSL/pinning con Frida en laboratorio autorizado para análisis de aplicaciones propias o permitidas.
- **tools**: Frida + objection, mitmproxy/mitmdump y parsers EvidenceStore.
- **required_inputs**: target_ip, device_id/session_id, app autorizada, canal MITM, interface, scope y confirmación explícita reforzada.
- **expected_evidence**: tráfico HTTPS descifrado, logs Frida/objection, logs mitmproxy, PCAP si aplica, capturas del panel, timeline JSON y AuditLog.
- **risk_level**: crítico.
- **confirmation_required**: sí, reforzada.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Herramientas objetivo y VersionLock

Las herramientas objetivo del Vector 5 se documentan sin instalación, sin ejecución y sin fijar versiones obligatorias:

- **Bettercap**;
- **mitmproxy/mitmdump**;
- **dnschef**;
- **net-creds**;
- **PCredz**;
- **adb/platform-tools**;
- **Hydra**;
- **aircrack-ng/airbase-ng**;
- **hostapd**;
- **dnsmasq**;
- **Frida + objection**.

Las versiones finales deben resolverse por VersionLock y `tool_healthcheck` antes de cualquier implementación futura. La documentación de una herramienta no implica instalación, disponibilidad, soporte ni autorización operativa.

### Contrato JSON de acción de red

El contrato documental `network_action` debe contener estos campos:

- `type: network_action`;
- `target_ip`;
- `mac`;
- `gateway`;
- `interface`;
- `technique_id`;
- `params`;
- `expected_evidence`;
- `scope`;
- `operator`;
- `requires_confirmation`;
- `risk_level`;
- `timeout`;
- `stop_conditions`;
- `cleanup_required`.

Este contrato es especificación documental, no endpoint ni schema implementado. X5/OjoRouter debe rechazar cualquier acción sin scope válido, operador, interfaz permitida, técnica registrada, evidencia esperada, confirmación requerida cuando aplique, `risk_level`, `timeout`, `stop_conditions`, `cleanup_required` si corresponde y Kill Switch desactivado. MITM, DNS Spoof, payload injection, Evil Twin, ADB WiFi, SSL/Frida y uso automático de credenciales requieren confirmación explícita.

### Confirmación explícita

Requieren confirmación explícita antes de cualquier ejecución futura:

- MITM completo;
- DNS Spoof;
- inyección de payload;
- Evil Twin;
- ADB WiFi;
- SSL bypass con Frida;
- captura/uso automático de credenciales.

Escaneo y perfilado de solo lectura no requieren confirmación, pero siguen sujetos a scope, Policy Engine, Kill Switch, registro de actividad y límites del laboratorio autorizado.

### Evidencias

Las evidencias esperadas del Vector 5 son:

- PCAP;
- logs Bettercap/mitmproxy;
- dominios redirigidos;
- cookies/credenciales JSON;
- capturas del panel;
- sesión ADB;
- tráfico HTTPS descifrado;
- logs Evil Twin;
- timeline JSON.

Cada evidencia debe asociarse a target_ip, MAC, gateway, interface, technique_id, operador, timestamp, scope, estado visual, herramienta, versión VersionLock, riesgo aceptado y AuditLog.

### Cierre seguro

El cierre seguro del Vector 5 debe incluir:

- parar ARP spoof/restaurar ARP si aplica;
- detener mitmproxy/dnschef;
- `adb disconnect` documentado como acción futura del worker;
- detener AP falso;
- guardar evidencias;
- AuditLog;
- scoring X5;
- estado `closed`.

El cierre seguro debe estar disponible en acciones activas y por Kill Switch. Si una técnica queda en `error`, X5/OjoRouter debe priorizar restauración de estado de red, guardado de evidencias parciales y AuditLog.

### Hermes Agent para Red Móvil / MITM

Hermes Agent entra ante protocolo propietario, pinning no soportado, parser faltante, canal C2 bloqueado, DPI/firewall, técnica no existente por modelo/app o incompatibilidad de herramienta. LaIA/Mistral puede solicitar a Hermes Agent una capacidad de laboratorio, pero no promoción directa.

Hermes Agent debe generar un módulo en `modules/laboratory/<technique_id>/`, probarlo en sandbox, documentar riesgos, declarar dependencias generadas, producir esquema de evidencias y promocionar solo tras revisión humana, VersionLock, `tool_healthcheck`, validación X5/OjoRouter, Policy Engine, Kill Switch y AuditLog. Hasta esa promoción, toda capacidad específica permanece como `IMPLEMENTACION_USUARIO_REQUERIDA`.

## Vector 6 — Análisis de Apps

El Vector 6 define la sección **Android > Análisis de Apps**, dedicada al análisis estático, dinámico, forense, de tráfico, hooking, secretos, endpoints, componentes vulnerables e informe final de APKs o apps Android dentro de laboratorio autorizado. Esta sección no implementa comandos, endpoints, workers, base de datos, tests, dependencias, scripts Frida reales ni lógica operativa. Toda lógica sensible queda como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta implementación autorizada, sandbox, revisión, promoción y auditoría.

### Propósito del Vector 6

**Android > Análisis de Apps** no es una herramienta suelta ni una consola de comandos internos. Es una página asistida por LaIA/Mistral donde el usuario selecciona una app, describe qué quiere analizar y recibe un plan documental `app_analysis_action` revisable antes de cualquier implementación futura.

El flujo hereda la arquitectura del Módulo 12:

- **LaIA/Mistral**: cerebro local contextual que recomienda profundidad, rellena opciones, interpreta hallazgos y sugiere siguientes acciones.
- **X5/OjoRouter**: valida scope, Policy Engine, Kill Switch, herramientas, VersionLock, `tool_healthcheck` y confirmaciones.
- **Hermes Agent**: crea parsers, scripts Frida, módulos contra ofuscación, reglas de detección o análisis profundo cuando faltan capacidades, siempre en laboratorio.
- **DeepSeek**: arquitecto avanzado para revisar, corregir y diseñar módulos complejos sin ejecutar ni promocionar capacidades.
- **EvidenceStore/AuditLog/scoring**: registra evidencias, trazabilidad, aprobaciones, bloqueos, cierres y evaluación.

### Origen exacto de la app

Una app puede entrar al análisis desde estos orígenes documentales:

1. **App instalada en dispositivo**:
   - origen documental: lista de paquetes del dispositivo autorizado;
   - extracción futura controlada mediante mecanismo ADB autorizado.
2. **APK subida manualmente desde PC**:
   - arrastrar y soltar en panel;
   - registrar hash SHA256 y nombre de archivo.
3. **APK extraída desde dispositivo**:
   - cuando la app está instalada pero no existe APK local;
   - extracción documental desde ruta de paquete detectada.
4. **APK desde carpeta de evidencias previas**:
   - análisis anteriores, laboratorio Hermes, artefactos de payload, control remoto o Red Móvil.
5. **App detectada durante Control Remoto o Red Móvil**:
   - si el sistema detecta tráfico, actividad o paquete relevante, ofrece botón **Analizar app**.

Cada origen debe guardar metadatos mínimos: `app_origin`, `package_name`, `apk_path`, `source_evidence_id`, `device_id`, `hash_sha256`, `operator` y `timestamp`.

### Subpáginas de Android > Análisis de Apps

La sección debe tener una barra lateral interna con bloques especializados. Cada bloque muestra tarjeta de app, plan LaIA, estado, riesgo, progreso, evidencias y acciones permitidas bajo Policy Engine, Scope, Kill Switch, EvidenceStore y AuditLog:

- **Selección de aplicación**: origen, lista, búsqueda, subida, extracción o evidencia previa.
- **Configuración del análisis**: tipo, profundidad, herramientas, root/no root y modo dinámico/estático.
- **Progreso y resultados en vivo**: tareas, logs, estado y hallazgos.
- **Secretos y endpoints encontrados**: API keys, tokens, JWT, URLs, dominios, APIs, WebSockets y hosts cloud.
- **Componentes vulnerables (Drozer)**: activities, services, receivers y providers exportados.
- **Hooking en tiempo real (Frida)**: hooking dinámico documentado con confirmación explícita y sin scripts operativos en esta ronda.
- **Tráfico interceptado (HTTP Toolkit / mitmproxy)**: captura autorizada y resumen HTTP(S) cuando exista implementación futura aprobada.
- **Informe final (PDF descargable)**: resumen, evidencias, riesgos, recomendaciones y acciones sugeridas por LaIA.
- **Evidencias**: archivos extraídos, capturas, logs, PCAP y reportes.
- **Historial / AuditLog**: aprobaciones, bloqueos, confirmaciones, errores, cierres y operador.
- **Hermes Agent Lab si falta capacidad**: parsers, scripts Frida, reglas, módulos anti-ofuscación o análisis profundo.

### Estados visuales

La barra de estado superior debe mostrar icono, texto, tarea activa, técnica usada, operador, tiempo transcurrido y último evento. Los estados documentales del Vector 6 son:

- `seleccionando_app`;
- `configurando_analisis`;
- `descompilando`;
- `analizando_estatico`;
- `buscando_secretos`;
- `analizando_componentes`;
- `enganchando_frida`;
- `hookeando`;
- `interceptando_trafico`;
- `generando_informe`;
- `completado`;
- `error`;
- `bloqueado`.

El estado `bloqueado` prevalece sobre cualquier tarea preparada o en cola cuando Policy Engine, Scope, Kill Switch, VersionLock o confirmaciones impidan continuar.

### Qué ve el usuario por fase

#### Fase selección

El usuario ve:

- tabla de apps filtrable;
- origen de app;
- paquete;
- versión;
- hash si existe;
- botón **Analizar**.

#### Fase configuración

El usuario ve:

- opciones en lenguaje natural;
- profundidad: `rápido`, `estándar`, `profundo`, `full_forensic`;
- tipo: `estático`, `dinámico`, `tráfico`, `hooking`, `completo`;
- chat LaIA;
- botón **Preparar plan**.

#### Fase ejecución

El usuario ve:

- barra de progreso;
- tareas con iconos;
- tabla de hallazgos en vivo;
- logs;
- chat LaIA para pedir análisis extra;
- botón **Parar/Cerrar**.

#### Fase resultados

El usuario ve:

- PDF final descargable;
- evidencias por tipo;
- riesgos;
- acciones sugeridas;
- botón **Nuevo análisis**.

### Herramientas nominales y VersionLock

Las herramientas se documentan como capacidades objetivo. No se instalan, no se ejecutan y no fijan versiones definitivas en esta ronda:

- **MobSF 4.0.1 nominal**: análisis estático/dinámico automatizado; versión real a resolver por VersionLock.
- **jadx 1.5.2 nominal**: descompilador dex a Java; versión real a resolver por VersionLock.
- **apktool 2.9.3 nominal**: descompilación a smali; versión real a resolver por VersionLock.
- **APKLeaks 1.0 nominal**: secretos/endpoints; versión real a resolver por VersionLock.
- **QARK 2.0 nominal**: vulnerabilidades OWASP Mobile; versión real a resolver por VersionLock.
- **Drozer 3.1 nominal**: componentes exportados; versión real a resolver por VersionLock.
- **Frida 16.5 nominal**: hooking dinámico; versión real a resolver por VersionLock.
- **objection 1.13 nominal**: automatización sobre Frida; versión real a resolver por VersionLock.
- **HTTP Toolkit 1.18 nominal**: interceptación de tráfico; versión real a resolver por VersionLock.
- **truffleHog 3.69 nominal**: secretos en código; versión real a resolver por VersionLock.
- **mitmproxy 10.2 nominal**: alternativa de tráfico; versión real a resolver por VersionLock.
- **apksigner/jarsigner/default-jdk**: firma/verificación; versiones reales a resolver por VersionLock.

Las versiones citadas por el usuario son referencia documental. La implementación futura debe resolver versión real con VersionLock y `tool_healthcheck`, registrar fuente, versión, hash si aplica, compatibilidad, motivo de uso o bloqueo y entorno.

### Técnicas registradas oficiales

Las siguientes técnicas quedan documentadas como registros oficiales esperados de catálogo. No son capacidades activas y no deben interpretarse como implementación disponible.

#### `android.analysis.decompile`

- **description**: descompilación documental de APK para obtener estructura, manifiesto, recursos, smali y fuentes Java aproximadas.
- **tools**: apktool + jadx bajo VersionLock.
- **required_inputs**: `apk_path`, `package_name`, `app_origin`, scope, operador y metadatos de origen.
- **expected_evidence**: `decompiled_code`, `manifest`, `smali`, `java_sources`.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.analysis.secrets`

- **description**: búsqueda documental de API keys, tokens, URLs, endpoints, JWT y credenciales.
- **tools**: APKLeaks + truffleHog bajo VersionLock.
- **required_inputs**: `apk_path` o `decompiled_code`, profundidad, filtros, scope y operador.
- **expected_evidence**: `secrets_list` JSON y riesgo por secreto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.analysis.endpoints`

- **description**: extracción de URLs, dominios, APIs, WebSockets y hosts cloud.
- **tools**: parsers de análisis estático/dinámico aprobados, APKLeaks, truffleHog o capacidad Hermes si falta parser.
- **required_inputs**: `apk_path`, `decompiled_code`, `traffic_summary` si existe, scope y operador.
- **expected_evidence**: `endpoints_json`.
- **handoff**: puede enviar hallazgos a Módulo 1 OSINT o Módulo 4 Web si el usuario confirma y X5 valida.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.analysis.drozer_components`

- **description**: análisis documental de activities, services, receivers y providers exportados.
- **tools**: Drozer bajo VersionLock y entorno autorizado.
- **required_inputs**: `package_name`, dispositivo autorizado si requiere dinámica, scope, operador y confirmación cuando haya ejecución dinámica.
- **expected_evidence**: `drozer_report`, componentes y posibles PoC documentales no ejecutables.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.analysis.frida_runtime`

- **description**: hooking genérico con Frida en app autorizada.
- **tools**: Frida bajo VersionLock.
- **required_inputs**: `package_name`, dispositivo/sesión autorizada, modo, límites, scope, operador y confirmación explícita.
- **expected_evidence**: `frida_log`, scripts usados, resultados y errores.
- **confirmation_required**: sí, explícita.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.analysis.ssl_pinning_bypass`

- **description**: bypass documental de pinning con objection/Frida si scope lo permite.
- **tools**: objection + Frida bajo VersionLock.
- **required_inputs**: `package_name`, dispositivo/sesión autorizada, modo, límites, scope, operador y confirmación explícita.
- **expected_evidence**: `frida_log`, `traffic_summary`, errores y resultado de validación.
- **fallback**: si falla, LaIA deriva a Hermes Agent para script personalizado en laboratorio.
- **confirmation_required**: sí, explícita.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.analysis.traffic_capture`

- **description**: captura documental de tráfico con HTTP Toolkit o mitmproxy en laboratorio autorizado.
- **tools**: HTTP Toolkit o mitmproxy bajo VersionLock.
- **required_inputs**: `package_name`, dispositivo/sesión autorizada, duración, filtros, scope, operador y confirmación explícita.
- **expected_evidence**: `pcap`, `traffic_summary`, cookies/tokens si aparecen y AuditLog.
- **confirmation_required**: sí, explícita.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.analysis.mobsf_report`

- **description**: generación documental de informe automatizado MobSF.
- **tools**: MobSF bajo VersionLock.
- **required_inputs**: `apk_path`, `package_name`, `app_origin`, scope, operador y opciones de reporte.
- **expected_evidence**: `mobsf_report` PDF/JSON.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.analysis.final_report`

- **description**: compilación de PDF final con hallazgos, evidencias y recomendaciones LaIA.
- **tools**: generador de reportes futuro validado por X5/OjoRouter y EvidenceStore.
- **required_inputs**: evidencias seleccionadas, alcance, operador, app, scoring y confirmación si puede sobrescribir.
- **expected_evidence**: `final_report`.
- **confirmation_required**: sí cuando pueda sobrescribir un informe existente.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Contrato JSON `app_analysis_action`

El contrato documental `app_analysis_action` debe representar la intención del análisis, la app origen, técnicas, evidencias esperadas, scope, operador y confirmación. Ejemplo documental no ejecutable:

```json
{
  "type": "app_analysis_action",
  "app_origin": "device",
  "package_name": "com.banca.app",
  "apk_path": null,
  "analysis_type": "full_forensic",
  "techniques": [
    {"technique_id": "android.analysis.decompile", "params": {}},
    {"technique_id": "android.analysis.secrets", "params": {"depth": "deep"}},
    {"technique_id": "android.analysis.drozer_components", "params": {"package": "com.banca.app"}},
    {"technique_id": "android.analysis.frida_runtime", "params": {"mode": "runtime_hooks"}},
    {"technique_id": "android.analysis.ssl_pinning_bypass", "params": {"mode": "objection_frida"}},
    {"technique_id": "android.analysis.traffic_capture", "params": {"duration_seconds": 60}}
  ],
  "expected_evidence": [
    "decompiled_code",
    "secrets_list",
    "drozer_report",
    "frida_log",
    "pcap",
    "mobsf_report",
    "final_report"
  ],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Este JSON es contrato documental, no ejecución real, endpoint, schema implementado ni garantía de disponibilidad. X5/OjoRouter debe rechazar cualquier `app_analysis_action` sin scope válido, operador, técnica registrada, evidencia esperada, VersionLock compatible, Kill Switch desactivado y confirmación cuando aplique.

### Evidencias exactas

Las evidencias del Vector 6 deben normalizarse en EvidenceStore con `timestamp`, app, técnica, operador, scope, `source_evidence_id` y hash:

- **`decompiled_code`**: carpeta Java/smali/manifest/resources.
- **`secrets_list`**: JSON con API keys, tokens, JWT, URLs, endpoints, clasificación y riesgo.
- **`endpoints_json`**: dominios, rutas, métodos, cloud, WebSocket y APIs.
- **`drozer_report`**: componentes vulnerables y hallazgos.
- **`frida_log`**: sesión Frida, scripts, resultados y errores.
- **`pcap`**: tráfico capturado.
- **`traffic_summary`**: resumen HTTP(S), cookies/tokens si aparecen.
- **`mobsf_report`**: reporte MobSF.
- **`final_report`**: PDF compilado por LaIA.
- **`screenshots`**: capturas del panel y hallazgos.
- **`audit_events`**: aprobaciones, bloqueos, confirmaciones, cierres y errores.

### Confirmaciones explícitas

Requieren confirmación explícita antes de cualquier ejecución futura:

- hooking en tiempo real con Frida;
- SSL pinning bypass;
- interceptación de tráfico;
- cualquier análisis que requiera root;
- extracción dinámica sensible;
- generación de informe final si puede sobrescribir;
- envío de hallazgos a otros módulos si implica nueva ejecución.

No requieren confirmación fuerte, aunque siempre quedan sujetos a scope, Policy Engine, Kill Switch, VersionLock, AuditLog y límites del laboratorio autorizado:

- análisis estático;
- búsqueda de secretos;
- extracción de endpoints;
- lectura de componentes ya descompilados.

Policy Engine y Kill Switch siempre prevalecen sobre cualquier opción seleccionada, plan LaIA o acción en cola.

### LaIA durante todo el análisis

LaIA/Mistral permanece activa durante todo el ciclo de análisis:

- **En selección**: recomienda análisis según categoría de app: banca, mensajería, cripto, IoT o corporativa.
- **En configuración**: rellena profundidad, herramientas y técnicas.
- **En ejecución**: interpreta hallazgos en tiempo real.
- **En secretos**: clasifica riesgo bajo, medio, alto o crítico.
- **En endpoints**: sugiere enviar a OSINT o Web.
- **En componentes**: sugiere plan Drozer/Frida.
- **En pinning**: sugiere objection/Frida o Hermes.
- **En tráfico**: explica cookies, tokens y endpoints.
- **En cierre**: genera PDF final y recomendaciones.

El usuario puede pedir en lenguaje natural: “analiza más profundo”, “explica este hallazgo”, “envía endpoints a Web”, “pide a Hermes un parser” o “genera informe”. LaIA convierte esas intenciones en planes revisables, nunca en ejecución directa.

### Lógica según hallazgos

Las reglas documentales de reacción ante hallazgos son:

- **Secreto encontrado**:
  - validar formato;
  - clasificar tipo;
  - guardar evidencia;
  - si es crítico, notificación en panel;
  - posible acción a OSINT/Web si el usuario confirma.
- **Endpoint encontrado**:
  - clasificar dominio;
  - guardar `endpoints_json`;
  - ofrecer **Enviar a Módulo 1 OSINT** o **Enviar a Módulo 4 Web**.
- **Componente vulnerable**:
  - sugerir plan Drozer;
  - mostrar riesgo;
  - pedir confirmación si hay ejecución dinámica.
- **SSL pinning detectado**:
  - ofrecer objection/Frida;
  - si falla, pedir script Hermes Agent.
- **Tráfico propietario**:
  - pedir parser Hermes Agent.
- **Ofuscación fuerte**:
  - derivar muestra a Hermes Agent Lab.

### Hermes Agent Lab para Análisis de Apps

Dentro de **Android > Análisis de Apps** debe existir un bloque fijo **Hermes Agent Lab**. Permite pedir:

- crear parser para protocolo propietario;
- generar script Frida específico;
- crear módulo contra ofuscador;
- adaptar PoC de GitHub;
- crear regla de detección de secretos;
- crear módulo de análisis profundo.

Hermes Agent trabaja en:

```text
modules/laboratory/<technique_id>/
```

Debe generar:

- `technique.json`;
- `worker.py`;
- parser;
- `evidence_schema.json`;
- `requirements.generated.txt`;
- `README.md`.

La promoción solo puede ocurrir tras sandbox, revisión, aprobación humana, VersionLock, Policy Engine, Kill Switch, EvidenceStore y AuditLog. Hermes Agent no promociona por sí mismo, no instala herramientas en producción y no convierte scripts de laboratorio en capacidades activas sin validación X5/OjoRouter.

### Cierre seguro

Al cerrar un análisis, el flujo documental debe:

1. detener Frida si está activo;
2. detener HTTP Toolkit/mitmproxy si está activo;
3. guardar evidencias pendientes;
4. generar PDF si el usuario confirma;
5. registrar AuditLog con timestamp y operador;
6. actualizar scoring X5 solo si hay evidencia válida;
7. dejar estado `completado` o `cerrado`.

El cierre seguro debe estar disponible desde la fase de ejecución, desde resultados y desde Kill Switch cuando aplique. Si una tarea queda en `error`, X5/OjoRouter debe priorizar guardado de evidencias parciales, limpieza de sesiones dinámicas y AuditLog.

### Informe PDF final

La estructura obligatoria del PDF final es:

- Resumen ejecutivo.
- App analizada: nombre, paquete, versión y hashes SHA256.
- Permisos peligrosos.
- Secretos encontrados: tipo, valor parcial y riesgo.
- Endpoints y URLs: dominio, ruta, riesgo y módulo sugerido.
- Componentes vulnerables: activities, services, providers, receivers y PoC documental si aplica.
- Tráfico capturado: peticiones, cookies, tokens y PCAP.
- Hooks Frida: scripts, resultados y errores.
- Evidencias adjuntas: capturas, archivos y logs.
- Riesgo 0-100 con justificación.
- Recomendaciones.
- Acciones sugeridas por LaIA: enviar a OSINT, Web, Hermes, reporte o nueva prueba.

El PDF final debe derivar únicamente de evidencias registradas y trazables. No debe inventar hallazgos, no debe ocultar bloqueos y debe indicar qué capacidades quedaron como `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Complemento Vector 6B — Hallazgos normalizados, handoff, scoring y asistencia LaIA/Hermes Agent

Este complemento extiende **Android > Análisis de Apps** con la capa de resultados normalizados, acciones rápidas por hallazgo, handoff entre módulos, scoring X5, contexto estructurado para LaIA/Mistral, tareas Hermes Agent y criterios de aceptación. No implementa código, endpoints, workers, base de datos, tests, requirements ni scripts. Toda lógica sensible permanece como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta implementación autorizada, sandbox, revisión, promoción y auditoría.

#### Modelo normalizado de hallazgo `android_app_finding`

Todo resultado del análisis debe transformarse en un hallazgo normalizado `android_app_finding` antes de mostrarse en panel, puntuar con X5, incluirse en PDF, usarse como entrada de LaIA o enviarse a otro módulo. Un log crudo, salida de herramienta o captura aislada no debe convertirse en acción ni scoring hasta estar vinculado a EvidenceStore y normalizado.

Campos obligatorios del hallazgo:

- `finding_id`;
- `app_id`;
- `package_name`;
- `app_version`;
- `apk_sha256`;
- `finding_type`;
- `title`;
- `description`;
- `severity`: `info`, `low`, `medium`, `high`, `critical`;
- `confidence`: valor entre `0.0` y `1.0`;
- `source_technique`;
- `source_tool`;
- `evidence_ids`;
- `affected_component`;
- `file_path`;
- `line_or_offset`;
- `masvs_category`;
- `recommended_action`;
- `handoff_targets`;
- `created_at`;
- `operator`.

Tipos documentales permitidos para `finding_type`:

- `secret`;
- `endpoint`;
- `dangerous_permission`;
- `exported_component`;
- `insecure_storage`;
- `weak_crypto`;
- `ssl_pinning`;
- `traffic_leak`;
- `webview_risk`;
- `hardcoded_credential`;
- `wallet_artifact`;
- `frida_observation`;
- `proprietary_protocol`;
- `obfuscation_blocker`;
- `root_required`;
- `tool_error`.

#### Mapeo a MASVS/OWASP Mobile

LaIA/Mistral debe clasificar hallazgos usando categorías de referencia OWASP MASVS/MASWE cuando sea posible. No se requiere implementar una base completa en esta ronda, pero el panel, EvidenceStore y el PDF final deben reservar y preservar el campo `masvs_category`.

Categorías documentales de referencia:

- autenticación/sesiones;
- red y TLS;
- almacenamiento local;
- criptografía;
- plataforma/interacción Android;
- WebView;
- código/ofuscación;
- privacidad/datos sensibles.

Si LaIA/Mistral no puede mapear con seguridad, debe marcar `masvs_category: unknown`, explicar por qué en el hallazgo y evitar inflar severidad o scoring sin evidencia suficiente.

#### Acciones rápidas por hallazgo

Cada fila de hallazgo debe mostrar botones de acción contextual. Los botones generan planes revisables o contratos documentales; no ejecutan directo y siguen sujetos a X5/OjoRouter, Policy Engine, Scope, Kill Switch, VersionLock, EvidenceStore y confirmación cuando aplique.

Para `secret`:

- validar formato;
- copiar a EvidenceStore;
- enviar a Módulo 5 Credenciales;
- pedir a LaIA clasificación de riesgo;
- pedir a Hermes Agent una regla de detección personalizada.

Para `endpoint`:

- enviar a Módulo 1 OSINT;
- enviar a Módulo 4 Web;
- crear target API;
- generar plan de fingerprinting.

Para `exported_component`:

- preparar plan Drozer;
- preparar PoC documental no ejecutable;
- pedir confirmación si hay ejecución dinámica.

Para `ssl_pinning`:

- preparar plan objection/Frida;
- pedir script personalizado a Hermes Agent si falla.

Para `proprietary_protocol`:

- pedir parser Hermes Agent;
- crear módulo de laboratorio.

Para `obfuscation_blocker`:

- pedir análisis Hermes Agent contra ofuscador;
- crear unpacker/parser si procede.

#### Handoff entre módulos

Android no trabaja aislado. Los hallazgos normalizados pueden crear handoff hacia otros módulos solo después de registrar evidencia, preservar `finding_id`, mostrar plan LaIA y obtener confirmación cuando el handoff implique nueva ejecución o tratamiento sensible.

Destinos documentales:

- **Módulo 1 OSINT**: dominios, IPs, certificados y fabricantes.
- **Módulo 2 Vulnerabilidades**: CVEs, librerías y componentes vulnerables.
- **Módulo 4 Web**: endpoints, APIs, paneles backend y rutas.
- **Módulo 5 Credenciales**: tokens, claves, cookies y JWT.
- **Módulo 12 Orquestación**: nuevo plan y fallback inteligente.
- **Hermes Agent Lab**: parser, script Frida, módulo contra ofuscación o regla.

Contrato documental `analysis_handoff` no ejecutable:

```json
{
  "type": "analysis_handoff",
  "source_module": "android",
  "source_vector": "analysis_apps",
  "finding_id": "finding-uuid",
  "target_module": "web",
  "handoff_reason": "endpoint_detected",
  "payload": {
    "endpoint": "https://api.example.local/v1/login",
    "app_package": "com.example.app",
    "apk_sha256": "sha256..."
  },
  "expected_next_action": "fingerprint_endpoint",
  "requires_confirmation": true,
  "operator": "admin"
}
```

Este contrato es especificación documental, no endpoint ni schema implementado. X5/OjoRouter debe rechazar handoffs sin evidencia válida, scope, operador, destino permitido, razón trazable, Kill Switch desactivado y confirmación cuando aplique.

#### Scoring del análisis de apps

X5 puede actualizar scoring solo con evidencia válida en EvidenceStore. No puntúan hallazgos sin EvidenceStore ni salidas de herramienta no normalizadas. Las técnicas con `IMPLEMENTACION_USUARIO_REQUERIDA` no puntúan hasta promoción aprobada.

Reglas documentales de scoring:

- herramienta ejecutada sin evidencia útil = no sube scoring;
- secreto validado + evidencia = sube scoring;
- falso positivo confirmado = baja scoring de la técnica;
- reporte PDF generado sin hallazgos = no sube por éxito ofensivo, pero puede registrar ejecución completa;
- técnicas con `IMPLEMENTACION_USUARIO_REQUERIDA` no puntúan hasta promoción.

Campos recomendados para evento de scoring:

- `technique_id`;
- `app_category`;
- `finding_type`;
- `evidence_valid`;
- `false_positive`;
- `score_before`;
- `score_after`;
- `score_delta`;
- `operator`.

#### Contexto estructurado que recibe LaIA

LaIA/Mistral debe recibir contexto estructurado, no texto suelto ni logs sin normalizar. El contexto mínimo para **Android > Análisis de Apps** incluye:

- app seleccionada;
- origen de app;
- `package_name`;
- hashes;
- categoría estimada: banca, mensajería, cripto, IoT, corporativa o genérica;
- herramientas disponibles;
- técnicas registradas;
- permisos detectados;
- hallazgos previos;
- scope;
- modo de ejecución;
- restricciones Policy/Kill Switch;
- evidencias disponibles.

Con este contexto, LaIA debe poder responder:

- qué análisis conviene;
- qué herramienta usar;
- qué hallazgo importa;
- qué falso positivo descartar;
- qué módulo debe recibir handoff;
- qué pedir a Hermes Agent.

LaIA permanece como cerebro local continuo durante selección, configuración, ejecución, revisión de hallazgos, handoff, scoring, cierre seguro y PDF final. Nunca sustituye validación X5/OjoRouter ni confirmación humana cuando aplique.

#### Tareas Hermes Agent desde Vector 6

La página **Android > Análisis de Apps > Hermes Agent Lab** puede enviar tareas estructuradas a Hermes Agent cuando falte capacidad, parser, script, wrapper, regla o soporte específico. Estas tareas son de laboratorio y no promocionan capacidades por sí mismas.

Tipos documentales de tarea:

- `create_protocol_parser`;
- `create_frida_script`;
- `create_obfuscation_unpacker`;
- `create_secret_detection_rule`;
- `adapt_github_poc`;
- `create_dynamic_analysis_module`;
- `repair_analysis_worker`;
- `generate_evidence_schema`.

Cada tarea debe incluir:

- `task_id`;
- `finding_id`;
- `app_context`;
- `technical_goal`;
- `input_evidence_ids`;
- `expected_files`;
- `expected_evidence`;
- `approval_required`;
- `target_path: modules/laboratory/<technique_id>/`.

Hermes Agent debe devolver:

- archivos creados;
- diff;
- logs;
- evidencias;
- dependencias;
- estado;
- recomendación de prueba sandbox.

Toda salida de Hermes Agent queda en `modules/laboratory/<technique_id>/` y requiere sandbox, revisión, aprobación humana, VersionLock, Policy Engine, Kill Switch, EvidenceStore, AuditLog y validación X5/OjoRouter antes de cualquier promoción.

#### Profundidades de análisis

Los perfiles de profundidad documentales son:

**`quick`**:

- decompile ligero;
- permisos;
- endpoints básicos;
- secretos básicos.

**`standard`**:

- decompile completo;
- secrets;
- endpoints;
- componentes exportados;
- MobSF si está disponible.

**`deep`**:

- MobSF;
- APKLeaks/truffleHog;
- QARK;
- Drozer;
- Frida runtime opcional;
- tráfico opcional.

**`full_forensic`**:

- todo lo anterior;
- tráfico;
- hooks Frida;
- PCAP;
- informe final;
- handoff a otros módulos;
- Hermes Agent si hay bloqueos.

Las profundidades no fuerzan ejecución. LaIA propone, el usuario revisa, X5/OjoRouter valida y cualquier paso dinámico, root, tráfico, Frida, handoff con nueva ejecución o sobrescritura de PDF requiere confirmación explícita.

#### Panel de resultados

El panel de resultados debe mostrar una tabla de hallazgos normalizados con columnas:

- severidad;
- confianza;
- tipo;
- título;
- técnica;
- herramienta;
- evidencia;
- MASVS;
- acción sugerida;
- botones de handoff;
- estado: `nuevo`, `revisado`, `falso positivo`, `enviado`, `cerrado`.

Cada cambio de estado debe quedar en AuditLog con operador, timestamp, `finding_id`, acción realizada, evidencia afectada y resultado. Marcar un hallazgo como falso positivo debe ajustar scoring de técnica solo si existe evidencia suficiente.

#### Criterios de aceptación del Vector 6

Vector 6 queda documentalmente completo si `docs/techniques/13_ANDROID.md` contiene:

- orígenes de app;
- subpáginas;
- estados;
- herramientas y VersionLock;
- técnicas oficiales;
- contrato `app_analysis_action`;
- evidencias;
- confirmaciones;
- cierre seguro;
- LaIA presente durante todo el flujo;
- Hermes Agent Lab fijo;
- modelo `android_app_finding`;
- handoff entre módulos;
- scoring;
- PDF final;
- criterios de aceptación.

Estos criterios no afirman implementación. Solo cierran la especificación documental del Vector 6 y mantienen toda lógica sensible como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta implementación autorizada, sandbox, revisión, promoción y auditoría.


## Vector 7 — IMSI Catcher / BTS / RF Móvil

El Vector 7 define la pestaña **Android > IMSI Catcher** como estación de laboratorio RF para identificación, análisis y control de dispositivos móviles, IoT, vehículos y terminales industriales dentro de un entorno controlado. Toda emisión RF, BTS, downgrade, intercepción, relay, inyección, comando AT o DoS queda documentada como capacidad de laboratorio con estado `HARDWARE_REQUIRED`, `RF_TRANSMIT` e `IMPLEMENTACION_USUARIO_REQUERIDA` hasta implementación privada autorizada, sandbox, aprobación y auditoría.

Esta sección no implementa código, endpoints, workers, base de datos, tests, requirements, scripts RF, comandos operativos ni lógica BTS real. No afirma soporte funcional: especifica producto, panel, hardware, estados, VersionLock, LaIA/Mistral, X5/OjoRouter, Hermes Agent, DeepSeek, EvidenceStore, AuditLog, Policy Engine y Kill Switch para una futura capacidad autorizada.

### Propósito del Vector 7

El Vector 7 convierte Ojo de Dios en una consola RF/BTS asistida por IA para laboratorio. No es una pantalla de comandos: el usuario trabaja desde panel, LaIA/Mistral prepara planes, X5/OjoRouter valida, Policy Engine y Kill Switch gobiernan, EvidenceStore/AuditLog registran y Hermes Agent crea soporte cuando falta capacidad.

Capacidades nominales documentales:

- Escaneo de bandas.
- Detección de tecnología GSM/LTE/NR.
- Estación BTS/eNodeB/gNodeB de laboratorio.
- Identificación por IMSI/IMEI/TAC.
- Clasificación de dispositivo por TAC y comportamiento.
- Acciones sobre SMS, voz, datos, portal/payload, AT y disponibilidad.
- Generación de evidencias RF, PCAP y logs.
- Evolución del arsenal mediante Hermes Agent.

Todas estas capacidades permanecen como especificación documental de producto hasta que exista implementación privada autorizada, promoción, evidencia y auditoría.

### Relación con Módulo 12, Módulo 10 y módulos conectados

El Vector 7 es transversal:

- **Módulo 12 Orquestación**: LaIA/Mistral dirige, X5/OjoRouter valida/ejecuta, Hermes Agent construye, DeepSeek revisa/diseña y Policy/Kill Switch/Evidence/AuditLog mandan.
- **Módulo 10 Wireless/RF/HackRF**: comparte hardware, waterfall, SDR, HackRF, evidencia IQ/PCAP y estado de emisión.
- **Módulo 13 Android**: muestra IMSI Catcher como vector Android/Red Móvil para dispositivos móviles, IoT, vehículos y terminales industriales.
- **Módulo 5 Credenciales**: recibe tokens, SMS, credenciales o datos sensibles solo mediante handoff auditado, redacción por defecto y confirmación cuando aplique.
- **Módulo 6 MITM/Red**: recibe tráfico, PCAP o relay si procede y si Policy Engine lo permite.
- **Hermes Agent Lab**: crea parsers, decoders, soporte de bandas, módulos AT o normalizadores de evidencia.

### Hardware requerido

Hardware mínimo documental:

- **HackRF One**: obligatorio para la pestaña. Si no está presente, el panel muestra `hardware_missing` y desactiva acciones de emisión.
- Antena adecuada para bandas del laboratorio.
- Entorno de laboratorio o jaula de Faraday cuando exista emisión.
- Host Ojo de Dios con Kali WSL2 o entorno Linux compatible.
- Identificador de hardware `hardware_id` para trazabilidad.
- Botón/verificación de salud de hardware: conectado, firmware, versión de host tools, número de serie y permisos USB.

El panel no debe ocultar la pestaña si falta hardware. Debe mostrarla en modo lectura con explicación, checklist y estado `HARDWARE_REQUIRED`.

### Herramientas nominales y VersionLock

Las herramientas se documentan como referencias nominales. No se instalan, no se ejecutan y no fijan versiones definitivas:

- **YateBTS nominal**: BTS 2G/GSM. La versión `8.0` queda como referencia nominal citada por el usuario; la versión pública open-source real debe resolverse con VersionLock porque las fuentes públicas pueden indicar otra versión.
- **srsRAN nominal**: estación 4G/5G según rama disponible. VersionLock debe resolver si corresponde a stack LTE legacy o srsRAN Project moderno.
- **gr-gsm nominal**: sniffing/análisis GSM.
- **osmocom-bb nominal**: capa GSM/baseband.
- **HackRF tools nominal**: `hackrf_info`, `hackrf_sweep` y utilidades SDR como referencias de salud y escaneo.
- **Wireshark/tshark nominal**: análisis de PCAP.
- **tcpdump nominal**: captura de paquetes.
- **minicom nominal**: consola serie/AT cuando exista interfaz compatible.
- **Python 3.12 + pyserial/scapy/requests nominales**: wrappers futuros.

Antes de cualquier implementación, `version_lock.py` o `tool_healthcheck` debe registrar:

- herramienta;
- versión detectada;
- fuente;
- ruta binaria;
- hash si aplica;
- compatibilidad Kali WSL2/Windows;
- estado: `available`, `missing`, `incompatible`, `blocked`;
- motivo de uso o bloqueo.

No se fijan versiones antiguas como definitivas. Las versiones citadas por el usuario permanecen como nominales/documentales hasta verificación real.

### Pestaña Android > IMSI Catcher

La pestaña **Android > IMSI Catcher** tiene barra lateral interna con estas secciones exactas y en este orden:

1. Configuración RF
2. Escaneo de Bandas
3. BTS Activa
4. Detalle del Dispositivo
5. SMS / Voz / Datos
6. Payload / Portal Cautivo
7. Consola AT
8. Evidencias
9. Historial / AuditLog
10. Hermes Agent Lab

### Configuración RF

La sección **Configuración RF** muestra:

- estado HackRF;
- serial/hardware_id;
- firmware/tools según VersionLock;
- banda seleccionada;
- tecnología: GSM/LTE/NR;
- MCC;
- MNC;
- LAC/TAC;
- Cell ID;
- ARFCN/EARFCN/NR_ARFCN;
- frecuencia;
- potencia TX;
- ganancia;
- antena;
- zona de laboratorio;
- indicador Faraday;
- estado Policy/Kill Switch;
- botón **Preparar plan**;
- botón **Iniciar BTS** solo como acción planificada.

LaIA/Mistral puede proponer valores desde el contexto de laboratorio, pero el usuario revisa y X5/OjoRouter valida. Ningún botón ejecuta directamente una emisión o BTS.

### Escaneo de Bandas

La sección **Escaneo de Bandas** muestra:

- botón **Escanear bandas**;
- gráfico waterfall;
- tabla de frecuencias detectadas;
- potencia estimada;
- tecnología detectada;
- banda candidata;
- recomendación LaIA;
- botón **Auto** para selección asistida;
- opción manual en modo experto;
- evidencia de escaneo en EvidenceStore.

Bandas nominales documentales:

- GSM850;
- GSM900;
- DCS1800;
- PCS1900;
- LTE B1/B3/B7/B20;
- NR si se añade soporte futuro.

No se incluyen parámetros listos para redes reales. VersionLock y RF Policy deciden disponibilidad futura.

### BTS Activa

La sección **BTS Activa** se habilita cuando el sistema pasa a estado `bts_active`. Debe mostrar:

- estado global;
- tecnología activa;
- banda;
- tiempo activo;
- contador de dispositivos;
- tabla de dispositivos conectados;
- tráfico/relay si existe;
- botones de parada;
- Kill Switch visible;
- indicador de emisión RF;
- últimas evidencias generadas.

La tabla de dispositivos debe incluir:

- `device_id`;
- IMSI enmascarado;
- IMEI enmascarado;
- TAC;
- tipo estimado;
- fabricante/modelo estimado;
- potencia señal;
- última actividad;
- estado del dispositivo;
- acciones disponibles según permisos.

### Detalle del Dispositivo

Al seleccionar un dispositivo, el panel abre una barra lateral o página de detalle con:

- IMSI/IMEI enmascarados por defecto;
- TAC;
- fabricante/modelo estimado;
- tipo: móvil, coche, IoT, datáfono, terminal industrial, desconocido;
- servicios detectados: SMS, Voz, Datos, MMS, AT si aplica;
- historial de acciones;
- evidencias relacionadas;
- chat contextual LaIA;
- botones de acción planificada;
- botón **Mostrar completo** con confirmación y AuditLog.

### SMS / Voz / Datos

La sección **SMS / Voz / Datos** existe para monitorización y evidencias:

- SMS capturados/interceptados como registros estructurados;
- llamadas/grabaciones como evidencias;
- tráfico de datos/relay como PCAP/logs;
- estado de cada flujo;
- enmascarado por defecto;
- botón de exportación enmascarada;
- exportación completa solo con confirmación reforzada.

### Payload / Portal Cautivo

La sección **Payload / Portal Cautivo** documenta configuración de laboratorio para:

- inyección HTTP;
- SMS especial/binario/clase 0;
- portal cautivo;
- perfil/certificado/APN cuando aplique;
- APK/laboratorio como artefacto;
- `expected_evidence`;
- confirmación explícita;
- estado `IMPLEMENTACION_USUARIO_REQUERIDA`.

No se implementan payloads ni scripts. Solo se documentan panel, contratos y evidencias.

### Consola AT

La sección **Consola AT** es modo experto/controlado para dispositivos que lo permitan:

- disponible solo si el dispositivo se clasifica como AT-capable;
- muestra puerto/canal lógico;
- LaIA puede explicar comandos o preparar plan, pero no escribe automáticamente;
- usuario confirma acciones;
- todo comando/respuesta queda en `at_command_log`;
- Hermes Agent puede crear módulo AT por modelo si falta soporte.

### Evidencias

El repositorio de evidencias del Vector 7 incluye:

- `pcap_imsi_catcher`;
- `imsi_list_json`;
- `device_fingerprint_json`;
- `sms_intercepted_json`;
- `call_recording_wav`;
- `payload_injected_json`;
- `at_command_log`;
- `rf_scan_report`;
- `radio_profile_json`;
- `timeline_json`;
- `screenshots`;
- `audit_log`.

Cada evidencia debe tener:

- `session_id`;
- `device_id` si aplica;
- `technique_id`;
- `radio_profile_id`;
- `timestamp`;
- `operator`;
- `redaction_policy`;
- `scope`;
- VersionLock tools;
- `hash_sha256`.

### Historial / AuditLog

AuditLog registra:

- hardware detectado;
- selección de banda;
- confirmación de emisión;
- inicio/parada BTS;
- dispositivo conectado;
- acción sobre dispositivo;
- revelado de IMSI/IMEI completo;
- exportación de datos sensibles;
- Kill Switch;
- errores;
- cierre seguro.

### Hermes Agent Lab

El bloque **Hermes Agent Lab** permite pedir:

- parser IMSI/PCAP;
- decoder SMS/voz;
- normalizador `evidence_schema`;
- soporte de banda no cubierta;
- wrapper YateBTS/srsRAN;
- módulo AT por modelo;
- portal/payload específico;
- módulo RF nuevo;
- clasificador TAC;
- reparación de herramienta incompatible.

Hermes Agent trabaja en `modules/laboratory/<technique_id>/` y debe generar:

- `technique.json`;
- `worker.py`;
- parser;
- `evidence_schema.json`;
- `requirements.generated.txt`;
- README;
- reporte de sandbox.

La promoción solo procede tras revisión, sandbox, aprobación humana, VersionLock, Policy Engine, Kill Switch, EvidenceStore y AuditLog.

### Estados visuales globales BTS

Lista exacta de estados globales BTS:

- `hardware_missing`
- `hackrf_ready`
- `scanning_bands`
- `band_selected`
- `bts_configured`
- `bts_starting`
- `bts_active`
- `device_attached`
- `traffic_relaying`
- `sms_intercepting`
- `call_recording`
- `payload_injection_ready`
- `at_console_ready`
- `error`
- `blocked_by_policy`
- `kill_switch_triggered`
- `closed`

Cada estado debe tener icono, color, texto, último evento, operador, timestamp y acción siguiente sugerida por LaIA.

### Estados de dispositivo conectado

Lista exacta de estados de dispositivo conectado:

- `detected`
- `attached`
- `identified`
- `classified`
- `idle`
- `relaying_traffic`
- `sms_active`
- `call_active`
- `payload_pending`
- `at_ready`
- `action_running`
- `evidence_generated`
- `disconnected`
- `closed`

### Redacción y privacidad visual

La política visual del Vector 7 exige:

- IMSI/IMEI completos enmascarados por defecto;
- cuerpos SMS enmascarados por defecto;
- grabaciones y PCAP visibles como metadatos, no contenido completo por defecto;
- botón **Mostrar completo** con confirmación y AuditLog;
- exportación completa solo con confirmación;
- PDF/informes usan redacción por defecto.


### Técnicas registradas del Vector 7

Cada acción IMSI/BTS/RF del Vector 7 se documenta como técnica nominal con `technique_id`, contrato JSON, evidencias esperadas, nivel de riesgo, requisitos de hardware, confirmación, estado de implementación y trazabilidad. Todas las técnicas de esta lista quedan con `HARDWARE_REQUIRED`, `IMPLEMENTACION_USUARIO_REQUERIDA`, validación futura por X5/OjoRouter, Policy Engine, Kill Switch, EvidenceStore, AuditLog y VersionLock. Las técnicas que impliquen emisión RF añaden además `RF_TRANSMIT`.

Lista oficial de técnicas nominales:

#### `android.imsi.scan_bands`

- **Descripción**: escaneo de espectro y detección de bandas/operadoras en laboratorio.
- **Herramientas nominales**: HackRF tools, `hackrf_sweep` y waterfall panel.
- **Evidencias**: `rf_scan_report`, `radio_profile_json` y captura del panel.
- **Confirmación**: no requiere confirmación fuerte si es solo lectura RF pasiva, pero sí requiere `hardware_check` y scope laboratorio.
- **Estado**: `HARDWARE_REQUIRED`, `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.imsi.start_2g`

- **Descripción**: inicio de BTS 2G de laboratorio con YateBTS o equivalente validado.
- **Confirmación**: requiere confirmación explícita.
- **Estado**: `RF_TRANSMIT`, `HARDWARE_REQUIRED`, `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Evidencias**: `radio_profile_json`, `bts_session_log` y AuditLog.

#### `android.imsi.start_4g`

- **Descripción**: inicio de eNodeB/stack LTE de laboratorio con srsRAN o equivalente validado.
- **Confirmación**: requiere confirmación explícita.
- **VersionLock**: debe resolver si se usa stack LTE legacy o rama moderna compatible.
- **Estado**: `RF_TRANSMIT`, `HARDWARE_REQUIRED`, `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Evidencias**: `radio_profile_json`, `bts_session_log` y PCAP si aplica.

#### `android.imsi.capture_imsi`

- **Descripción**: captura/registro de IMSI/IMEI en entorno de laboratorio.
- **Redacción**: datos sensibles enmascarados por defecto.
- **Evidencias**: `imsi_list.json`, `device_fingerprint.json` y `timeline_json`.
- **Confirmación**: mostrar completo requiere confirmación y AuditLog.
- **Estado**: `HARDWARE_REQUIRED`, `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.imsi.downgrade_to_2g`

- **Descripción**: downgrade 4G→2G como capacidad nominal de laboratorio.
- **Confirmación**: requiere confirmación reforzada.
- **Estado**: `RF_TRANSMIT`, `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Controles**: técnica sensible con `stop_conditions` estrictas y Kill Switch visible.

#### `android.imsi.mitm_traffic`

- **Descripción**: relay/inspección/modificación de tráfico dentro de laboratorio.
- **Confirmación**: requiere confirmación explícita.
- **Estado**: `RF_TRANSMIT`, `HARDWARE_REQUIRED`, `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Evidencias**: `pcap_imsi_catcher`, logs de relay/proxy y timeline.
- **Handoff**: posible a Módulo 6 MITM/Red.

#### `android.imsi.inject_payload_http`

- **Descripción**: inyección nominal de APK/artefacto sobre tráfico HTTP de laboratorio.
- **Confirmación**: requiere confirmación reforzada.
- **Estado**: `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Evidencias**: `payload_injected.json`, PCAP y captura panel.

#### `android.imsi.inject_payload_sms`

- **Descripción**: envío nominal de SMS especial/binario/clase 0 dentro de laboratorio.
- **Confirmación**: requiere confirmación reforzada.
- **Estado**: `RF_TRANSMIT`, `HARDWARE_REQUIRED`, `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Evidencias**: `sms_intercepted.json`, `payload_injected.json` y AuditLog.
- **Redacción**: datos sensibles enmascarados por defecto.

#### `android.imsi.inject_payload_portal`

- **Descripción**: portal cautivo nominal para laboratorio.
- **Confirmación**: requiere confirmación explícita.
- **Estado**: `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Evidencias**: `payload_injected.json`, logs del portal y capturas del panel.

#### `android.imsi.intercept_sms`

- **Descripción**: intercepción/captura de SMS en laboratorio.
- **Confirmación**: requiere confirmación explícita.
- **Estado**: `RF_TRANSMIT`, `HARDWARE_REQUIRED`, `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Evidencias**: `sms_intercepted.json`.
- **Redacción**: cuerpos SMS enmascarados por defecto.

#### `android.imsi.intercept_call`

- **Descripción**: intercepción/grabación nominal de llamada en entorno controlado.
- **Confirmación**: requiere confirmación reforzada.
- **Estado**: `RF_TRANSMIT`, `HARDWARE_REQUIRED`, `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Evidencias**: `call_recording.wav`, metadata y AuditLog.
- **Redacción**: grabaciones no se muestran completas por defecto.

#### `android.imsi.send_at_command`

- **Descripción**: acción nominal para enviar comandos AT a dispositivo/módem compatible.
- **Confirmación**: requiere confirmación explícita.
- **Estado**: `HARDWARE_REQUIRED`, `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Evidencias**: `at_command_log.txt`.
- **Hermes Agent**: puede crear módulo AT por modelo.

#### `android.imsi.dos_device`

- **Descripción**: denegación de servicio nominal contra dispositivo concreto en laboratorio.
- **Confirmación**: requiere confirmación reforzada.
- **Estado**: `RF_TRANSMIT`, `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Evidencias**: `dos_event_log`, timeline y AuditLog.

#### `android.imsi.identify_device_type`

- **Descripción**: identificación por TAC, fabricante, patrón de comportamiento y servicios.
- **Estado**: `HARDWARE_REQUIRED`, `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Evidencias**: `device_fingerprint.json`.
- **Handoff**: puede alimentar Módulo 1 OSINT, Módulo 10 RF y Módulo 13 Android.

### Contrato JSON `imsi_action`

Contrato base documental para cualquier acción del Vector 7. No ejecuta nada y no representa endpoint, worker ni lógica BTS real.

```json
{
  "type": "imsi_action",
  "session_id": "sess-7890",
  "device_id": "dev-1234",
  "imsi": "masked_or_full",
  "imei": "masked_or_full",
  "tac": "12345678",
  "technique_id": "android.imsi.intercept_sms",
  "radio_profile": {
    "technology": "GSM",
    "band": "GSM900",
    "arfcn": 512,
    "frequency": 900.2,
    "mcc": "001",
    "mnc": "01",
    "lac": 100,
    "cell_id": 10,
    "tx_power": 30,
    "gain": 20,
    "antenna": "internal",
    "lab_zone": "faraday_cage_1",
    "faraday_required": true,
    "hardware_id": "hackrf_001",
    "versionlock_tools": {
      "yatebts": "nominal",
      "srsran": "nominal",
      "hackrf_tools": "nominal"
    }
  },
  "params": {
    "duration": 60,
    "filter_type": "all"
  },
  "expected_evidence": ["sms_intercepted.json", "pcap_imsi_catcher"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true,
  "risk_level": "high",
  "hardware_check": true,
  "rf_policy_check": true,
  "policy_check": true,
  "kill_switch_required": true,
  "stop_conditions": ["kill_switch_active", "out_of_scope", "hardware_lost", "timeout_reached"],
  "cleanup_required": true
}
```

X5/OjoRouter debe rechazar cualquier `imsi_action` sin scope laboratorio, operador, hardware_check, RF policy, Policy Engine, Kill Switch, VersionLock, permisos y evidencia esperada. Si `requires_confirmation` es `true`, no se permite pasar a ejecución futura sin confirmación humana registrada.

### Contrato `radio_profile`

Campos oficiales del perfil RF:

- `technology`: GSM, LTE, NR.
- `band`.
- `arfcn`, `earfcn`, `nr_arfcn` si aplica.
- `frequency`.
- `mcc`.
- `mnc`.
- `lac` / `tac`.
- `cell_id`.
- `tx_power`.
- `gain`.
- `antenna`.
- `lab_zone`.
- `faraday_required`.
- `hardware_id`.
- `versionlock_tools`.
- `created_at`.
- `operator`.
- `scope`.

El perfil RF debe guardarse como evidencia `radio_profile_json` al iniciar una sesión. Ningún `radio_profile` autoriza por sí solo emisión RF; solo describe configuración propuesta o usada dentro del laboratorio.

### Flujo asistido Mistral + X5

Flujo exacto previsto para Vector 7:

1. El usuario abre **Android > IMSI Catcher**.
2. El panel verifica HackRF/hardware y herramientas mediante VersionLock/tool_healthcheck.
3. El usuario pulsa **Escanear bandas**.
4. LaIA/Mistral interpreta resultados y sugiere banda/tecnología.
5. El usuario revisa configuración RF.
6. El usuario pulsa **Preparar plan**.
7. Mistral genera `imsi_action` para `android.imsi.start_2g` o `android.imsi.start_4g`.
8. El panel muestra modal con técnica, `radio_profile`, riesgo, evidencias, confirmaciones y `stop_conditions`.
9. El usuario confirma.
10. X5/OjoRouter valida:
    - `hardware_check`;
    - `rf_policy_check`;
    - scope;
    - Policy Engine;
    - Kill Switch;
    - VersionLock;
    - permisos del operador.
11. Si valida, X5 enrutaría a worker futuro.
12. El panel cambia a `bts_active`.
13. Cuando aparece dispositivo, LaIA clasifica TAC/comportamiento.
14. El usuario elige acción contextual.
15. Mistral genera nuevo `imsi_action`.
16. X5 valida otra vez.
17. El panel muestra progreso y evidencias.
18. Al finalizar se guarda EvidenceStore y AuditLog.

Este flujo es documental y no implica ejecución actual de RF, BTS, relay, intercepción, payload, AT ni DoS.

### Qué ve el usuario en cada fase

**Escaneo de bandas**:

- waterfall;
- tabla de frecuencia/potencia/tecnología;
- recomendación LaIA;
- botón Auto;
- modo experto manual.

**Selección de banda**:

- `radio_profile` propuesto;
- campos editables;
- warnings de VersionLock/hardware;
- Policy status.

**Revisión del plan**:

- técnica propuesta;
- riesgos;
- evidencia esperada;
- `stop_conditions`;
- botón Confirmar.

**Confirmación de emisión**:

- confirmación explícita;
- estado de laboratorio;
- Kill Switch visible.

**BTS activa**:

- indicador verde;
- contador de dispositivos;
- tabla de dispositivos;
- acciones rápidas.

**Dispositivo conectado**:

- línea resaltada;
- IMSI/IMEI enmascarados;
- TAC/fabricante/tipo estimado;
- botón Detalle.

**Acción sobre dispositivo**:

- modal de técnica;
- parámetros;
- evidencias;
- progreso;
- cancelar/parar.

**Evidencias generadas**:

- enlaces EvidenceStore;
- vista enmascarada por defecto;
- opción Mostrar completo con AuditLog.

**Cierre**:

- botón **Apagar BTS**;
- progreso de limpieza;
- estado final `closed`.

### Confirmaciones explícitas

Requieren confirmación explícita o reforzada según riesgo:

- iniciar BTS;
- downgrade 4G→2G;
- MITM de tráfico;
- inyección payload HTTP;
- inyección SMS;
- portal cautivo;
- interceptar SMS;
- interceptar llamada;
- enviar comandos AT;
- DoS;
- exportar datos sensibles;
- mostrar IMSI/IMEI completos;
- mostrar SMS completos;
- reproducir/exportar grabación completa.

### Evidencias exactas

Tipos exactos de evidencia del Vector 7:

- `pcap_imsi_catcher`: captura de tráfico completa.
- `imsi_list.json`: IMSI/IMEI enmascarados por defecto.
- `call_recording.wav`: grabación con metadatos.
- `sms_intercepted.json`: SMS con redacción por defecto.
- `payload_injected.json`: registro de inyección.
- `at_command_log.txt`: comandos AT y respuestas.
- `device_fingerprint.json`: TAC, tipo, fabricante/modelo estimado.
- `rf_scan_report`: bandas, frecuencia, potencia.
- `radio_profile_json`: configuración RF usada.
- `bts_session_log`: estado BTS.
- `timeline_json`: cronología completa.
- `audit_log`: decisiones, confirmaciones y resultados.

### Enmascarado y datos sensibles

- IMSI/IMEI completos ocultos por defecto.
- SMS ocultos por defecto.
- Grabaciones y PCAP visibles como metadatos por defecto.
- Botón **Mostrar completo** exige confirmación y AuditLog.
- Exportación completa exige confirmación reforzada.
- PDF/informes usan redacción por defecto.
- Handoff a Módulo 5 Credenciales solo con datos enmascarados salvo confirmación.

### Hermes Agent avanzado para Vector 7

Hermes Agent entra cuando exista:

- banda no soportada;
- parser IMSI/PCAP faltante;
- TAC desconocido;
- módulo AT por modelo;
- portal/payload específico;
- soporte YateBTS/srsRAN incompatible;
- decoder SMS/voz;
- módulo RF nuevo;
- normalizador `evidence_schema`;
- clasificador de dispositivo;
- reparación de VersionLock/tool wrapper.

Acciones Hermes documentales:

- `create_imsi_parser`
- `create_pcap_decoder`
- `create_tac_classifier`
- `create_at_module`
- `create_rf_tool_wrapper`
- `create_sms_voice_decoder`
- `create_evidence_schema`
- `repair_bts_wrapper`
- `create_portal_payload_module`

Hermes Agent trabaja en `modules/laboratory/<technique_id>/` y genera:

- `technique.json`;
- `worker.py`;
- parser;
- `evidence_schema.json`;
- `requirements.generated.txt`;
- `README.md`;
- reporte sandbox.

La promoción solo procede tras revisión, sandbox, aprobación humana, VersionLock, Policy Engine, Kill Switch, EvidenceStore y AuditLog. Hermes Agent no autoaprueba capacidades RF, BTS, AT, payload, relay, intercepción ni DoS.

### Cierre seguro: Apagar BTS

Secuencia exacta del flujo **Apagar BTS**:

1. Detener emisión BTS/eNodeB/gNodeB.
2. Parar captura PCAP.
3. Cerrar proxies/relay.
4. Detener grabaciones.
5. Guardar evidencias pendientes.
6. Cerrar consola AT.
7. Limpiar estado temporal.
8. Restaurar configuración de red/laboratorio si aplica.
9. Registrar AuditLog.
10. Actualizar scoring X5 solo si hay evidencia válida.
11. Marcar dispositivos como `closed`.
12. Cambiar estado global a `closed`.

El cierre seguro no inicia acciones nuevas y debe permanecer disponible desde la pestaña BTS Activa, desde el panel de dispositivo y desde Kill Switch.


### Handoff del Vector 7 con otros módulos

El Vector 7 no trabaja aislado. Sus evidencias, dispositivos, tráfico y hallazgos pueden enviarse a otros módulos mediante contratos auditados, redacción por defecto, EvidenceStore, AuditLog, Policy Engine, Kill Switch y validación X5/OjoRouter.

#### Handoff con Módulo 10 — Wireless / RF general

El Vector 7 reutiliza la capa RF/HackRF del Módulo 10 para:

- estado del HackRF;
- waterfall;
- control documental de frecuencia, ganancia, antena y perfil RF;
- evidencias IQ/PCAP;
- `radio_profile_json`;
- `rf_scan_report`;
- estado de emisión;
- kill switch RF.

Las capturas RF, IQ, PCAP y reportes generados durante sesiones IMSI/BTS deben almacenarse en el mismo EvidenceStore y respetar la misma política de metadatos, hash, redacción, timeline y AuditLog que M10.

#### Handoff con Módulo 6 — Red / MITM

Cuando el Vector 7 genere tráfico relay, PCAP o sesión de datos, puede crear handoff hacia Módulo 6 para análisis de red/MITM.

Casos documentales:

- `pcap_imsi_catcher` necesita análisis de protocolo.
- Tráfico relay requiere proxy o inspección.
- Se detectan cookies, tokens o credenciales.
- Se necesita correlacionar tráfico con otros dispositivos de la red.

M6 recibe evidencia, no acceso libre. LaIA/Mistral debe preparar handoff revisable y X5/OjoRouter valida Policy Engine, Kill Switch y scope antes de permitir cualquier continuidad futura.

#### Handoff con Módulo 5 — Credenciales

Si durante la sesión IMSI aparecen secretos, SMS, tokens, cookies, credenciales o datos de autenticación, el Vector 7 no los trata como texto suelto. Debe empaquetarlos como `credential_handoff` hacia M5.

Reglas documentales:

- valores enmascarados por defecto;
- `source_module = "android"`;
- `source_vector = "imsi_catcher"`;
- `source_evidence_id` obligatorio;
- M5 clasifica, deduplica y decide acciones;
- mostrar completo requiere confirmación y AuditLog.

#### Handoff con Módulo 12 — Orquestación

Toda acción `android.imsi.*` hereda el flujo M12:

- LaIA/Mistral genera plan y rellena parámetros.
- X5/OjoRouter valida hardware, scope, Policy Engine, Kill Switch, VersionLock y permisos.
- EvidenceStore guarda evidencias.
- AuditLog registra decisiones, confirmaciones y resultados.
- Scoring X5 solo se actualiza con evidencia válida.
- Hermes Agent se activa si falta parser, wrapper, decoder, soporte de banda, TAC, AT o `evidence_schema`.

#### Handoff interno dentro del Módulo 13

El Vector 7 también puede enviar hallazgos a otros vectores Android:

- **Vector 3 Control Remoto**: si un dispositivo queda identificado/controlable, se transfiere `device_id`, estado y evidencias para abrir panel de control remoto.
- **Vector 5 Red Móvil / MITM**: si hay tráfico relay, PCAP o sesión de datos, se envía a Red Móvil para análisis más profundo.
- **Vector 6 Análisis de Apps**: si se detecta APK, perfil, payload o app relacionada, se transfiere a Análisis de Apps para descompilación, secretos, endpoints y reporte.

### Contrato JSON `rf_handoff`

Contrato base documental para handoff RF/IMSI/BTS hacia otros módulos. No representa endpoint ni ejecución real.

```json
{
  "type": "rf_handoff",
  "source_module": "android",
  "source_vector": "M13_V7",
  "session_id": "sess-7890",
  "device_id": "dev-1234",
  "radio_profile_id": "rp-001",
  "evidence_ids": ["ev-001", "ev-002"],
  "target_module": "M13_V5",
  "handoff_reason": "traffic_relay_ready",
  "redaction_policy": "mask_imsi",
  "requires_confirmation": true,
  "operator": "admin",
  "created_at": "2026-06-02T10:00:00Z"
}
```

Campos obligatorios:

- `type`
- `source_module`
- `source_vector`
- `session_id`
- `device_id`
- `radio_profile_id`
- `evidence_ids`
- `target_module`
- `handoff_reason`
- `redaction_policy`
- `requires_confirmation`
- `operator`
- `created_at`

### Preflight RF antes de emitir

Antes de habilitar **Iniciar BTS**, el panel debe mostrar un checklist automático:

- [ ] HackRF detectado (`hardware_check` OK).
- [ ] Antena seleccionada.
- [ ] `lab_zone` definida.
- [ ] `faraday_required` validado si aplica.
- [ ] VersionLock OK para herramientas requeridas.
- [ ] Kill Switch armado y visible.
- [ ] Operador autenticado y autorizado.
- [ ] Policy Engine permite la acción.
- [ ] `radio_profile` completo.
- [ ] `radio_profile_json` guardado.
- [ ] Confirmación explícita del usuario recibida.

Si cualquier ítem falla:

- botón **Iniciar BTS** desactivado;
- estado `blocked_by_policy`, `hardware_missing` o `error`;
- LaIA/Mistral explica el motivo;
- AuditLog registra bloqueo si hubo intento de ejecución.

### Errores y recuperación

Estados de fallo y respuesta esperada del panel:

#### HackRF desconectado durante sesión

- estado global: `error`;
- detener emisión si existía;
- guardar evidencias pendientes;
- registrar AuditLog;
- mostrar **Hardware desconectado**.

#### Herramienta incompatible por VersionLock

- bloquear inicio;
- mostrar herramienta y versión detectada;
- estado `blocked_by_policy` o `error`;
- sugerir Hermes Agent si falta wrapper o compatibilidad.

#### BTS no arranca

- guardar logs;
- no dejar sesión a medias;
- estado `error`;
- LaIA/Mistral prepara diagnóstico;
- Hermes Agent puede crear wrapper/reparación si procede.

#### Dispositivo se desconecta

- estado del dispositivo: `disconnected`;
- guardar evidencias asociadas;
- no detener BTS global salvo Policy Engine o Kill Switch.

#### PCAP no se guarda

- estado `error`;
- detener captura;
- guardar logs disponibles;
- notificar fallo de evidencia.

#### Kill Switch activado

- estado `kill_switch_triggered`;
- detener emisión;
- detener capturas;
- cerrar relay/proxies;
- guardar evidencias pendientes;
- AuditLog prioritario.

#### Policy bloquea emisión

- estado `blocked_by_policy`;
- no ejecutar nada;
- mostrar motivo;
- registrar intento.

En todos los casos debe ejecutarse `cleanup_required` si había sesión o recursos activos.

### Scoring X5 del Vector 7

Reglas documentales de scoring:

- Solo puntúa si hay evidencia válida.
- `hardware_missing` no penaliza técnica.
- `blocked_by_policy` no penaliza técnica.
- Fallo por herramienta incompatible puede bajar score del wrapper/tool integration, no de la técnica RF.
- Falso positivo de TAC baja score de `android.imsi.identify_device_type`.
- Captura válida con evidencia sube score de `android.imsi.capture_imsi`.
- PCAP útil sube score de captura/relay correspondiente.
- Evidencia corrupta o ausente no sube score.
- Técnicas con `IMPLEMENTACION_USUARIO_REQUERIDA` no puntúan hasta promoción.
- Técnicas `RF_TRANSMIT` no puntúan si no pasan preflight, confirmación y EvidenceStore.

Campos recomendados:

- `technique_id`
- `session_id`
- `device_type`
- `radio_profile_id`
- `evidence_valid`
- `blocked_by_policy`
- `hardware_available`
- `false_positive`
- `score_before`
- `score_after`
- `score_delta`
- `operator`

### Preparación para Módulo 16 — Evidencia / Ops / Calidad

Todas las evidencias RF/IMSI deben quedar preparadas para M16.

Requisitos documentales:

- SHA256 de cada archivo de evidencia.
- Hashes encadenados en `timeline_json`.
- Cadena de custodia interna: acceso, revelado, exportación, modificación, operador y timestamp.
- Exportación enmascarada por defecto.
- Exportación completa solo con confirmación reforzada.
- Metadatos: `session_id`, `device_id`, `radio_profile_id`, `technique_id`, `scope`, `operator`, VersionLock.
- Informes compatibles con compilador final de M16.
- Integridad verificable antes de handoff o exportación.

Tipos relevantes:

- PCAP;
- IQ si aplica;
- grabaciones;
- SMS;
- logs AT;
- radio_profile;
- timeline;
- capturas del panel;
- AuditLog.

### Criterios de aceptación del Vector 7

Vector 7 queda documentalmente cerrado si `docs/techniques/13_ANDROID.md` contiene:

- [ ] Propósito IMSI/BTS/RF documentado.
- [ ] Hardware requerido documentado.
- [ ] Herramientas nominales y VersionLock documentados.
- [ ] Panel **Android > IMSI Catcher** documentado.
- [ ] Subpáginas exactas documentadas.
- [ ] Estados BTS documentados.
- [ ] Estados por dispositivo documentados.
- [ ] Técnicas `android.imsi.*` documentadas.
- [ ] Contratos `imsi_action`, `radio_profile` y `rf_handoff` documentados.
- [ ] Confirmaciones explícitas documentadas.
- [ ] Evidencias documentadas.
- [ ] Enmascarado/redacción documentado.
- [ ] Preflight RF documentado.
- [ ] Errores/recuperación documentados.
- [ ] Cierre seguro documentado.
- [ ] Handoff M10/M6/M5/M12/M13 interno documentado.
- [ ] Hermes Agent documentado.
- [ ] Scoring X5 documentado.
- [ ] Preparación M16 documentada.
- [ ] No se afirma implementación real de emisión/intercepción.

### Nota final del Vector 7

El Vector 7 queda definido como especificación de producto/laboratorio. Esta documentación no crea lógica funcional ni afirma ejecución real. Las partes sensibles permanecen marcadas como:

- `IMPLEMENTACION_USUARIO_REQUERIDA`
- `HARDWARE_REQUIRED`
- `RF_TRANSMIT`

### Reglas finales del Vector 7

No crear lógica. No ejecutar RF. No crear comandos operativos. No instalar herramientas. No añadir tests. No afirmar soporte funcional. Mantener el Vector 7 como documentación exacta de producto, panel, estados, hardware, VersionLock, LaIA/X5/Hermes/DeepSeek, EvidenceStore, AuditLog, Policy y Kill Switch.

## Vector 8 — Servicio de Accesibilidad y Registro de Eventos

El Vector 8 define el **Servicio de Accesibilidad y Registro de Eventos** como especificación de producto/laboratorio para Android. Su propósito documental es describir cómo el panel **Android > Accesibilidad** debe preparar, revisar, autorizar, registrar y preservar eventos de accesibilidad dentro de un entorno autorizado, sin crear lógica funcional de registro, monitorización, endpoints, workers, base de datos, tests, scripts ni comandos operativos.

Toda capacidad sensible del Vector 8 permanece marcada como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta que exista implementación futura aprobada, promoción explícita, scope válido, Policy Engine favorable, Kill Switch armado, EvidenceStore operativo y AuditLog completo. Esta documentación no afirma ejecución real de keylogging, captura de notificaciones, monitorización de pantalla, lectura de códigos, evasión, instalación de servicios ni modificación de permisos.

### Propósito del Vector 8

El Vector 8 documenta un flujo controlado para sesiones de accesibilidad en laboratorio autorizado. El panel debe permitir que el operador revise intención, alcance, dispositivo, permisos, redacción de datos, evidencias esperadas y criterios de parada antes de activar cualquier registro futuro.

Objetivos documentales:

- centralizar eventos de accesibilidad autorizados bajo una sesión trazable;
- preservar evidencias con redacción por defecto;
- detectar hallazgos relevantes sin tratarlos como texto suelto;
- preparar handoff seguro hacia M5, M12, M13 interno y M16;
- mantener confirmaciones explícitas para acciones sensibles;
- asegurar que toda lógica real de captura o monitorización siga como `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Herramientas nominales y VersionLock

Las herramientas nominales del Vector 8 se registran como inventario de laboratorio y no implican instalación, ejecución ni soporte funcional en esta ronda:

- `apktool` para inspección/reempaquetado autorizado de APK en laboratorio;
- `msfvenom` como referencia nominal de generación Android bajo VersionLock y políticas heredadas;
- `ProGuard`/R8 para ofuscación compatible con proyectos Android autorizados;
- `Obfuscapk` para variantes ofuscadas controladas en laboratorio;
- `JDK` para firma, certificados y utilidades Java cuando exista pipeline aprobado;
- `Frida` para instrumentación autorizada y observación controlada;
- `objection` para apoyo de análisis dinámico autorizado.

VersionLock debe registrar versión detectada, fuente, compatibilidad, decisión de uso, fecha, operador y motivo. Si VersionLock no valida una herramienta, el panel debe bloquear la activación o dejarla en modo documental/dry-run. La presencia de una herramienta en esta lista no significa que esté instalada, permitida ni disponible.

### Panel **Android > Accesibilidad**

El panel **Android > Accesibilidad** debe mostrar una vista específica para el Vector 8 con estado del dispositivo, estado del servicio, preflight, configuración de redacción, evidencias esperadas, acciones revisables, handoffs y timeline.

Subpáginas exactas documentadas:

- **Resumen**: estado del dispositivo, sesión, agente C2, permiso de accesibilidad, Kill Switch, Policy Engine y último AuditLog.
- **Registro de Eventos**: configuración documental para pulsaciones, notificaciones, secuencias táctiles y eventos del servicio.
- **Notificaciones**: vista enmascarada de eventos de notificación y clasificación de posibles códigos 2FA o secretos.
- **Evasión / Ofuscación**: estado nominal de ofuscación, compatibilidad, AV/Play Protect y propuestas Hermes Agent.
- **Handoff**: envíos revisables hacia M5, M12 y vectores internos de M13.
- **Evidencias**: `keylog.csv`, `notifications.json`, `touch_sequences`, `evasion_report`, `timeline`, capturas del panel y AuditLog.
- **M16 Ready**: integridad, SHA256, hashes encadenados, cadena de custodia, exportación enmascarada y exportación completa con confirmación reforzada.

Ninguna subpágina ejecuta acciones por sí misma. Cualquier botón debe abrir un plan revisable generado por LaIA/Mistral y validado por X5/OjoRouter antes de una ejecución futura aprobada.

### Estados del servicio

Estados documentales del Vector 8:

- `idle`: sin sesión activa.
- `preflight_required`: faltan validaciones previas.
- `ready`: preflight completo y pendiente de confirmación.
- `starting`: activación futura solicitada y en validación.
- `active`: sesión documentalmente activa cuando exista implementación futura.
- `paused`: registro pausado por operador o política.
- `stopping`: cierre seguro en curso.
- `stopped`: sesión finalizada.
- `permission_missing`: permiso de accesibilidad ausente o no validado.
- `blocked_by_policy`: Policy Engine no permite la acción.
- `blocked_by_av`: antivirus, Play Protect u otro control bloquea el servicio.
- `disconnected`: dispositivo desconectado.
- `kill_switch_triggered`: Kill Switch activado.
- `error`: fallo genérico.
- `cleanup_required`: quedan sesión o recursos activos que deben cerrarse/preservarse.

### Técnicas `android.accessibility.*`

Las técnicas del Vector 8 se documentan como catálogo futuro. Todas quedan en estado `IMPLEMENTACION_USUARIO_REQUERIDA` hasta promoción:

#### `android.accessibility.event_logging`

- **description**: registro autorizado de eventos de accesibilidad de una sesión controlada.
- **required_inputs**: `session_id`, `device_id`, scope, permiso de accesibilidad, confirmación explícita, política de redacción y operador.
- **expected_evidence**: `timeline`, eventos normalizados, AuditLog y hashes SHA256.
- **risk_level**: alto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.accessibility.notification_capture`

- **description**: captura documental de notificaciones bajo redacción por defecto para detectar hallazgos relevantes sin exponer secretos.
- **required_inputs**: `session_id`, `device_id`, scope, redacción activa y confirmación explícita.
- **expected_evidence**: `notifications.json`, timeline, AuditLog y metadatos de redacción.
- **risk_level**: alto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.accessibility.touch_sequences`

- **description**: preservación de secuencias táctiles autorizadas como evidencia abstracta y minimizada.
- **required_inputs**: `session_id`, `device_id`, scope, redacción, ventana temporal y confirmación explícita.
- **expected_evidence**: `touch_sequences`, timeline encadenado y AuditLog.
- **risk_level**: alto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.accessibility.credential_detection`

- **description**: detección documental de posibles códigos de verificación, contraseñas, tokens o datos de autenticación para handoff seguro a M5.
- **required_inputs**: evidencia fuente, `source_evidence_id`, redacción `mask_all`, target M5 y confirmación si se solicita revelado.
- **expected_evidence**: `credential_handoff`, referencia a evidencia original, AuditLog y decisión M5.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.accessibility.evasion_obfuscation`

- **description**: generación futura de variante ofuscada de laboratorio cuando AV/Play Protect bloquee el servicio y Policy Engine lo permita.
- **required_inputs**: artefacto autorizado, motivo, VersionLock, scope, evidencia de bloqueo, confirmación y entorno de laboratorio.
- **expected_evidence**: `evasion_report`, hashes, configuración, resultado de laboratorio y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Contrato JSON `accessibility_action`

Contrato documental base para acciones del Vector 8. No representa endpoint ni ejecución real.

```json
{
  "type": "accessibility_action",
  "source_module": "android",
  "source_vector": "M13_V8",
  "technique_id": "android.accessibility.event_logging",
  "session_id": "sess-7890",
  "device_id": "dev-1234",
  "action": "activate_logging",
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
- `technique_id`
- `session_id`
- `device_id`
- `action`
- `redaction_policy`
- `requires_confirmation`
- `operator`
- `created_at`

### Handoff con otros módulos

El Vector 8 no trabaja aislado. Sus evidencias, eventos registrados y hallazgos pueden enviarse a otros módulos mediante contratos auditados y con redacción por defecto.

#### Handoff con Módulo 5 — Credenciales

Si durante la sesión de accesibilidad aparecen códigos de verificación, contraseñas, tokens o cualquier dato de autenticación, el Vector 8 no los trata como texto suelto. Debe empaquetarlos como `credential_handoff` hacia M5.

Reglas:

- valores enmascarados por defecto;
- `source_module = "android"`;
- `source_vector = "accessibility"`;
- `source_evidence_id` obligatorio;
- M5 clasifica, deduplica y decide acciones;
- mostrar completo requiere confirmación y AuditLog.

#### Handoff con Módulo 12 — Orquestación

Toda acción `android.accessibility.*` hereda el flujo M12:

- LaIA/Mistral genera plan y rellena parámetros;
- X5/OjoRouter valida hardware, scope, Policy, Kill Switch, VersionLock y permisos;
- EvidenceStore guarda;
- AuditLog registra;
- scoring X5 solo con evidencia válida;
- Hermes Agent se activa si falta parser, ofuscación, bypass de detección o `evidence_schema`.

#### Handoff interno dentro del Módulo 13

El Vector 8 también puede enviar hallazgos a otros vectores Android:

- **Vector 3 Control Remoto**: si el dispositivo está controlable, se transfiere `device_id`, estado y evidencias para abrir panel de control remoto.
- **Vector 6 Análisis de Apps**: si se detecta una app desconocida durante el registro, se envía su APK al Vector 6 para descompilación, secretos, endpoints y reporte.

### Contrato JSON `accessibility_handoff`

Contrato base:

```json
{
  "type": "accessibility_handoff",
  "source_module": "android",
  "source_vector": "M13_V8",
  "session_id": "sess-7890",
  "device_id": "dev-1234",
  "evidence_ids": ["ev-001", "ev-002"],
  "target_module": "M5",
  "handoff_reason": "credential_found",
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

### Confirmaciones explícitas

El Vector 8 requiere confirmación explícita antes de activar registro, revelar datos completos, exportar evidencia completa, iniciar handoff sensible, solicitar ofuscación/evasión de laboratorio o cerrar una sesión con recursos pendientes.

La confirmación debe mostrar:

- acción solicitada;
- técnica `android.accessibility.*`;
- dispositivo y sesión;
- alcance autorizado;
- evidencias esperadas;
- política de redacción;
- riesgos y criterios de parada;
- efecto del Kill Switch;
- operador y timestamp.

### Evidencias y redacción por defecto

Evidencias documentales del Vector 8:

- `keylog.csv`;
- `notifications.json`;
- `touch_sequences`;
- `evasion_report`;
- `timeline`;
- capturas del panel;
- AuditLog.

Reglas de enmascarado/redacción:

- `mask_all` es la política por defecto para datos sensibles;
- códigos de verificación, contraseñas, tokens, cookies, secretos y autenticadores se muestran enmascarados;
- revelar valor completo requiere confirmación reforzada y AuditLog;
- exportación enmascarada es el modo por defecto;
- exportación completa solo procede con autorización reforzada, scope válido y registro de cadena de custodia;
- los datos sensibles nunca deben tratarse como texto suelto fuera de contratos auditados.

### Preflight antes de activar el servicio

Antes de habilitar **Activar registro**, el panel debe mostrar checklist automático:

- [ ] Dispositivo conectado y agente C2 operativo.
- [ ] Permiso de accesibilidad concedido o plan autorizado para forzarlo/corregirlo bajo Policy Engine.
- [ ] Kill Switch armado.
- [ ] Operador autenticado y autorizado.
- [ ] Policy Engine permite la acción.
- [ ] Enmascaramiento de datos sensible activo por defecto.
- [ ] Confirmación explícita del usuario recibida.

Si cualquier ítem falla:

- botón **Activar registro** desactivado;
- estado `blocked_by_policy`, `permission_missing` o `error`;
- LaIA explica el motivo;
- AuditLog registra bloqueo si hubo intento de ejecución.

### Errores y recuperación

Estados de fallo y respuesta del panel:

#### Servicio no arranca

- estado: `error`;
- guardar logs disponibles;
- LaIA sugiere revisar permisos o reinyectar APK;
- Hermes Agent puede crear wrapper/reparación si procede.

#### Antivirus bloquea el servicio

- estado: `blocked_by_av`;
- detener registro si estaba activo;
- guardar evidencias pendientes;
- LaIA sugiere ofuscación;
- Hermes Agent genera variante ofuscada en laboratorio.

#### Dispositivo se desconecta

- estado del dispositivo: `disconnected`;
- guardar evidencias asociadas;
- no detener otros servicios salvo Policy/Kill Switch.

#### Kill Switch activado

- estado `kill_switch_triggered`;
- detener servicio de accesibilidad;
- detener capturas;
- guardar evidencias pendientes;
- AuditLog prioritario.

#### Policy bloquea activación

- estado `blocked_by_policy`;
- no ejecutar nada;
- mostrar motivo;
- registrar intento.

En todos los casos debe ejecutarse `cleanup_required` si había sesión o recursos activos.

### Cierre seguro

El cierre seguro del Vector 8 debe:

- detener el servicio de accesibilidad cuando exista implementación futura activa;
- detener capturas o buffers asociados;
- sellar evidencias pendientes con SHA256;
- actualizar `timeline` y AuditLog;
- aplicar redacción por defecto a vistas y exportaciones;
- marcar `cleanup_required` si quedan recursos abiertos;
- bloquear nuevas acciones si Policy Engine, Kill Switch o VersionLock no permiten continuar.

### Hermes Agent en el Vector 8

Hermes Agent puede participar solo como constructor de laboratorio cuando falte parser, ofuscación, bypass de detección, wrapper, compatibilidad o `evidence_schema`. Sus propuestas no se autoaprueban, no se ejecutan en producción y deben pasar por Research → Quarantine → Analyze → Build → Sandbox Test → Evidence → Review → Approval → Promotion.

Cualquier artefacto sensible construido por Hermes Agent para el Vector 8 queda como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta promoción explícita.

### Scoring X5 del Vector 8

Reglas:

- Solo puntúa si hay evidencia válida: pulsaciones, notificaciones, códigos 2FA u otros eventos preservados dentro del scope.
- `permission_missing` no penaliza técnica.
- `blocked_by_policy` no penaliza técnica.
- Detección por antivirus penaliza la técnica si no se aplicó ofuscación.
- Éxito de ofuscación sube score de `android.accessibility.evasion_obfuscation`.
- Evidencia corrupta o ausente no sube score.
- Técnicas con `IMPLEMENTACION_USUARIO_REQUERIDA` no puntúan hasta promoción.

Campos recomendados:

- `technique_id`
- `session_id`
- `device_type`
- `evidence_valid`
- `blocked_by_policy`
- `false_positive`
- `score_before`
- `score_after`
- `score_delta`
- `operator`

### Preparación para Módulo 16 — Evidencia / Ops / Calidad

Todas las evidencias del Vector 8 deben quedar preparadas para M16.

Requisitos documentales:

- SHA256 de cada archivo de evidencia (`keylog.csv`, `notifications.json`).
- Hashes encadenados en `timeline_json`.
- Cadena de custodia interna: acceso, revelado, exportación, modificación, operador y timestamp.
- Exportación enmascarada por defecto.
- Exportación completa solo con confirmación reforzada.
- Metadatos: `session_id`, `device_id`, `technique_id`, `scope`, `operator`, VersionLock.
- Informes compatibles con compilador final de M16.
- Integridad verificable antes de handoff o exportación.

Tipos relevantes:

- `keylog.csv`;
- `notifications.json`;
- `touch_sequences`;
- `evasion_report`;
- `timeline`;
- capturas del panel;
- AuditLog.

### Criterios de aceptación del Vector 8

Vector 8 queda documentalmente cerrado si `docs/techniques/13_ANDROID.md` contiene:

- [ ] Propósito del Vector 8 documentado.
- [ ] Herramientas nominales y VersionLock documentados.
- [ ] Panel **Android > Accesibilidad** documentado.
- [ ] Subpáginas exactas documentadas.
- [ ] Estados del servicio documentados.
- [ ] Técnicas `android.accessibility.*` documentadas.
- [ ] Contratos `accessibility_action` y `accessibility_handoff` documentados.
- [ ] Confirmaciones explícitas documentadas.
- [ ] Evidencias documentadas.
- [ ] Enmascarado/redacción documentado.
- [ ] Preflight documentado.
- [ ] Errores/recuperación documentados.
- [ ] Cierre seguro documentado.
- [ ] Handoff M5/M12/M13 interno documentado.
- [ ] Hermes Agent documentado.
- [ ] Scoring X5 documentado.
- [ ] Preparación M16 documentada.
- [ ] No se afirma implementación real de registro o monitorización.

### Nota final del Vector 8

El Vector 8 queda definido como especificación de producto/laboratorio. Esta documentación no crea lógica funcional ni afirma ejecución real. Las partes sensibles permanecen marcadas como:

- `IMPLEMENTACION_USUARIO_REQUERIDA`

### Reglas finales del Vector 8

No crear lógica. No implementar endpoints. No crear workers. No modificar base de datos. No crear tests. No añadir requirements. No crear scripts. No añadir comandos operativos. No afirmar soporte funcional de registro o monitorización. Mantener el Vector 8 como documentación exacta de producto/laboratorio, handoff, preflight, errores, scoring, evidencia, ops, LaIA/X5/Hermes Agent, EvidenceStore, AuditLog, Policy Engine, Kill Switch, VersionLock y preparación M16.

## Vector 9 — Capa de Conectividad

El Vector 9 define la **Capa de Conectividad** de Android como especificación de producto/laboratorio para centralizar hardware, detección, paneles, técnicas registradas, contratos JSON y evidencias relacionadas con WiFi, Bluetooth, IoT tipo AP isla, NFC/RFID y RF auxiliar. Esta ronda es solo documentación: no implementa código, endpoints, workers, base de datos, tests, requirements, scripts funcionales, instalación de herramientas ni comandos operativos.

Toda técnica de conectividad queda bajo scope autorizado, Policy Engine, Kill Switch, VersionLock, EvidenceStore, AuditLog y confirmación explícita cuando aplique. Las capacidades sensibles permanecen como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta implementación futura aprobada y promoción formal.

### Herramientas y versiones nominales — Kali WSL2 + Windows

Las herramientas, versiones y ubicaciones siguientes se documentan como inventario objetivo de laboratorio. No se ejecutan ni instalan en esta ronda. VersionLock debe validar versión real, origen, compatibilidad, ubicación Windows/Kali, estado del driver, disponibilidad de hardware y decisión de uso antes de cualquier acción futura.

#### Adaptador WiFi Alfa — Realtek RTL8812AU

- **Hardware nominal**: adaptador WiFi Alfa con chipset Realtek RTL8812AU.
- **Windows**: driver en Windows para detección y operación base.
- **Kali WSL2**: para modo monitor, pasar el adaptador a Kali WSL2 con `usbipd-win` y validar `rtl88xxau-dkms` bajo VersionLock.
- **Uso documental**: WiFi scanning, Evil Twin, KARMA, PMKID y fuerza bruta a hotspot dentro de laboratorio autorizado.
- **Estado sensible**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### Dongle Bluetooth 5.3 — CSR8510 o similar

- **Hardware nominal**: dongle Bluetooth 5.3, CSR8510 o similar.
- **Windows**: driver en Windows para detección y operación base.
- **Kali WSL2**: para sniffing BLE y ataques avanzados, pasar el dongle a Kali WSL2 con `usbipd-win`.
- **Versiones nominales**:
  - BlueZ 5.70;
  - bleak 0.22;
  - Gattacker 1.0;
  - BtleJuice 1.0.
- **Uso documental**: Sniffing BLE, A2DP spoofing, BlueBorne y fuzzing BT 5.3 dentro de laboratorio autorizado.
- **Estado sensible**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### HackRF One

- **Hardware nominal**: HackRF One.
- **Windows**: driver en Windows para detección base.
- **Kali WSL2**: pasar a Kali WSL2 con `usbipd-win` para uso de herramientas RF autorizadas.
- **Versiones nominales**:
  - hackrf 2024.02;
  - gr-gsm 1.0;
  - gr-bluetooth.
- **Uso documental**: apoyo RF controlado para conectividad, correlación y laboratorio.
- **Estado sensible**: `IMPLEMENTACION_USUARIO_REQUERIDA`, `HARDWARE_REQUIRED` y, si aplica emisión RF, `RF_TRANSMIT`.

#### Lector ACR122U — NFC/RFID

- **Hardware nominal**: lector ACR122U para NFC/RFID.
- **Windows**: driver en Windows para detección base.
- **Kali WSL2**: pasar a Kali WSL2 con `usbipd-win` para laboratorio NFC/RFID autorizado.
- **Versiones nominales**:
  - libnfc 1.8;
  - mfoc 0.10;
  - mfcuk 0.10;
  - nfc-tools 0.7.
- **Uso documental**: clonación de tarjetas y relay NFC si hay dos lectores, siempre con autorización y evidencia.
- **Estado sensible**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### Paquete Kali WSL2 nominal

Versiones nominales para Kali WSL2:

- aircrack-ng 1.7;
- hcxdumptool/hcxtools;
- hostapd 2.10;
- dnsmasq 2.89;
- Bettercap 2.34;
- Airgeddon 11.0;
- nmap 7.99;
- hydra 9.7;
- Metasploit 6.4.x;
- wireshark 4.2;
- tshark 4.2;
- mitmproxy 10.2.

Estas versiones son referencias documentales para VersionLock. La documentación no autoriza ejecución directa, no define comandos y no sustituye validación de scope, hardware, permisos, Policy Engine, Kill Switch, evidencia esperada ni confirmación humana.

### Panel de control **Android > Conectividad**

El panel **Android > Conectividad** debe centralizar estado de hardware, descubrimiento de dispositivos, técnicas de conectividad, evidencias, historial y solicitudes Hermes. Ninguna subpágina ejecuta acciones por sí misma: LaIA/Mistral prepara un plan revisable, X5/OjoRouter valida hardware, scope, Policy, Kill Switch, permisos y VersionLock, y EvidenceStore/AuditLog preservan resultados si existe implementación futura aprobada.

Subpáginas documentadas:

- **Visor de Hardware**: indica qué dispositivos están disponibles —Alfa, BT 5.3, HackRF, ACR122U— y su ubicación —Windows o Kali—. Si falta hardware o no está en la ubicación requerida, sugiere la acción necesaria, por ejemplo **Pasar a Kali WSL2**, sin ejecutar pasos operativos.
- **Dispositivos Detectados**: tabla unificada con todos los dispositivos WiFi, Bluetooth e IoT APs detectados en tiempo real cuando exista implementación futura.
- **Ataques WiFi**: Evil Twin, KARMA, PMKID y Fuerza Bruta a Hotspot como técnicas registradas de laboratorio.
- **Ataques Bluetooth**: Sniffing BLE, A2DP Spoofing, BlueBorne y Fuzzing BT 5.3 como técnicas registradas de laboratorio.
- **Dispositivos IoT (AP Isla)**: escaneo de APs de bombillas, enchufes y cámaras; acceso documental a su portal web o API local si el scope lo permite.
- **NFC/RFID**: clonación de tarjetas y Relay NFC si hay dos lectores autorizados.
- **Evidencias**: PCAP, data dumps, capturas del panel, logs de herramienta, hashes y timeline.
- **Historial/AuditLog**: decisiones de Policy Engine, confirmaciones, bloqueos, errores, handoffs y cierre seguro.
- **Hermes Agent Lab**: solicitud de parsers, wrappers, compatibilidad, conectores de evidencia o adaptadores de laboratorio cuando falte capacidad.

### Estados visuales

Estados visuales del Vector 9:

- `hardware_missing`: falta un dispositivo requerido.
- `scanning`: buscando dispositivos WiFi/BT/IoT.
- `devices_found`: se muestran los dispositivos detectados.
- `attacking`: una técnica está en ejecución cuando exista implementación futura aprobada.
- `success`: ataque exitoso y evidencia generada dentro del scope.
- `error`: fallo en la ejecución, detección, hardware, herramienta o evidencia.
- `blocked_by_policy`: acción denegada por Policy Engine, scope, permisos, Kill Switch o VersionLock.

Los estados no implican ejecución real en esta ronda; son contrato de UI y orquestación para futuras promociones.

### Técnicas registradas `android.connectivity.*`

Las técnicas del Vector 9 quedan documentadas como registros esperados de catálogo. Todas requieren scope autorizado, preflight, VersionLock, confirmación cuando aplique y `IMPLEMENTACION_USUARIO_REQUERIDA` hasta promoción.

#### `android.connectivity.wifi_evil_twin`

- **description**: técnica WiFi Evil Twin para laboratorio autorizado y evidencia controlada.
- **hardware_required**: adaptador Alfa RTL8812AU o compatible validado.
- **expected_evidence**: PCAP, configuración de laboratorio, timeline, capturas del panel y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.connectivity.wifi_karma`

- **description**: técnica KARMA WiFi para escenarios controlados con dispositivos propios o autorizados.
- **hardware_required**: adaptador WiFi compatible con modo monitor/AP bajo VersionLock.
- **expected_evidence**: PCAP, lista de probes/respuestas, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.connectivity.wifi_pmkid`

- **description**: captura documental PMKID para auditoría WiFi autorizada.
- **hardware_required**: adaptador WiFi compatible y herramientas validadas por VersionLock.
- **expected_evidence**: captura PMKID, PCAP/hash material enmascarado si aplica, timeline y AuditLog.
- **risk_level**: alto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.connectivity.wifi_hotspot_bruteforce`

- **description**: fuerza bruta a hotspot propio o autorizado con límites, confirmación reforzada y parada segura.
- **hardware_required**: interfaz WiFi compatible y diccionario autorizado.
- **expected_evidence**: intento auditado, resultado, logs minimizados, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.connectivity.bt_sniffing`

- **description**: sniffing BLE/BT autorizado con dongle compatible y evidencia PCAP/data dump.
- **hardware_required**: dongle Bluetooth 5.3 CSR8510 o similar validado.
- **expected_evidence**: PCAP, data dump, metadatos de interfaz, timeline y AuditLog.
- **risk_level**: alto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.connectivity.bt_a2dp_spoof`

- **description**: spoofing A2DP de laboratorio para dispositivos propios o autorizados.
- **hardware_required**: dongle Bluetooth compatible y pila BlueZ validada.
- **expected_evidence**: logs de sesión, capturas del panel, timeline y AuditLog.
- **risk_level**: alto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.connectivity.bt_blueborne`

- **description**: evaluación BlueBorne documental y controlada para validar exposición sin afirmar explotación real.
- **hardware_required**: dongle Bluetooth compatible y entorno aislado.
- **expected_evidence**: hallazgo validado, versión/huella del objetivo, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.connectivity.bt_fuzzing`

- **description**: fuzzing BT 5.3 de laboratorio con límites, ventana temporal y parada segura.
- **hardware_required**: dongle Bluetooth 5.3 compatible.
- **expected_evidence**: caso de prueba, crash o no-crash, logs, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.connectivity.iot_scan`

- **description**: escaneo de APs IoT tipo isla, como bombillas, enchufes y cámaras dentro del scope.
- **hardware_required**: interfaz WiFi compatible o red autorizada.
- **expected_evidence**: dispositivos detectados, fingerprints, capturas del panel, timeline y AuditLog.
- **risk_level**: medio-alto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.connectivity.iot_attack`

- **description**: interacción controlada con portal web o API local de IoT autorizado, sin asumir explotación real.
- **hardware_required**: conectividad al AP/red IoT autorizado.
- **expected_evidence**: solicitud/respuesta minimizada, hallazgo, capturas del panel, timeline y AuditLog.
- **risk_level**: alto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.connectivity.nfc_clone`

- **description**: clonación NFC/RFID de laboratorio con lector ACR122U y tarjetas propias/autorizadas.
- **hardware_required**: lector ACR122U validado.
- **expected_evidence**: dump enmascarado, hash, cadena de custodia, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.connectivity.nfc_relay`

- **description**: relay NFC documental cuando existan dos lectores autorizados y entorno de laboratorio.
- **hardware_required**: dos lectores NFC/RFID autorizados.
- **expected_evidence**: transcripción minimizada, latencias, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Contrato JSON `connectivity_action`

Contrato JSON para una acción de conectividad. Es especificación documental, no endpoint ni schema implementado.

```json
{
  "type": "connectivity_action",
  "device_id": "dev-1234",
  "technique_id": "android.connectivity.bt_sniffing",
  "params": {
    "target_mac": "AA:BB:CC:DD:EE:FF",
    "duration_seconds": 60,
    "interface": "hci0"
  },
  "expected_evidence": ["pcap", "data_dump"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Campos obligatorios:

- `type`
- `device_id`
- `technique_id`
- `params`
- `expected_evidence`
- `scope`
- `operator`
- `requires_confirmation`

Reglas del contrato:

- `type` debe ser `connectivity_action`.
- `technique_id` debe pertenecer al catálogo `android.connectivity.*`.
- `scope` debe ser válido, explícito y auditable.
- `requires_confirmation` debe ser `true` para técnicas de riesgo alto o crítico.
- `params` debe mantenerse minimizado y redactado por defecto cuando contenga identificadores sensibles.
- EvidenceStore debe rechazar evidencia sin tipo esperado, hash, sesión, operador y timestamp cuando exista implementación futura.
- X5/OjoRouter debe bloquear acciones sin hardware requerido, VersionLock válido, Policy Engine favorable o Kill Switch armado.

### Flujo de trabajo asistido — Mistral + X5 + Hermes

El flujo asistido del Vector 9 describe cómo el panel debe guiar detección, selección, ejecución futura aprobada, intervención Hermes Agent y recuperación sin exponer comandos operativos ni asumir capacidades ya implementadas. Mistral/LaIA actúa como cerebro contextual, X5/OjoRouter valida y enruta bajo Policy Engine/Kill Switch/VersionLock, y Hermes Agent solo interviene en laboratorio cuando falta capacidad o compatibilidad. Cualquier worker, módulo o artefacto mencionado en esta sección es una referencia documental futura y permanece como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta revisión, sandbox, aprobación y promoción.

#### Detección y sugerencia inicial

Flujo esperado:

1. El usuario accede a **Android > Conectividad**.
2. El panel muestra el hardware disponible —Alfa, BT 5.3, HackRF, ACR122U— y su ubicación actual: Windows o Kali.
3. El usuario pulsa **Escanear dispositivos**.
4. Mistral ordena a X5 preparar y validar técnicas de escaneo WiFi, Bluetooth e IoT dentro del scope autorizado.
5. X5/OjoRouter valida hardware, ubicación, Policy Engine, Kill Switch, permisos, VersionLock y redacción de evidencia antes de cualquier ejecución futura aprobada.
6. Los dispositivos detectados aparecen en la tabla unificada del panel cuando exista implementación futura.
7. Mistral analiza los dispositivos y sugiere en el chat contextual hallazgos accionables, por ejemplo: **Se ha detectado un altavoz Bluetooth vulnerable a BlueBorne. ¿Deseas ejecutar el ataque?**.

La sugerencia de Mistral no autoriza ejecución. Debe mostrarse como recomendación revisable con técnica, riesgo, evidencia esperada, hardware requerido, estado de scope y confirmación necesaria.

#### Selección y ejecución de una técnica

Flujo esperado:

1. El usuario selecciona un dispositivo y una técnica desde la tabla o escribe una intención en lenguaje natural, por ejemplo: **Haz un Evil Twin con la red WiFi guardada de este móvil**.
2. Mistral selecciona la técnica correspondiente del catálogo `android.connectivity.*`.
3. Mistral rellena parámetros revisables como SSID, canal, interfaz, duración, dispositivo objetivo y evidencia esperada.
4. El panel muestra el plan JSON en una ventana modal antes de cualquier acción.
5. El usuario confirma o cancela.
6. X5 valida contra Policy Engine, Kill Switch, scope, permisos, VersionLock, hardware y ubicación Windows/Kali WSL2.
7. Si existe implementación futura aprobada, X5 enruta la técnica mediante un worker autorizado en Kali WSL2 cuando la técnica requiera ese entorno.
8. El panel muestra progreso en tiempo real mediante estados visuales y timeline.
9. Si la técnica requiere emisión —Evil Twin, BlueBorne, A2DP Spoofing u otra marcada como emisión— se solicita confirmación explícita adicional y aviso de responsabilidad antes de continuar.
10. EvidenceStore preserva PCAP, data dump, logs minimizados, capturas, hashes y AuditLog si la ejecución futura produce evidencia válida.

El plan JSON debe permanecer editable/revisable antes de confirmar. Ninguna selección de UI ni instrucción en lenguaje natural debe saltarse Policy Engine, Kill Switch, VersionLock, scope, confirmaciones o redacción por defecto.

#### Intervención de Hermes — Evolución del Arsenal

Hermes Agent puede intervenir solo si una técnica falla porque el dispositivo usa un protocolo no soportado, un chipset desconocido, una defensa no catalogada, un parser ausente o una incompatibilidad de evidencia. Esta intervención es de laboratorio, no autoejecuta producción y no crea capacidades reales en esta ronda.

Flujo esperado:

1. X5 notifica a Mistral que la técnica falló por compatibilidad, protocolo no soportado, chipset desconocido o defensa no catalogada.
2. Mistral sugiere al usuario: **Este dispositivo no responde a las técnicas disponibles. ¿Solicito a Hermes un módulo personalizado?**.
3. Si el usuario acepta, Mistral prepara una solicitud a Hermes con el perfil del dispositivo: MAC, tipo, versión de firmware, capturas de tráfico si existen, técnica fallida, error, hardware usado, VersionLock y evidencias parciales.
4. Hermes consulta fuentes abiertas como GitHub o Exploit-DB y documentación técnica autorizada para buscar PoC, referencias o compatibilidad aplicable.
5. Si encuentra información suficiente, Hermes propone artefactos de laboratorio como `technique.json`, `worker.py` y `evidence_schema.json`, pero estos nombres son contractuales/documentales y no se crean en esta ronda.
6. Hermes prueba la propuesta en sandbox cuando exista pipeline aprobado.
7. Si la prueba es exitosa, Hermes notifica: **Nuevo módulo para atacar este dispositivo listo para revisión**.
8. El usuario revisa la propuesta y, si la aprueba, la promociona al arsenal mediante el pipeline Research → Quarantine → Analyze → Build → Sandbox Test → Evidence → Review → Approval → Promotion.
9. Solo tras promoción, X5 puede reanudar el ataque original con la nueva técnica dentro de scope, Policy Engine y Kill Switch.
10. Si Hermes no encuentra información suficiente, lo comunica al usuario y sugiere aportar manualmente una PoC o un 0-day mediante el hook `IMPLEMENTACION_USUARIO_REQUERIDA`.

Hermes no decide promoción, no instala herramientas, no ejecuta contra objetivos reales y no sustituye aprobación humana. Cualquier módulo personalizado queda bloqueado hasta evidencia de sandbox, revisión y aprobación explícita.

### Preflight checklist obligatorio del Vector 9

Antes de ejecutar cualquier técnica de conectividad, el panel debe mostrar y bloquear según este checklist:

- [ ] Hardware requerido detectado y en la ubicación correcta: Kali WSL2 si es necesario.
- [ ] Dispositivo objetivo seleccionado y perfilado.
- [ ] Técnica seleccionada compatible con el hardware disponible.
- [ ] Kill Switch armado.
- [ ] Operador autorizado.
- [ ] Scope del laboratorio válido.
- [ ] Para técnicas de emisión —Evil Twin, BlueBorne, A2DP Spoofing— confirmación explícita del usuario y aviso de responsabilidad.
- [ ] VersionLock de herramientas verificado.

Si cualquier ítem falla:

- la técnica no se ejecuta;
- el botón de acción permanece desactivado;
- el estado pasa a `hardware_missing`, `blocked_by_policy` o `error` según corresponda;
- Mistral explica el motivo en lenguaje natural;
- AuditLog registra el bloqueo si hubo intento de ejecución.

### Errores y recuperación asistida del Vector 9

#### Hardware no disponible

- El panel muestra `hardware_missing`.
- La técnica no se ejecuta.
- Mistral sugiere: **Conecta el adaptador Alfa y pásalo a Kali WSL2 para habilitar esta técnica**.
- AuditLog registra el intento si el usuario intentó iniciar la técnica.

#### Técnica no compatible con el dispositivo

- X5 intenta ejecutar la técnica solo si preflight, Policy Engine, Kill Switch, VersionLock y confirmación lo permiten.
- Si falla con un error de compatibilidad, X5 notifica a Mistral.
- Mistral analiza el error y, si es un caso no cubierto, sugiere intervención de Hermes según el flujo de evolución del arsenal.
- Se preservan logs minimizados y evidencias parciales si existen.

#### Dispositivo se desconecta durante el ataque

- El panel marca el dispositivo como `disconnected`.
- Se guardan evidencias parciales.
- Si el ataque era automatizado, se pausa y se notifica al usuario.
- X5 evita reintentos automáticos fuera de Policy Engine, scope y confirmación.

#### Kill Switch activado

- Se detiene inmediatamente cualquier emisión o captura.
- Se guardan evidencias pendientes.
- El estado global cambia a `kill_switch_triggered`.
- AuditLog recibe registro prioritario.
- El panel exige revisión antes de reanudar cualquier técnica.

#### Policy bloquea la acción

- El estado cambia a `blocked_by_policy`.
- Se muestra el motivo del bloqueo.
- La técnica no se ejecuta.
- Mistral puede proponer alternativas permitidas por scope, pero no puede saltarse la decisión de Policy Engine.

### Preflight de conectividad

Antes de habilitar una técnica de conectividad, el panel debe validar:

- hardware requerido presente;
- ubicación correcta del hardware: Windows o Kali WSL2 según técnica;
- si requiere Kali WSL2, hardware pasado con `usbipd-win` y visible para la sesión;
- driver o stack nominal validado por VersionLock;
- interfaz seleccionada;
- dispositivo objetivo dentro del scope;
- operador autenticado y autorizado;
- Kill Switch armado;
- Policy Engine permite la acción;
- redacción de evidencia activa por defecto;
- confirmación explícita recibida cuando aplique.

Si cualquier ítem falla:

- botón de acción desactivado;
- estado `hardware_missing`, `blocked_by_policy` o `error`;
- LaIA/Mistral explica el motivo;
- AuditLog registra bloqueo si hubo intento de ejecución;
- el panel sugiere acción documental, por ejemplo **Pasar a Kali WSL2**, sin ejecutar comandos.

### Evidencias del Vector 9

Tipos de evidencia relevantes:

- PCAP;
- data dump;
- fingerprints WiFi/BT/IoT;
- capturas del panel;
- logs de herramienta minimizados;
- hashes SHA256;
- timeline JSON;
- AuditLog;
- reportes Hermes si faltó parser, wrapper o compatibilidad.

Reglas de evidencia:

- exportación enmascarada por defecto;
- identificadores sensibles como MAC, SSID privado, dumps NFC, tokens o material de hash se minimizan o enmascaran por defecto;
- exportación completa requiere confirmación reforzada, scope válido y AuditLog;
- cada archivo debe tener SHA256 antes de handoff o exportación;
- timeline JSON debe encadenar hashes cuando exista sesión con múltiples artefactos.

### Handoff con otros módulos

El Vector 9 no trabaja aislado. Sus evidencias, dispositivos detectados y hallazgos pueden enviarse a otros módulos mediante contratos auditados, redacción por defecto, confirmación cuando aplique, EvidenceStore y AuditLog.

#### Handoff con Módulo 10 — Wireless / RF general

- El Vector 9 comparte hardware con M10: HackRF, adaptador Alfa y dongle BT.
- Las evidencias de emisión, como PCAP y grabaciones IQ, se almacenan en el mismo EvidenceStore y respetan las políticas de metadatos de M10.
- Si se detecta un nuevo dispositivo RF durante el escaneo, se puede enviar su perfil a M10 para un análisis más profundo de espectro.
- Cualquier emisión RF o uso avanzado de HackRF mantiene `HARDWARE_REQUIRED`, `RF_TRANSMIT`, scope explícito, confirmación reforzada y `IMPLEMENTACION_USUARIO_REQUERIDA` hasta promoción.

#### Handoff con Módulo 6 — Red / MITM

- Si se captura tráfico de red, PCAP o data dump durante un ataque WiFi o Bluetooth, se puede enviar a M6 para inspección de protocolos y extracción de credenciales.
- Casos documentales:
  - tráfico de un dispositivo IoT;
  - handshake WiFi;
  - sesión BLE sniffada.
- M6 recibe evidencia, no acceso libre al dispositivo ni autorización automática para nuevas acciones.

#### Handoff con Módulo 5 — Credenciales y Autenticación

Si se capturan credenciales, portal cautivo, clave WiFi, tokens BLE o cualquier material de autenticación, el Vector 9 debe empaquetarlos como `credential_handoff` y enviarlos a M5.

Reglas:

- valores enmascarados por defecto;
- `source_module = "android"`;
- `source_vector = "connectivity"`;
- `source_evidence_id` obligatorio;
- M5 clasifica y decide acciones.

#### Handoff con Módulo 12 — Orquestación

Todas las acciones `android.connectivity.*` heredan el flujo M12:

- LaIA/Mistral genera el plan y rellena parámetros.
- X5 valida hardware, scope, Policy, Kill Switch, VersionLock y permisos.
- EvidenceStore guarda.
- AuditLog registra.
- Hermes se activa si falta parser, wrapper o técnica para un dispositivo concreto.

#### Handoff interno dentro del Módulo 13

- **Vector 3 Control Remoto**: si un dispositivo queda identificado y es controlable, se transfiere su `device_id` y estado al panel de control remoto.
- **Vector 5 Red Móvil / MITM**: si hay tráfico relay o PCAP, se envía para análisis más profundo.
- **Vector 6 Análisis de Apps**: si se detecta una APK o perfil durante la interacción con un dispositivo IoT, se transfiere al Vector 6.

### Contrato JSON `connectivity_handoff`

Contrato documental para enviar evidencias, dispositivos detectados o hallazgos del Vector 9 a otros módulos. No representa endpoint ni schema implementado.

```json
{
  "type": "connectivity_handoff",
  "source_module": "android",
  "source_vector": "M13_V9",
  "session_id": "sess-7890",
  "device_id": "dev-1234",
  "evidence_ids": ["ev-001", "ev-002"],
  "target_module": "M6",
  "handoff_reason": "pcap_analysis",
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

### Scoring X5 del Vector 9

Reglas:

- Solo puntúa si hay evidencia válida: PCAP, credenciales, informe de vulnerabilidad o clonación exitosa.
- `hardware_missing` no penaliza la técnica.
- `blocked_by_policy` no penaliza la técnica.
- Un ataque exitoso a un dispositivo IoT sube el score de `android.connectivity.iot_attack`.
- Una clonación NFC exitosa sube el score de `android.connectivity.nfc_clone`.
- Evidencia corrupta, ausente o fuera de scope no sube score.
- Técnicas en estado `IMPLEMENTACION_USUARIO_REQUERIDA` no puntúan hasta promoción.

Campos recomendados:

- `technique_id`
- `session_id`
- `device_id`
- `evidence_valid`
- `blocked_by_policy`
- `hardware_available`
- `score_before`
- `score_after`
- `score_delta`
- `operator`

### Preparación para Módulo 16 — Evidencia / Ops / Calidad

Todas las evidencias del Vector 9 deben cumplir:

- SHA256 de cada archivo de evidencia.
- Hashes encadenados en `timeline_json`.
- Cadena de custodia interna: acceso, revelado, exportación y operador.
- Exportación enmascarada por defecto.
- Metadatos: `session_id`, `device_id`, `technique_id`, `scope`, `operator`, VersionLock.
- Integridad verificable antes de handoff o exportación.
- Informes compatibles con compilador final de M16.

Tipos de evidencia relevantes:

- PCAP WiFi;
- PCAP Bluetooth;
- grabaciones IQ si aplica;
- credenciales capturadas;
- informes de dispositivos IoT;
- capturas del panel;
- AuditLog.

### Cierre seguro del Vector 9

Cierre seguro:

- detener escaneos, sesiones, capturas y buffers cuando exista implementación futura;
- detener cualquier emisión activa si aplica;
- guardar evidencias pendientes;
- calcular hashes;
- actualizar `timeline_json` y AuditLog;
- liberar hardware si procede;
- dejar estado final `success`, `error`, `blocked_by_policy`, `kill_switch_triggered` o `hardware_missing` según corresponda;
- marcar `cleanup_required` si quedan recursos abiertos.

### Criterios de aceptación del Vector 9

Vector 9 queda documentalmente cerrado si `docs/techniques/13_ANDROID.md` contiene:

- [ ] Propósito del Vector 9 documentado.
- [ ] Herramientas nominales y VersionLock documentados.
- [ ] Compatibilidad hardware Windows/Kali documentada (`usbipd-win`).
- [ ] Panel **Android > Conectividad** documentado con sus subpáginas.
- [ ] Estados visuales documentados.
- [ ] Técnicas `android.connectivity.*` documentadas con sus `technique_id`.
- [ ] Contrato `connectivity_action` documentado.
- [ ] Contrato `connectivity_handoff` documentado.
- [ ] Flujo de trabajo asistido (Mistral + X5 + Hermes) documentado.
- [ ] Preflight checklist documentado.
- [ ] Errores y recuperación documentados.
- [ ] Handoffs con M10, M6, M5, M12 y M13 interno documentados.
- [ ] Scoring X5 documentado.
- [ ] Preparación para M16 documentada.
- [ ] Confirmaciones explícitas para técnicas de emisión documentadas.
- [ ] No se afirma implementación real de emisión o interceptación.

### Pantallas de trabajo específicas por herramienta del Vector 9

Las siguientes pantallas de trabajo definen la UI documental esperada para cada técnica/herramienta del Vector 9 dentro de **Android > Conectividad**. No implementan código, no crean scripts, no añaden endpoints, no ejecutan workers y no afirman soporte funcional. Cada botón descrito debe entenderse como disparador de un plan revisable Mistral/LaIA → X5/OjoRouter → Policy Engine/Kill Switch/VersionLock → EvidenceStore/AuditLog cuando exista implementación futura aprobada. Toda acción sensible permanece como `IMPLEMENTACION_USUARIO_REQUERIDA`, con `HARDWARE_REQUIRED` y `RF_TRANSMIT` cuando aplique.

#### Evil Twin WiFi

- **Sección**: **Ataques WiFi > Evil Twin**.
- **Campo `SSID a suplantar`**: autocompletado por Mistral al seleccionar un dispositivo de la tabla; permite escritura manual por el operador.
- **Campo `Interfaz`**: autocompletado, por ejemplo `wlan0`, si VersionLock y el visor de hardware confirman disponibilidad.
- **Campo `Canal`**: sugerido por Mistral a partir del perfil del objetivo y del escaneo autorizado.
- **Checkbox `Servir portal cautivo`**: si se activa, aparece un campo para pegar el HTML del portal o seleccionar plantilla: Google, Facebook o genérico.
- **Botón `Iniciar Evil Twin`**: lanza el plan revisable; antes de cualquier ejecución futura requiere scope válido, confirmación explícita de emisión, Kill Switch armado, Policy Engine favorable, hardware compatible y VersionLock.
- **Visor activo**: mientras el plan esté activo en una implementación futura, muestra dispositivos conectados al AP falso y credenciales capturadas en tiempo real con redacción por defecto.
- **Botón `Detener`**: apaga el AP falso cuando exista implementación futura, guarda evidencias pendientes, actualiza `timeline_json` y registra AuditLog.

#### KARMA Attack

- **Sección**: **Ataques WiFi > KARMA**.
- **Parámetros**: Mistral activa documentalmente el modo KARMA en Bettercap dentro del plan; no requiere parámetros adicionales del usuario.
- **Visor en tiempo real**: muestra los SSID solicitados por los dispositivos y cuáles han sido suplantados cuando exista implementación futura.
- **Tabla de dispositivos conectados**: muestra IP, MAC y tráfico cursado con minimización/redacción por defecto.
- **Controles**: iniciar/detener quedan sujetos a confirmación explícita si existe emisión, Policy Engine, Kill Switch, VersionLock y EvidenceStore.

#### PMKID Attack

- **Sección**: **Ataques WiFi > PMKID**.
- **Campo `Interfaz`**: autocompletado desde el visor de hardware.
- **Campo `BSSID objetivo`**: opcional; si queda vacío, el plan documenta captura de todos los PMKID disponibles dentro del scope.
- **Botón `Capturar PMKID`**: prepara un plan para captura mediante herramientas nominales validadas por VersionLock; el visor muestra PMKID capturados en tiempo real cuando exista implementación futura.
- **Botón `Enviar a Hashcat`**: una vez capturados, envía el material al Módulo 5 para cracking offline mediante handoff auditado y redacción por defecto.
- **Progreso de cracking**: muestra estado devuelto por M5 sin exponer material sensible salvo confirmación reforzada y AuditLog.

#### Fuerza Bruta a Hotspot Móvil

- **Sección**: **Ataques WiFi > Hotspot**.
- **Campo `BSSID`**: autocompletado al seleccionar un hotspot de la tabla.
- **Campo `Diccionario`**: desplegable con opciones `rockyou.txt`, `generado por IA` y `personalizado`.
- **Diccionario `generado por IA`**: Mistral crea una propuesta contextual revisable, sujeta a scope y política de credenciales.
- **Botón `Iniciar ataque`**: prepara el plan para herramienta nominal validada por VersionLock; requiere confirmación reforzada, límites, parada segura y aprobación de Policy Engine.
- **Visor de progreso**: muestra progreso y contraseña encontrada solo con redacción por defecto; revelado completo requiere confirmación reforzada y AuditLog.

#### Sniffing BLE

- **Sección**: **Ataques Bluetooth > Sniffing BLE**.
- **Campo `Dispositivo objetivo (MAC)`**: autocompletado al seleccionar un dispositivo de la tabla.
- **Campo `Duración (segundos)`**: valor por defecto `60`, editable por el operador dentro de límites de Policy Engine.
- **Botón `Iniciar captura`**: prepara el plan para captura BLE con bleak y Wireshark/tshark como herramientas nominales bajo VersionLock.
- **Visor de paquetes BLE**: muestra paquetes BLE en tiempo real cuando exista implementación futura, con minimización de identificadores.
- **Finalización**: al terminar, el PCAP se guarda en Evidencias y el panel ofrece enviar a M6 para análisis mediante `connectivity_handoff`.

#### A2DP Spoofing — Inyección de Audio

- **Sección**: **Ataques Bluetooth > A2DP Spoofing**.
- **Requisito**: HackRF detectado y validado; si falta, estado `hardware_missing`.
- **Campo `Dispositivo objetivo (MAC)`**: autocompletado desde la tabla.
- **Campo `Archivo de audio a emitir`**: selector de archivos WAV o MP3.
- **Botón `Emitir audio`**: prepara el plan de emisión con gr-bluetooth y HackRF como herramientas nominales; requiere confirmación explícita adicional, aviso de responsabilidad, `RF_TRANSMIT`, Policy Engine favorable y Kill Switch armado.
- **Visor de progreso**: muestra estado de emisión cuando exista implementación futura.
- **Botón `Detener`**: detiene emisión futura, guarda evidencias y actualiza AuditLog.
- **Evidencia**: confirmación de emisión, archivo de audio utilizado, hashes, timeline y AuditLog.

#### BlueBorne

- **Sección**: **Ataques Bluetooth > BlueBorne**.
- **Requisito**: HackRF detectado y validado si la técnica lo requiere; si falta, estado `hardware_missing`.
- **Campo `Dispositivo objetivo (MAC)`**: autocompletado desde la tabla.
- **Verificación Mistral**: Mistral verifica si el dispositivo parece vulnerable mediante fingerprinting documental y evidencia disponible.
- **Escaneo previo**: si la vulnerabilidad no está clara, el panel ofrece ejecutar un escaneo previo con nmap y scripts nominales bajo VersionLock, scope, confirmación y Policy Engine.
- **Botón `Ejecutar BlueBorne`**: lanza un plan revisable; no implica explotación real en esta ronda y requiere confirmación explícita reforzada.
- **Resultado**: muestra éxito con shell o fallo cuando exista implementación futura aprobada; cualquier sesión resultante queda bajo EvidenceStore, AuditLog, Kill Switch y Policy Engine.
- **Handoff**: si tiene éxito, se ofrece handoff a Vector 3 — Control Remoto con `device_id`, estado y evidencias.

#### Fuzzing Bluetooth 5.3

- **Sección**: **Ataques Bluetooth > Fuzzing**.
- **Campo `Dispositivo objetivo (MAC)`**: autocompletado desde la tabla.
- **Campo `Perfil de fuzzing`**: desplegable con `L2CAP`, `GATT`, `SMP` y `automático`.
- **Modo `automático`**: Mistral selecciona el perfil según el dispositivo, fingerprint, servicios y compatibilidad.
- **Botón `Iniciar fuzzing`**: prepara un plan para scripts Python con bleak como capacidad nominal; los scripts reales quedan `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Visor**: muestra paquetes enviados y respuestas cuando exista implementación futura, con límites, ventana temporal y parada segura.
- **Crash detectado**: si se detecta un crash, se notifica al usuario, se guardan evidencias, hashes, timeline y AuditLog.

#### Escaneo de IoT — AP Isla

- **Sección**: **Dispositivos IoT**.
- **Botón `Escanear redes IoT`**: prepara un plan para nmap y scripts NSE nominales bajo VersionLock para buscar APs de dispositivos IoT como bombillas, enchufes y cámaras.
- **Tabla de resultados**: muestra SSID, fabricante por OUI y servicios expuestos.
- **Selección de dispositivo**: al seleccionar uno, se abre su pantalla de ataque específica **Dispositivos IoT > [Nombre del dispositivo]**.
- **Evidencia**: fingerprints, capturas del panel, timeline, hashes y AuditLog.

#### Ataque a Dispositivo IoT

- **Sección**: **Dispositivos IoT > [Nombre del dispositivo]**.
- **Campo `URL del panel / API`**: autocompletado por Mistral a partir del fingerprint y servicios expuestos.
- **Si tiene panel web**: botones `Fuerza bruta (Hydra)` y `Buscar exploits (Metasploit)` como acciones documentales sujetas a confirmación, scope, Policy Engine y VersionLock.
- **Si tiene API local**: campo `Comando a enviar` y botón `Enviar`.
- **Comandos de ejemplo**: Mistral puede generar propuestas revisables como encender/apagar o cambiar configuración, sin ejecutar nada automáticamente.
- **Visor de respuesta**: muestra respuesta del dispositivo cuando exista implementación futura, con redacción de secretos y registro de evidencias.
- **Handoff**: si se detecta APK, perfil, endpoint, secreto o tráfico relevante, se ofrece handoff a Vector 6, M5 o M6 según corresponda.

#### Clonación NFC

- **Sección**: **NFC/RFID > Clonación**.
- **Requisito**: ACR122U detectado; si falta, estado `hardware_missing`.
- **Botón `Leer tarjeta`**: prepara el plan para mfoc/mfcuk como herramientas nominales bajo VersionLock.
- **Visor de lectura**: muestra UID y sectores leídos cuando exista implementación futura; dumps sensibles se enmascaran por defecto.
- **Botón `Clonar en tarjeta virgen`**: se habilita si la lectura es exitosa; el usuario coloca una tarjeta virgen y confirma explícitamente.
- **Evidencia**: volcado de la tarjeta original, hash, cadena de custodia, confirmación de clonación, timeline y AuditLog.

#### Relay NFC

- **Sección**: **NFC/RFID > Relay**.
- **Requisito**: dos lectores ACR122U detectados y validados; si falta alguno, estado `hardware_missing`.
- **Estado de lectores**: el panel muestra el estado de ambos lectores, ubicación Windows/Kali si aplica y VersionLock.
- **Botón `Iniciar relay`**: prepara un plan de relay; cualquier script real queda `IMPLEMENTACION_USUARIO_REQUERIDA` y requiere confirmación reforzada, scope, Policy Engine y Kill Switch.
- **Visor de tráfico retransmitido**: muestra tráfico en tiempo real cuando exista implementación futura, con minimización y redacción.
- **Cierre**: detener relay, guardar evidencias, hashes, timeline y AuditLog.

### Handoff interno ampliado dentro del Módulo 13

El Vector 9 puede enviar hallazgos a otros vectores del propio Módulo Android para continuar la auditoría de forma encadenada. Estos handoffs internos no conceden ejecución automática: cada continuidad debe pasar por plan revisable de Mistral/LaIA, validación de X5/OjoRouter, Policy Engine, Kill Switch, VersionLock, EvidenceStore y AuditLog.

#### Handoff al Vector 3 — Control Remoto

Si durante un ataque de conectividad se obtiene acceso a un dispositivo —por ejemplo shell BlueBorne, control de IoT, panel web o API local— se transfiere al Vector 3:

- `device_id` del dispositivo controlado;
- `session_id` activa;
- tipo de acceso conseguido: shell, API o panel web;
- evidencias generadas durante la técnica de conectividad.

El usuario puede abrir directamente el panel de **Control Remoto** desde un botón en la pantalla de la técnica. Ese botón solo prepara el handoff y la apertura contextual; no autoriza acciones remotas sin confirmación, scope, Policy Engine, Kill Switch y AuditLog.

#### Handoff al Vector 5 — Red Móvil / MITM

Si se captura tráfico de red —PCAP de WiFi, Bluetooth o IoT— que requiere análisis profundo o relay, se envía al Vector 5:

- `evidence_ids` con los archivos PCAP;
- `device_id` del dispositivo origen del tráfico;
- `handoff_reason`: `deep_traffic_analysis`.

El Vector 5 puede aplicar sus técnicas de MITM para inspeccionar credenciales, cookies o tokens presentes en el tráfico, siempre bajo redacción por defecto, scope autorizado, confirmación cuando aplique, EvidenceStore y AuditLog.

#### Handoff al Vector 6 — Análisis de Apps

Si durante la interacción con un dispositivo IoT o Bluetooth se detecta una APK, un perfil de configuración o un payload, se envía al Vector 6:

- `evidence_ids` con el archivo APK, perfil o payload;
- `device_id` del dispositivo donde se encontró;
- `handoff_reason`: `app_discovered`.

El Vector 6 puede descompilar la APK, buscar secretos y analizar componentes exportados dentro de su propio flujo documental, con redacción por defecto y sin asumir ejecución automática de nuevas acciones.

### Nota final del Vector 9

El Vector 9 queda completamente cerrado como especificación documental de producto/laboratorio de conectividad Android. Esta documentación no crea lógica funcional ni afirma ejecución real de WiFi, Bluetooth, IoT, NFC/RFID o RF. Las partes sensibles permanecen marcadas como:

- `IMPLEMENTACION_USUARIO_REQUERIDA`
- `HARDWARE_REQUIRED`
- `RF_TRANSMIT` cuando aplique

### Reglas finales del Vector 9

No implementar código. No crear endpoints. No crear workers. No modificar base de datos. No crear tests. No añadir requirements. No crear scripts funcionales. No instalar herramientas. No añadir comandos operativos. No afirmar soporte funcional de conectividad ofensiva. Mantener el Vector 9 como documentación exacta de producto/laboratorio, panel, hardware, VersionLock, estados, técnicas registradas, contrato JSON, evidencia, handoff, scoring, cierre seguro, LaIA/X5/Hermes Agent, EvidenceStore, AuditLog, Policy Engine y Kill Switch.

## Vector 10 — Carteras de Criptomonedas y Apps Financieras

El Vector 10 define **Carteras de Criptomonedas y Apps Financieras** como especificación documental de producto/laboratorio para auditorías Android autorizadas sobre aplicaciones financieras, wallets, apps de intercambio y componentes relacionados. Esta sección no implementa código, endpoints, workers, base de datos, tests, requirements, scripts funcionales ni comandos operativos. Ninguna descripción afirma extracción real, hooking real, overlays reales, interceptación real de portapapeles, manipulación real de transacciones ni acceso real a secretos.

Toda capacidad sensible del Vector 10 permanece marcada como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta implementación futura aprobada, sandbox, revisión, autorización explícita, scope válido, Policy Engine favorable, Kill Switch armado, VersionLock, EvidenceStore y AuditLog. Cualquier hallazgo sensible —frase semilla, clave privada, token, dirección, credencial, archivo de wallet o evidencia financiera— debe estar enmascarado por defecto, protegido por cadena de custodia y gestionado mediante contratos auditados.

### Herramientas y versiones nominales — Kali WSL2

Las herramientas siguientes se documentan como inventario nominal de laboratorio para VersionLock. No se instalan ni ejecutan en esta ronda. Las referencias de instalación indicadas quedan como metadatos documentales de origen, no como instrucciones operativas que el panel pueda ejecutar.

- **adb 34.0.5**: referencia documental `sudo apt install adb`; uso previsto: extracción autorizada de archivos del dispositivo cuando exista permiso, root o ADB con permisos.
- **Frida 16.5**: referencia documental `pip install frida-tools`; uso previsto: hooking autorizado y volcado de memoria en laboratorio.
- **objection 1.13**: referencia documental `pip install objection`; uso previsto: automatización de tareas Frida dentro de laboratorio.
- **apktool 2.9.3**: referencia documental `sudo apt install apktool`; uso previsto: descompilación autorizada de APKs.
- **jadx 1.5.2**: referencia documental `sudo apt install jadx`; uso previsto: análisis estático de código.
- **Python 3.12**: preinstalado en Kali; librerías nominales `frida`, `requests`, `bip39-utils` con referencia documental `pip install frida requests bip39-utils`.
- **Dolphin Mistral Nemo 12B (LaIA)**: genera planes, scripts Frida documentales, overlays revisables y payloads personalizados de laboratorio, sin ejecución automática.
- **Hermes (DeepSeek API)**: crea propuestas de módulos para nuevas apps o protecciones no catalogadas, siempre en laboratorio y bajo pipeline de revisión/promoción.

VersionLock debe registrar versión detectada, origen, compatibilidad, ubicación Kali WSL2, permisos requeridos, decisión de uso, operador, timestamp y motivo. Si VersionLock no valida una herramienta, el panel debe bloquear la técnica y mostrar el motivo.

### Panel de control **Android > Carteras**

Dentro de **Android > Carteras**, el Vector 10 define una sección específica para detección, análisis, acciones revisables, evidencia, historial y evolución Hermes. Ninguna subpágina ejecuta acciones por sí misma: Mistral/LaIA propone, X5/OjoRouter valida, Policy Engine decide, Kill Switch puede detener, VersionLock bloquea incompatibilidades y EvidenceStore/AuditLog preservan evidencias si existe implementación futura aprobada.

Subpáginas documentadas:

- **Detección de Apps**: tabla con apps financieras detectadas por nombre de paquete e iconos. Mistral identifica automáticamente candidatas al escanear el dispositivo autorizado.
- **Extracción de Archivos**: pantalla para extraer directorios de datos de la app seleccionada; requiere root o ADB con permisos, scope explícito y confirmación.
- **Volcado de Memoria**: pantalla para enganchar Frida al proceso de la app y buscar patrones BIP39 en RAM dentro de laboratorio autorizado.
- **Overlay Attack**: pantalla para diseñar y desplegar una ventana falsa idéntica a la app objetivo como prueba controlada de resiliencia anti-phishing/anti-overlay.
- **Interceptación de Portapapeles**: pantalla para capturar y modificar contenido del portapapeles en tiempo real dentro de laboratorio autorizado.
- **Manipulación de Transacciones**: pantalla para modificar direcciones de envío antes de la firma en un entorno controlado, sin afirmar ejecución real.
- **Evidencias**: hallazgos enmascarados, archivos extraídos, dumps, capturas, hashes, timeline y reportes.
- **Historial/AuditLog**: confirmaciones, bloqueos, accesos, revelados, exportaciones, operador y timestamps.
- **Hermes Agent Lab**: propuestas para nuevas apps, protecciones no catalogadas, parsers, schemas, hooks o módulos de laboratorio.

### Pantallas de trabajo por técnica

#### Extracción de Archivos

- **Campo `App seleccionada`**: autocompletado por Mistral al seleccionar una app de la tabla de detección.
- **Campo `Ruta de extracción`**: autocompletado con la ruta base de la app, por ejemplo `/data/data/<paquete>/`; permite añadir subrutas manualmente.
- **Botón `Extraer`**: prepara un plan revisable para extracción mediante ADB o root autorizados; no ejecuta nada sin confirmación, Policy Engine, Kill Switch, VersionLock y permisos.
- **Progreso**: muestra estado y lista de archivos extraídos cuando exista implementación futura.
- **Visor de archivos**: permite descargar individualmente o buscar patrones de frases semilla BIP39 en texto plano usando regex en un flujo futuro aprobado; todo resultado sensible queda enmascarado por defecto.
- **Evidencia esperada**: listado de archivos, hashes, rutas, metadatos, coincidencias enmascaradas, timeline y AuditLog.

#### Volcado de Memoria RAM

- **Campo `App seleccionada`**: autocompletado desde la tabla de detección.
- **Campo `Script Frida`**: desplegable con opciones `Buscar BIP39`, `Capturar clave privada` y `Personalizado`.
- **Modo `Personalizado`**: habilita un editor de código documental para revisión humana; cualquier script real queda `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Botón `Iniciar volcado`**: prepara un plan Frida para buscar patrones en memoria; no afirma ejecución real en esta ronda.
- **Resultados en tiempo real**: muestra frases semilla o claves privadas solo como hallazgos enmascarados por defecto; revelado completo requiere confirmación reforzada, scope, AuditLog y cadena de custodia.
- **Botón `Exportar`**: guarda hallazgos en Evidencias y ofrece handoff a Módulo 5 — Credenciales mediante contrato auditado.

#### Overlay Attack — Ventana Falsa

- **Campo `App a suplantar`**: autocompletado por Mistral.
- **Campo `Plantilla de overlay`**: desplegable con plantillas generadas por Mistral para apps comunes como Trust Wallet, MetaMask y Binance; permite subir HTML/CSS personalizado.
- **Botón `Previsualizar`**: muestra el overlay en emulador o sobre una captura del dispositivo, sin desplegarlo.
- **Botón `Desplegar overlay`**: prepara un plan de despliegue que requiere accesibilidad activa, confirmación explícita reforzada, Policy Engine favorable, Kill Switch armado y `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Activación documental**: el overlay se activa cuando el usuario abre la app real solo en una implementación futura aprobada.
- **Credenciales capturadas**: se muestran en tiempo real únicamente enmascaradas por defecto y se gestionan mediante handoff a M5 si procede.

#### Interceptación de Portapapeles

- **Campo `App objetivo`**: opcional; si se deja vacío, el plan documenta interceptación de todo el sistema dentro del scope autorizado.
- **Botón `Iniciar interceptación`**: prepara un plan Frida para enganchar `ClipboardManager`; no ejecuta scripts reales en esta ronda.
- **Visor de contenido**: muestra contenido capturado en tiempo real cuando exista implementación futura, con redacción por defecto.
- **Botón `Modificar portapapeles`**: permite introducir un texto que reemplazaría contenido copiado, por ejemplo una dirección de wallet de laboratorio; requiere confirmación reforzada y no se ejecuta automáticamente.
- **Evidencia esperada**: contenido original enmascarado, contenido reemplazado enmascarado, timestamps, paquete objetivo, hashes, timeline y AuditLog.

#### Manipulación de Transacciones

- **Campo `App objetivo`**: autocompletado por Mistral.
- **Campo `Dirección de destino falsa`**: campo de texto para introducir una dirección de wallet de laboratorio.
- **Botón `Inyectar hook`**: prepara un plan Frida para modificar una función de envío de transacciones como `sendTransaction`; no afirma hook real.
- **Confirmación**: requiere scope explícito, confirmación reforzada, Policy Engine, Kill Switch, VersionLock y `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Panel de monitorización**: cuando exista implementación futura, muestra dirección original y dirección modificada enmascaradas por defecto.
- **Evidencia esperada**: confirmación de hook, comparación original/modificada enmascarada, app objetivo, timestamps, timeline y AuditLog.

### Técnicas registradas `android.crypto.*`

Las técnicas del Vector 10 quedan registradas como catálogo documental. Todas requieren scope autorizado, confirmación cuando aplique, VersionLock, Policy Engine, Kill Switch, EvidenceStore, AuditLog y `IMPLEMENTACION_USUARIO_REQUERIDA` hasta promoción.

#### `android.crypto.extract_files`

- **description**: extracción autorizada de archivos de la app financiera seleccionada.
- **required_inputs**: `device_id`, `package_name`, ruta, permisos/root/ADB, scope, operador y confirmación.
- **expected_evidence**: archivos extraídos, hashes SHA256, rutas, coincidencias enmascaradas, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.crypto.dump_memory`

- **description**: volcado de memoria RAM con Frida para buscar patrones sensibles como BIP39 en laboratorio autorizado.
- **required_inputs**: `device_id`, `package_name`, script seleccionado, timeout, scope, operador y confirmación reforzada.
- **expected_evidence**: hallazgos enmascarados, dump referenciado, hashes, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.crypto.overlay_attack`

- **description**: despliegue documental de overlay falso para evaluación anti-overlay/anti-phishing de apps financieras autorizadas.
- **required_inputs**: `device_id`, `package_name`, plantilla, accesibilidad activa, scope, operador y confirmación reforzada.
- **expected_evidence**: plantilla, capturas, hallazgos enmascarados, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.crypto.clipboard_intercept`

- **description**: interceptación y modificación documental del portapapeles para evaluar controles de apps financieras.
- **required_inputs**: `device_id`, paquete objetivo opcional, texto de reemplazo si aplica, scope, operador y confirmación reforzada.
- **expected_evidence**: eventos enmascarados, valores reemplazados enmascarados, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.crypto.transaction_manipulation`

- **description**: manipulación documental de direcciones de transacción antes de la firma en laboratorio autorizado.
- **required_inputs**: `device_id`, `package_name`, dirección destino de laboratorio, función objetivo, scope, operador y confirmación reforzada.
- **expected_evidence**: dirección original/modificada enmascarada, confirmación de hook, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Contrato JSON `crypto_action`

Contrato JSON para una acción de cartera. Es especificación documental, no endpoint ni schema implementado.

```json
{
  "type": "crypto_action",
  "device_id": "dev-1234",
  "technique_id": "android.crypto.dump_memory",
  "params": {
    "package_name": "com.trustapp.wallet",
    "script": "bip39_search",
    "timeout_seconds": 60
  },
  "expected_evidence": ["seed_phrase", "private_key"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Campos obligatorios:

- `type`
- `device_id`
- `technique_id`
- `params`
- `expected_evidence`
- `scope`
- `operator`
- `requires_confirmation`

Reglas del contrato:

- `type` debe ser `crypto_action`.
- `technique_id` debe pertenecer al catálogo `android.crypto.*`.
- `scope` debe ser explícito, autorizado y auditable.
- `requires_confirmation` debe ser `true` para todas las técnicas del Vector 10.
- `params` debe estar minimizado y redactado por defecto cuando incluya identificadores, direcciones, scripts o rutas sensibles.
- EvidenceStore debe rechazar hallazgos sin hash, técnica, operador, timestamp, redacción y cadena de custodia cuando exista implementación futura.
- X5/OjoRouter debe bloquear acciones sin permisos/root/ADB, VersionLock válido, Policy Engine favorable o Kill Switch armado.

### Flujo de trabajo asistido — Mistral + X5 + Hermes

El flujo asistido del Vector 10 describe cómo el panel **Android > Carteras** debe guiar detección, selección, validación, ejecución futura aprobada, recuperación y evolución Hermes para apps financieras y carteras. Mistral/LaIA actúa como cerebro contextual, X5/OjoRouter valida y enruta bajo Policy Engine, Kill Switch y VersionLock, y Hermes Agent solo interviene en laboratorio cuando falta soporte para una app, esquema de cifrado o protección. Cualquier worker, script Frida, overlay, bypass, técnica de extracción o módulo mencionado es referencia documental futura y permanece como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta sandbox, revisión, aprobación y promoción.

#### Detección y sugerencia inicial

Flujo esperado:

1. El usuario accede a **Android > Carteras**.
2. El panel muestra automáticamente las apps financieras detectadas en el dispositivo por nombre de paquete e icono.
3. Mistral identifica previamente esas apps mediante un escaneo documental con `adb shell pm list packages` y una base de datos local de paquetes conocidos de carteras, banca y exchanges. Esta referencia no implica que se ejecute el comando en esta ronda.
4. Mistral cruza nombre de paquete, versión si está disponible, permisos, estado ADB/root/accesibilidad y evidencias previas.
5. Mistral sugiere en el chat contextual: **Se han detectado 3 apps financieras. Trust Wallet es la más vulnerable a extracción de archivos. ¿Deseas proceder?**.
6. La sugerencia muestra técnica propuesta, riesgo, permisos requeridos, evidencia esperada, redacción por defecto, necesidad de confirmación y controles de parada.

La sugerencia de Mistral no autoriza ejecución. El usuario debe seleccionar o confirmar una acción, y X5/OjoRouter debe validar scope, Policy Engine, Kill Switch, permisos, VersionLock y EvidenceStore antes de cualquier ejecución futura aprobada.

#### Ejecución de una técnica

Flujo esperado:

1. El usuario selecciona una app y una técnica desde el panel, o escribe una intención en lenguaje natural, por ejemplo: **Extrae la frase semilla de Trust Wallet**.
2. Mistral analiza permisos disponibles: root, accesibilidad activa, ADB, C2 o control remoto según el dispositivo.
3. Mistral selecciona la técnica más adecuada del catálogo `android.crypto.*`.
4. Mistral rellena el contrato JSON `crypto_action` con parámetros como `package_name`, `script`, `timeout_seconds`, evidencia esperada, scope, operador y `requires_confirmation`.
5. El panel muestra el plan en una ventana modal revisable, con riesgos, redacción, evidencia prevista, permisos requeridos y criterios de parada.
6. El usuario confirma o cancela.
7. X5 valida contra Policy Engine, Kill Switch, scope, permisos, VersionLock, estado del dispositivo, redacción y EvidenceStore.
8. Si existe implementación futura aprobada, X5 enruta la técnica mediante un worker autorizado en Kali WSL2 para capacidades como ADB, Frida u objection.
9. El panel muestra progreso en tiempo real mediante estados visuales, timeline y AuditLog.
10. Si la técnica implica overlay o manipulación de transacciones, se solicita confirmación explícita adicional y aviso de responsabilidad antes de continuar.
11. Los hallazgos sensibles se muestran enmascarados por defecto. Revelar valores completos requiere confirmación reforzada, scope válido, cadena de custodia y AuditLog.

Ninguna instrucción en lenguaje natural puede saltarse permisos, Policy Engine, Kill Switch, VersionLock, confirmaciones reforzadas ni redacción por defecto.

#### Intervención de Hermes — Evolución del Arsenal

Hermes Agent puede intervenir cuando una técnica falla porque la app cambió su esquema de cifrado, usa un nuevo mecanismo de protección, detecta Frida/objection, no está en la base de datos de paquetes o requiere un parser/schema no catalogado.

Flujo esperado:

1. X5 notifica a Mistral que la técnica falló por app no soportada, cifrado nuevo, protección no catalogada, detección de Frida, parser faltante o error de compatibilidad.
2. Mistral sugiere al usuario: **Esta app no responde a las técnicas disponibles. ¿Solicito a Hermes un módulo personalizado?**.
3. Si el usuario acepta, Mistral envía a Hermes una solicitud con el perfil de la app: nombre de paquete, versión, permisos, técnica fallida, error, archivos extraídos si los hay, capturas, fingerprints y metadatos de VersionLock.
4. Hermes busca en fuentes abiertas como GitHub, foros de seguridad y documentación técnica autorizada una PoC, referencia, bypass, parser o documentación aplicable.
5. Si encuentra información suficiente, Hermes propone un módulo de laboratorio como script Frida, técnica de extracción, overlay personalizado, parser o `evidence_schema`.
6. Hermes prueba la propuesta en sandbox cuando exista pipeline aprobado.
7. Si la prueba es exitosa, Hermes notifica al usuario: **Nuevo módulo para Trust Wallet v8.0 listo para revisión**.
8. El usuario revisa la propuesta y, si la aprueba, la promociona al arsenal mediante el pipeline Research → Quarantine → Analyze → Build → Sandbox Test → Evidence → Review → Approval → Promotion.
9. Solo tras promoción, X5 puede reanudar el ataque original con la nueva técnica dentro del scope, Policy Engine, Kill Switch, VersionLock y EvidenceStore.
10. Si Hermes no encuentra información suficiente, lo comunica y sugiere aportar manualmente una PoC o 0-day mediante el hook `IMPLEMENTACION_USUARIO_REQUERIDA`.

Hermes no autoaprueba, no instala herramientas, no ejecuta contra objetivos reales y no sustituye revisión humana. Todo módulo personalizado permanece bloqueado hasta evidencia de sandbox y aprobación explícita.

### Preflight checklist obligatorio del Vector 10

Antes de ejecutar cualquier técnica del Vector 10, el panel debe mostrar y bloquear según este checklist:

- [ ] Dispositivo conectado y accesible: ADB, C2 o control remoto.
- [ ] App objetivo identificada y verificada.
- [ ] Permisos necesarios disponibles según técnica seleccionada: root, accesibilidad o ADB.
- [ ] Kill Switch armado.
- [ ] Operador autorizado.
- [ ] Scope del laboratorio válido.
- [ ] Para técnicas de overlay o manipulación de transacciones: confirmación explícita del usuario y aviso de responsabilidad.
- [ ] VersionLock de herramientas verificado: Frida, apktool, objection, adb, jadx u otras requeridas.
- [ ] Redacción de hallazgos sensibles activa por defecto.
- [ ] EvidenceStore y AuditLog preparados para hashes, timeline y cadena de custodia.

Si cualquier ítem falla:

- la técnica no se ejecuta;
- el botón de acción permanece desactivado;
- el estado pasa a `app_not_supported`, `root_required`, `permission_missing`, `blocked_by_policy` o `error` según corresponda;
- Mistral explica el motivo en lenguaje natural;
- AuditLog registra el bloqueo si hubo intento de ejecución.

### Errores y recuperación asistida del Vector 10

#### App no detectada o no soportada

- El panel muestra `app_not_supported`.
- No se ejecuta ninguna técnica.
- Mistral sugiere: **Esta app no está en mi base de datos. ¿Deseas solicitar a Hermes un análisis personalizado?**.
- Si el usuario acepta, se abre el flujo Hermes de evolución del arsenal con perfil de paquete, versión y evidencias disponibles.

#### Permisos insuficientes

- Si la técnica requiere root y el dispositivo no lo tiene, el panel muestra `root_required`.
- Mistral sugiere alternativas permitidas, por ejemplo overlay si hay accesibilidad activa o esperar a un entorno con root autorizado.
- Si la técnica requiere accesibilidad y no está activa, Mistral sugiere activarla o usar una técnica alternativa compatible.
- No se ejecuta nada que exceda permisos, scope o Policy Engine.

#### Error en la ejecución de Frida

- Si Frida no puede engancharse al proceso, por ejemplo por detección de Frida en la app, X5 notifica a Mistral.
- Mistral sugiere usar objection con ofuscación en laboratorio o solicitar a Hermes un bypass personalizado.
- Se guardan logs minimizados, versión de Frida/objection, paquete objetivo, error y AuditLog.
- Cualquier bypass queda `IMPLEMENTACION_USUARIO_REQUERIDA` hasta sandbox, revisión y promoción.

#### Dispositivo se desconecta durante el ataque

- El panel marca el dispositivo como `disconnected`.
- Se guardan evidencias parciales.
- Si el ataque era automatizado, se pausa y se notifica al usuario.
- X5 evita reintentos automáticos fuera de Policy Engine, scope, permisos y confirmación.

#### Kill Switch activado

- Se detiene inmediatamente cualquier hook, overlay, extracción, captura o manipulación futura activa.
- Se guardan evidencias pendientes.
- El estado global cambia a `kill_switch_triggered`.
- AuditLog recibe registro prioritario.
- El panel exige revisión antes de reanudar cualquier técnica.

#### Policy bloquea la acción

- El estado cambia a `blocked_by_policy`.
- Se muestra el motivo del bloqueo.
- La técnica no se ejecuta.
- Mistral puede proponer alternativas permitidas por scope, pero no puede saltarse la decisión de Policy Engine.

### Handoff con otros módulos

El Vector 10 puede enviar sus hallazgos a otros módulos mediante contratos auditados, redacción por defecto, confirmación explícita cuando aplique, EvidenceStore y AuditLog. Ningún handoff autoriza ejecución automática en el módulo receptor: cada continuidad debe pasar por scope, Policy Engine, Kill Switch, VersionLock y aprobación humana cuando sea necesario.

#### Handoff con Módulo 5 — Credenciales

Las frases semilla, claves privadas, contraseñas, tokens, direcciones sensibles y secretos extraídos por técnicas del Vector 10 deben empaquetarse como `credential_handoff` y enviarse a M5.

Reglas:

- `source_module = "android"`;
- `source_vector = "crypto"`;
- `source_evidence_id` obligatorio;
- redacción por defecto con valores enmascarados;
- M5 clasifica, deduplica y decide acciones;
- mostrar valores completos requiere confirmación reforzada y AuditLog.

M5 recibe hallazgos normalizados y referencias a evidencias, no texto suelto ni permiso para revelar secretos sin cadena de custodia.

#### Handoff con Módulo 12 — Orquestación

Todas las acciones `android.crypto.*` heredan el flujo M12:

- LaIA/Mistral genera plan y rellena parámetros;
- X5 valida permisos, scope, Policy, Kill Switch y VersionLock;
- EvidenceStore guarda;
- AuditLog registra;
- scoring X5 solo con evidencia válida;
- Hermes Agent se activa si falta parser, bypass de protección o soporte para una nueva app.

M12 mantiene la autoridad de orquestación: ninguna técnica de wallet, overlay, portapapeles, hook o transacción puede saltarse confirmaciones reforzadas, redacción por defecto ni parada de emergencia.

#### Handoff interno dentro del Módulo 13

El Vector 10 puede encadenar hallazgos hacia otros vectores Android:

- **Vector 3 Control Remoto**: si se obtiene acceso a la app o al dispositivo, se puede transferir el control para interactuar directamente con la app financiera. El handoff debe incluir `device_id`, `session_id`, tipo de acceso, estado y evidencias.
- **Vector 6 Análisis de Apps**: si se necesita análisis más profundo de la app —descompilación, búsqueda de secretos en código, endpoints, permisos o componentes exportados— se envía la APK y sus evidencias relacionadas.
- **Vector 8 Accesibilidad**: el ataque de overlay y la interceptación del portapapeles dependen del servicio de accesibilidad desplegado por el Vector 8. Si no está activo, el panel sugiere activarlo primero mediante el flujo de preflight y confirmación de Vector 8.

### Scoring X5 del Vector 10

Reglas:

- Solo puntúa si hay evidencia válida: frase semilla, clave privada, overlay exitoso o transacción manipulada dentro del scope autorizado.
- `app_not_supported` no penaliza la técnica porque no se ejecutó.
- `blocked_by_policy` no penaliza la técnica.
- Un falso positivo en el volcado de memoria, por ejemplo un patrón BIP39 incorrecto, baja el score de `android.crypto.dump_memory`.
- Una extracción exitosa de frase semilla sube el score de la técnica correspondiente.
- Evidencia corrupta, ausente, sin hash, fuera de scope o no redactada correctamente no sube score.
- Técnicas en estado `IMPLEMENTACION_USUARIO_REQUERIDA` no puntúan hasta promoción.

Campos recomendados:

- `technique_id`
- `session_id`
- `device_id`
- `package_name`
- `evidence_valid`
- `blocked_by_policy`
- `false_positive`
- `score_before`
- `score_after`
- `score_delta`
- `operator`

### Preparación para Módulo 16 — Evidencia / Ops / Calidad

Todas las evidencias del Vector 10 deben cumplir:

- SHA256 de cada archivo de evidencia, incluyendo frases semilla, claves, capturas, logs y scripts referenciados.
- Hashes encadenados en `timeline_json`.
- Cadena de custodia interna: acceso, revelado, exportación y operador.
- Exportación enmascarada por defecto, con frases y claves enmascaradas.
- Exportación completa solo con confirmación reforzada, scope válido, AuditLog y registro de revelado.
- Metadatos obligatorios: `session_id`, `device_id`, `technique_id`, `scope`, `operator`, VersionLock.
- Integridad verificable antes de handoff, exportación o inclusión en informe final.
- Compatibilidad con compilador final de M16 y controles de calidad de evidencia.

Tipos de evidencia:

- `seed_phrase.txt`: frase semilla extraída, siempre enmascarada por defecto.
- `private_key.txt`: clave privada extraída, siempre enmascarada por defecto.
- `overlay_capture.png`: captura del overlay desplegado.
- `clipboard_log.txt`: registro de interceptación del portapapeles.
- `transaction_log.json`: registro de transacciones manipuladas.
- `frida_script.js`: script de Frida utilizado o referenciado por la técnica.
- capturas del panel, timeline, hashes y AuditLog.

### Criterios de aceptación del Vector 10

El Vector 10 queda documentalmente cerrado si `docs/techniques/13_ANDROID.md` contiene:

- [ ] Propósito del Vector 10 documentado.
- [ ] Herramientas nominales y VersionLock documentados: adb, Frida, objection, apktool, jadx, Python, Mistral y Hermes.
- [ ] Panel **Android > Carteras** documentado con sus subpáginas.
- [ ] Pantallas de trabajo por técnica documentadas: extracción, volcado, overlay, portapapeles y manipulación.
- [ ] Técnicas `android.crypto.*` documentadas con sus `technique_id`.
- [ ] Contrato `crypto_action` documentado.
- [ ] Contrato `crypto_handoff` documentado.
- [ ] Estados visuales del submódulo **Carteras** documentados.
- [ ] Flujo de trabajo asistido (Mistral + X5 + Hermes) documentado.
- [ ] Preflight checklist documentado.
- [ ] Errores y recuperación documentados.
- [ ] Handoffs con M5, M12 y M13 interno —Vectores 3, 6 y 8— documentados.
- [ ] Handoffs internos explícitos a Vector 3, Vector 6 y Vector 8 documentados.
- [ ] Scoring X5 documentado.
- [ ] Preparación para M16 documentada.
- [ ] Confirmaciones explícitas para técnicas de overlay y manipulación documentadas.
- [ ] No se afirma implementación real de extracción o manipulación de fondos.

### Estados visuales del submódulo **Carteras**

El panel **Android > Carteras** reflejará uno de los siguientes estados globales. Estos estados son contrato documental de UI y orquestación; no implican ejecución real ni disponibilidad funcional en esta ronda:

- `idle`: sin app seleccionada, esperando instrucciones.
- `scanning`: buscando apps financieras en el dispositivo.
- `app_selected`: una app ha sido seleccionada y se muestran sus técnicas.
- `extracting`: extrayendo archivos de la app cuando exista implementación futura aprobada.
- `dumping`: volcando memoria RAM con Frida cuando exista implementación futura aprobada.
- `overlay_active`: ventana falsa desplegada y esperando interacción en un entorno de laboratorio aprobado.
- `clipboard_active`: interceptación de portapapeles en curso en un entorno autorizado.
- `transaction_hook_active`: hook de manipulación de transacciones activo en un entorno autorizado.
- `success`: técnica ejecutada con éxito y evidencia generada.
- `error`: fallo en la ejecución.
- `blocked_by_policy`: acción denegada por Policy Engine.
- `kill_switch_triggered`: Kill Switch activado, todo detenido.

### Contrato JSON `crypto_handoff`

Cuando el Vector 10 envía hallazgos a otros módulos, utiliza el contrato `crypto_handoff`. Este contrato es documentación de arquitectura: no representa endpoint, worker, base de datos ni schema implementado.

```json
{
  "type": "crypto_handoff",
  "source_module": "android",
  "source_vector": "M13_V10",
  "session_id": "sess-7890",
  "device_id": "dev-1234",
  "evidence_ids": ["ev-001", "ev-002"],
  "target_module": "M5",
  "handoff_reason": "seed_phrase_extracted",
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

Reglas documentales:

- `type` debe ser `crypto_handoff`.
- `source_module` debe ser `android`.
- `source_vector` debe ser `M13_V10`.
- `redaction_policy` debe ser `mask_all` por defecto para frases semilla, claves privadas, contraseñas, tokens y direcciones sensibles.
- `requires_confirmation` debe ser `true` si el handoff permite revelar, exportar, correlacionar o actuar sobre material sensible.
- EvidenceStore y AuditLog deben preservar hashes, operador, timestamp, motivo y cadena de custodia antes de cualquier continuidad futura.

### Handoff interno explícito dentro del Módulo 13

El Vector 10 puede enviar hallazgos a otros vectores del propio Módulo Android para continuar la auditoría de forma encadenada. Estos handoffs internos no ejecutan acciones por sí mismos: abren contexto, evidencias y planes revisables que vuelven a pasar por LaIA/Mistral, X5/OjoRouter, Policy Engine, Kill Switch, VersionLock, EvidenceStore y AuditLog.

#### Handoff al Vector 3 — Control Remoto

Si tras una extracción o manipulación se necesita interactuar directamente con la app, se transfiere al Vector 3:

- `device_id` del dispositivo;
- `session_id` activa;
- `handoff_reason`: `manual_interaction_required`;
- evidencias y estado de la técnica que originó el handoff.

El usuario puede abrir el panel de **Control Remoto** desde un botón en la pantalla de la técnica. Ese botón solo abre el contexto del Vector 3 y no autoriza interacción remota sin confirmación, scope, Policy Engine, Kill Switch y AuditLog.

#### Handoff al Vector 6 — Análisis de Apps

Si se requiere un análisis más profundo de la app financiera —descompilación, búsqueda de secretos en el código, endpoints, permisos o componentes exportados— se envía la APK al Vector 6:

- `evidence_ids` con el archivo APK;
- `device_id` del dispositivo o app de origen si aplica;
- `handoff_reason`: `deep_analysis`.

El Vector 6 recibe la APK y aplica sus técnicas documentales de descompilación, búsqueda de endpoints y secretos, siempre con redacción por defecto, EvidenceStore y AuditLog.

#### Handoff al Vector 8 — Accesibilidad

Las técnicas de overlay y manipulación de transacciones dependen del servicio de accesibilidad del Vector 8.

- Si el servicio de accesibilidad no está activo, Mistral sugiere activarlo primero mediante el preflight y las confirmaciones del Vector 8.
- El handoff es bidireccional: el Vector 8 notifica al Vector 10 cuando el servicio está listo.
- Cuando el Vector 8 confirma estado listo, el Vector 10 puede preparar el despliegue documental del overlay o la técnica dependiente, siempre con confirmación reforzada, Policy Engine, Kill Switch, VersionLock, EvidenceStore y AuditLog.

### Nota final del Vector 10

Con esta ronda, el Vector 10 alcanza la misma profundidad documental que los vectores 7 y 9. Queda completamente cerrado como especificación de producto/laboratorio para carteras de criptomonedas y apps financieras. Esta documentación no crea lógica funcional ni afirma ejecución real de extracción o manipulación de activos. Las partes sensibles permanecen marcadas como:

- `IMPLEMENTACION_USUARIO_REQUERIDA`

## Vector 11 — Mensajería

El Vector 11 define **Mensajería** como especificación documental de producto/laboratorio para auditorías Android autorizadas sobre apps de mensajería, chats, backups, notificaciones, multimedia, hooks controlados y sesiones. Esta sección es solo documentación: no implementa código, endpoints, workers, base de datos, tests, requirements, scripts funcionales ni comandos operativos. Ninguna pantalla descrita afirma extracción real de chats, tokens, cookies, multimedia, backups, mensajes o sesiones.

Toda capacidad sensible del Vector 11 permanece marcada como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta implementación futura aprobada, sandbox, revisión, autorización explícita, scope válido, Policy Engine favorable, Kill Switch armado, VersionLock, EvidenceStore y AuditLog. Cualquier hallazgo sensible —mensajes, contactos, tokens, cookies, contraseñas, claves, multimedia o contenido privado— debe quedar enmascarado por defecto, protegido por cadena de custodia y gestionado mediante contratos auditados.

### Herramientas y versiones nominales — Kali WSL2

Las herramientas siguientes se documentan como inventario nominal de laboratorio para VersionLock. No se instalan ni ejecutan en esta ronda. Las referencias de instalación o clonación quedan como metadatos documentales de origen, no como instrucciones operativas que el panel pueda ejecutar.

- **adb 34.0.5**: referencia documental `sudo apt install adb`; uso previsto: acceso autorizado a archivos, backups y estado del dispositivo.
- **android-backup-toolkit latest**: referencia documental `git clone https://github.com/nelenkov/android-backup-toolkit`; uso previsto: análisis autorizado de backups Android.
- **abpt — Android Backup Parser Toolkit latest**: referencia documental `git clone https://github.com/digitalsleuth/abpt`; uso previsto: parseo autorizado de backups Android.
- **Frida 16.5**: referencia documental `pip install frida-tools`; uso previsto: hooks autorizados en laboratorio.
- **objection 1.13**: referencia documental `pip install objection`; uso previsto: automatización sobre Frida dentro de laboratorio.
- **jadx 1.5.2**: referencia documental `sudo apt install jadx`; uso previsto: análisis estático de APKs de mensajería autorizadas.
- **sqlite3**: referencia documental `sudo apt install sqlite3`; uso previsto: inspección autorizada de bases de datos SQLite extraídas.
- **signal-back latest**: referencia documental `git clone https://github.com/xeals/signal-back`; uso previsto: análisis de backups Signal autorizados.
- **hashcat 7.0.1**: Windows nativo o Kali; uso previsto: evaluación autorizada de backups cifrados de Signal.
- **Dolphin Mistral Nemo 12B**: generación de planes, scripts documentales y guía del flujo de ataque, sin ejecución automática.
- **Hermes (DeepSeek API)**: creación de propuestas de módulos para apps no catalogadas, nuevos formatos, cifrados o protecciones.

VersionLock debe registrar versión detectada, origen, compatibilidad, ubicación Kali WSL2/Windows si aplica, permisos requeridos, decisión de uso, operador, timestamp y motivo. Si VersionLock no valida una herramienta, el panel bloquea la técnica y muestra el motivo.

### Panel de control **Android > Mensajería**

Dentro de **Android > Mensajería**, el Vector 11 define una sección específica para detección, extracción, backups, notificaciones, hooks, multimedia, sesiones, evidencia, historial y evolución Hermes. Ninguna subpágina ejecuta acciones por sí misma: Mistral/LaIA propone, X5/OjoRouter valida, Policy Engine decide, Kill Switch puede detener, VersionLock bloquea incompatibilidades y EvidenceStore/AuditLog preservan evidencias si existe implementación futura aprobada.

Subpáginas documentadas:

- **Detección de Apps**: tabla con WhatsApp, Telegram, Signal y otras apps detectadas.
- **Extracción de Chats**: acceso documental a archivos de base de datos del dispositivo cuando el scope, permisos y VersionLock lo permitan.
- **Forzar Backup**: generación documental de copia de seguridad vía ADB sin root si la app lo permite.
- **Interceptación de Notificaciones**: enlace con el Vector 8 para leer mensajes entrantes en tiempo real cuando accesibilidad esté activa y autorizada.
- **Hook de Envío**: consola Frida documental para modificar o enviar mensajes dentro de laboratorio autorizado.
- **Multimedia**: visor de archivos de imagen, vídeo y documento de apps de mensajería.
- **Clonación de Sesión**: extracción documental de tokens y cookies para evaluación de suplantación bajo scope autorizado.
- **Evidencias**: bases de datos, backups, multimedia, tokens enmascarados, capturas, hashes, timeline y reportes.
- **Historial/AuditLog**: confirmaciones, bloqueos, accesos, revelados, exportaciones, operador y timestamps.
- **Hermes Agent Lab**: propuestas para apps no catalogadas, parsers, schemas, hooks, decoders o módulos de laboratorio.

### Pantallas de trabajo por técnica

#### Extracción de Chats

- **Campo `App seleccionada`**: autocompletado por Mistral al seleccionar una app de mensajería detectada.
- **Botón `Extraer base de datos`**: prepara un plan revisable para obtener `msgstore.db` en WhatsApp, `telegram.sqlite` en Telegram o la carpeta de backups de Signal mediante referencias documentales como `adb pull` o comandos root autorizados. No ejecuta extracción real en esta ronda.
- **Visor de mensajes**: tabla con mensajes extraídos cuando exista implementación futura; columnas documentales: remitente, texto y fecha.
- **Búsqueda**: campo de búsqueda por palabra clave.
- **Botón `Exportar chats`**: guarda en CSV/JSON cuando exista implementación futura y ofrece handoff a Módulo 5 — Credenciales si se encuentran claves, contraseñas o secretos.
- **Evidencia esperada**: base de datos, exportación CSV/JSON, hashes SHA256, timeline y AuditLog.

#### Forzar Backup — sin root

- **Campo `App seleccionada`**: autocompletado por Mistral.
- **Botón `Crear backup`**: prepara un plan documental para generar un backup con ADB si la app lo permite, con referencia documental `adb backup -f <archivo>.ab <paquete>`; no crea archivos reales en esta ronda.
- **Botón `Parsear backup`**: prepara el procesamiento del `.ab` con android-backup-toolkit y abpt para extraer datos en texto plano cuando exista implementación futura aprobada.
- **Visor de resultados**: chats, contactos y archivos extraídos del backup, con redacción por defecto.
- **Evidencia esperada**: archivo `.ab`, datos parseados, hashes, metadatos de app, timeline y AuditLog.

#### Interceptación de Notificaciones — requiere Vector 8 activo

- **Indicador de estado**: muestra `Accesibilidad activa` o `Requiere activar Vector 8`.
- **Tabla en tiempo real**: app, título y texto de notificaciones de mensajería cuando exista implementación futura y autorización válida.
- **Registro automático**: los mensajes entrantes se registran automáticamente solo en un flujo futuro aprobado, con redacción por defecto y AuditLog.
- **Dependencia**: si Vector 8 no está activo, Mistral sugiere activarlo primero mediante su preflight y confirmaciones.

#### Hook de Envío — Frida

- **Campo `App seleccionada`**: autocompletado por Mistral.
- **Campo `Script Frida`**: desplegable con opciones `Enviar mensaje`, `Modificar mensaje`, `Eliminar mensaje` y `Personalizado`.
- **Modo `Personalizado`**: habilita editor de código documental; cualquier script real queda `IMPLEMENTACION_USUARIO_REQUERIDA`.
- **Botón `Inyectar hook`**: prepara un plan Frida para el proceso de la app; no afirma hook real en esta ronda.
- **Estado del hook**: muestra `pending`, `active`, `error` o `blocked_by_policy` cuando exista implementación futura.
- **Consola de comandos**: interfaz documental para instrucciones en tiempo real, por ejemplo **Envía 'Hola' a este chat**, siempre sujeta a confirmación, scope, Policy Engine, Kill Switch y AuditLog.

#### Extracción de Multimedia

- **Campo `App seleccionada`**: autocompletado por Mistral.
- **Botón `Extraer multimedia`**: prepara un plan para extraer carpetas de imágenes, vídeos y documentos de la app mediante referencia documental `adb pull` o root autorizado.
- **Visor multimedia**: muestra miniaturas con opción documental de descarga cuando exista implementación futura.
- **Evidencia esperada**: archivos multimedia, hashes, rutas, metadatos, timeline y AuditLog.

#### Clonación de Sesión

- **Campo `App seleccionada`**: autocompletado por Mistral.
- **Botón `Extraer tokens`**: prepara un plan Frida para obtener tokens de sesión y cookies en laboratorio autorizado; no afirma extracción real.
- **Visor de valores**: muestra valores extraídos únicamente enmascarados por defecto; revelar completo requiere confirmación reforzada y AuditLog.
- **Botón `Enviar a Credenciales`**: handoff a Módulo 5 mediante contrato auditado cuando existan tokens, cookies, claves o contraseñas.
- **Evidencia esperada**: tokens/cookies enmascarados, script referenciado, capturas del panel, hashes, timeline y AuditLog.

### Técnicas registradas `android.messaging.*`

Las técnicas del Vector 11 quedan registradas como catálogo documental. Todas requieren scope autorizado, confirmación cuando aplique, VersionLock, Policy Engine, Kill Switch, EvidenceStore, AuditLog y `IMPLEMENTACION_USUARIO_REQUERIDA` hasta promoción.

#### `android.messaging.extract_chats`

- **description**: extracción autorizada de chats y bases de datos de apps de mensajería.
- **required_inputs**: `device_id`, `package_name`, permisos/root/ADB si aplica, ruta de salida, scope, operador y confirmación.
- **expected_evidence**: `chat_database.sqlite`, exportación CSV/JSON, hashes, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.messaging.force_backup`

- **description**: creación y parseo documental de backup Android sin root si la app lo permite.
- **required_inputs**: `device_id`, `package_name`, archivo `.ab`, scope, operador y confirmación.
- **expected_evidence**: backup `.ab`, datos parseados, contactos, chats, hashes y AuditLog.
- **risk_level**: alto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.messaging.intercept_notifications`

- **description**: interceptación documental de notificaciones de mensajería mediante dependencia con Vector 8.
- **required_inputs**: `device_id`, app objetivo opcional, Vector 8 activo, scope, operador y confirmación.
- **expected_evidence**: notificaciones enmascaradas, timeline y AuditLog.
- **risk_level**: alto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.messaging.hook_send`

- **description**: hook Frida documental para enviar, modificar o eliminar mensajes en laboratorio autorizado.
- **required_inputs**: `device_id`, `package_name`, script seleccionado, comando, scope, operador y confirmación reforzada.
- **expected_evidence**: estado del hook, comando enmascarado si aplica, resultado, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.messaging.extract_media`

- **description**: extracción autorizada de imágenes, vídeos y documentos de apps de mensajería.
- **required_inputs**: `device_id`, `package_name`, rutas multimedia, scope, operador y confirmación.
- **expected_evidence**: media files, hashes, metadatos, timeline y AuditLog.
- **risk_level**: alto.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

#### `android.messaging.clone_session`

- **description**: extracción documental de tokens y cookies de sesión para evaluación autorizada de suplantación.
- **required_inputs**: `device_id`, `package_name`, script Frida, scope, operador y confirmación reforzada.
- **expected_evidence**: tokens/cookies enmascarados, handoff a M5, hashes, timeline y AuditLog.
- **risk_level**: crítico.
- **implementation_status**: `IMPLEMENTACION_USUARIO_REQUERIDA`.

### Contrato JSON `messaging_action`

Contrato JSON base para acciones de mensajería. Es especificación documental, no endpoint ni schema implementado.

```json
{
  "type": "messaging_action",
  "device_id": "dev-1234",
  "technique_id": "android.messaging.extract_chats",
  "params": {
    "package_name": "com.whatsapp",
    "output_path": "/evidence/chats/"
  },
  "expected_evidence": ["chat_database.sqlite", "media_files"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

Campos obligatorios:

- `type`
- `device_id`
- `technique_id`
- `params`
- `expected_evidence`
- `scope`
- `operator`
- `requires_confirmation`

Reglas del contrato:

- `type` debe ser `messaging_action`.
- `technique_id` debe pertenecer al catálogo `android.messaging.*`.
- `scope` debe ser explícito, autorizado y auditable.
- `requires_confirmation` debe ser `true` para técnicas de extracción, hook, sesión o cualquier lectura de contenido sensible.
- `params` debe estar minimizado y redactado por defecto cuando incluya rutas, comandos, paquetes, chats o identificadores sensibles.
- EvidenceStore debe rechazar hallazgos sin hash, técnica, operador, timestamp, redacción y cadena de custodia cuando exista implementación futura.
- X5/OjoRouter debe bloquear acciones sin permisos/root/ADB, Vector 8 activo cuando aplique, VersionLock válido, Policy Engine favorable o Kill Switch armado.

### Flujo de trabajo asistido — Mistral + X5 + Hermes

El flujo asistido del Vector 11 describe cómo el panel **Android > Mensajería** debe guiar detección, selección, validación, ejecución futura aprobada, recuperación y evolución Hermes para apps de mensajería. Mistral/LaIA actúa como cerebro contextual, X5/OjoRouter valida y enruta bajo Policy Engine, Kill Switch y VersionLock, y Hermes Agent solo interviene en laboratorio cuando falta soporte para una app, esquema de cifrado, parser o protección. Cualquier worker, script Frida, parser de base de datos, técnica de extracción o módulo mencionado es referencia documental futura y permanece como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta sandbox, revisión, aprobación y promoción.

#### Detección y sugerencia inicial

Flujo esperado:

1. El usuario accede a **Android > Mensajería**.
2. El panel muestra automáticamente las apps de mensajería detectadas en el dispositivo: WhatsApp, Telegram, Signal u otras.
3. Mistral identifica previamente esas apps mediante una referencia documental a `adb shell pm list packages` y una base de datos local de paquetes conocidos. Esta referencia no implica ejecución en esta ronda.
4. Mistral cruza nombre de paquete, versión si está disponible, permisos, estado ADB/root/accesibilidad, backups visibles y evidencias previas.
5. Mistral sugiere en el chat contextual: **Se han detectado 4 apps de mensajería. WhatsApp tiene copia de seguridad habilitada y es vulnerable a extracción sin root. ¿Deseas proceder?**.
6. La sugerencia muestra técnica propuesta, riesgo, permisos requeridos, evidencia esperada, redacción por defecto, necesidad de confirmación y controles de parada.

La sugerencia de Mistral no autoriza ejecución. El usuario debe seleccionar o confirmar una acción, y X5/OjoRouter debe validar scope, Policy Engine, Kill Switch, permisos, VersionLock y EvidenceStore antes de cualquier ejecución futura aprobada.

#### Ejecución de una técnica

Flujo esperado:

1. El usuario selecciona una app y una técnica desde el panel, o escribe una intención en lenguaje natural, por ejemplo: **Extrae todos los chats de Telegram**.
2. Mistral analiza permisos disponibles: root, accesibilidad activa, ADB, C2 o control remoto según el dispositivo.
3. Mistral selecciona la técnica más adecuada del catálogo `android.messaging.*`.
4. Mistral rellena el contrato JSON `messaging_action` con parámetros como `package_name`, `output_path`, `script`, evidencia esperada, scope, operador y `requires_confirmation`.
5. El panel muestra el plan en una ventana modal revisable, con riesgos, redacción, evidencia prevista, permisos requeridos y criterios de parada.
6. El usuario confirma o cancela.
7. X5 valida contra Policy Engine, Kill Switch, scope, permisos, VersionLock, estado del dispositivo, redacción y EvidenceStore.
8. Si existe implementación futura aprobada, X5 enruta la técnica mediante un worker autorizado en Kali WSL2 para capacidades como ADB, Frida, sqlite3, android-backup-toolkit, abpt o herramientas equivalentes validadas.
9. El panel muestra progreso en tiempo real mediante estados visuales, timeline y AuditLog.
10. Si la técnica implica hook de envío o clonación de sesión, se solicita confirmación explícita adicional y aviso de responsabilidad antes de continuar.
11. Los hallazgos sensibles se muestran enmascarados por defecto. Revelar valores completos requiere confirmación reforzada, scope válido, cadena de custodia y AuditLog.

Ninguna instrucción en lenguaje natural puede saltarse permisos, Policy Engine, Kill Switch, VersionLock, confirmaciones reforzadas ni redacción por defecto.

#### Intervención de Hermes — Evolución del Arsenal

Hermes Agent puede intervenir cuando una técnica falla porque la app cambió su esquema de cifrado, usa un nuevo mecanismo de protección, detecta Frida/objection, no está en la base de datos de paquetes o requiere un parser/schema no catalogado.

Flujo esperado:

1. X5 notifica a Mistral que la técnica falló por app no soportada, cifrado nuevo, protección no catalogada, parser faltante, detección de Frida o error de compatibilidad.
2. Mistral sugiere al usuario: **Esta app no responde a las técnicas disponibles. ¿Solicito a Hermes un módulo personalizado?**.
3. Si el usuario acepta, Mistral envía a Hermes una solicitud con el perfil de la app: nombre de paquete, versión, permisos, técnica fallida, error, archivos extraídos si los hay, capturas, fingerprints y metadatos de VersionLock.
4. Hermes busca en fuentes abiertas como GitHub, foros de seguridad y documentación técnica autorizada una PoC, referencia, bypass, técnica de extracción o parser de base de datos aplicable.
5. Si encuentra información suficiente, Hermes propone un módulo de laboratorio como script Frida, técnica de extracción, parser de base de datos o `evidence_schema`.
6. Hermes prueba la propuesta en sandbox cuando exista pipeline aprobado.
7. Si la prueba es exitosa, Hermes notifica al usuario: **Nuevo módulo para Signal v7.2 listo para revisión**.
8. El usuario revisa la propuesta y, si la aprueba, la promociona al arsenal mediante el pipeline Research → Quarantine → Analyze → Build → Sandbox Test → Evidence → Review → Approval → Promotion.
9. Solo tras promoción, X5 puede reanudar el ataque original con la nueva técnica dentro del scope, Policy Engine, Kill Switch, VersionLock y EvidenceStore.
10. Si Hermes no encuentra información suficiente, lo comunica y sugiere aportar manualmente una PoC o 0-day mediante el hook `IMPLEMENTACION_USUARIO_REQUERIDA`.

Hermes no autoaprueba, no instala herramientas, no ejecuta contra objetivos reales y no sustituye revisión humana. Todo módulo personalizado permanece bloqueado hasta evidencia de sandbox y aprobación explícita.

### Preflight checklist obligatorio del Vector 11

Antes de ejecutar cualquier técnica del Vector 11, el panel debe mostrar y bloquear según este checklist:

- [ ] Dispositivo conectado y accesible: ADB, C2 o control remoto.
- [ ] App objetivo identificada y verificada.
- [ ] Permisos necesarios disponibles según técnica seleccionada: root, accesibilidad o ADB.
- [ ] Kill Switch armado.
- [ ] Operador autorizado.
- [ ] Scope del laboratorio válido.
- [ ] Para técnicas de hook de envío o clonación de sesión: confirmación explícita del usuario y aviso de responsabilidad.
- [ ] VersionLock de herramientas verificado: Frida, sqlite3, adb, android-backup-toolkit, abpt u otras requeridas.
- [ ] Redacción de mensajes, tokens, cookies y multimedia sensible activa por defecto.
- [ ] EvidenceStore y AuditLog preparados para hashes, timeline y cadena de custodia.

Si cualquier ítem falla:

- la técnica no se ejecuta;
- el botón de acción permanece desactivado;
- el estado pasa a `app_not_supported`, `root_required`, `permission_missing`, `blocked_by_policy` o `error` según corresponda;
- Mistral explica el motivo en lenguaje natural;
- AuditLog registra el bloqueo si hubo intento de ejecución.

### Errores y recuperación asistida del Vector 11

#### App no detectada o no soportada

- El panel muestra `app_not_supported`.
- No se ejecuta ninguna técnica.
- Mistral sugiere: **Esta app no está en mi base de datos. ¿Deseas solicitar a Hermes un análisis personalizado?**.
- Si el usuario acepta, se abre el flujo Hermes de evolución del arsenal con perfil de paquete, versión y evidencias disponibles.

#### Permisos insuficientes

- Si la técnica requiere root y el dispositivo no lo tiene, el panel muestra `root_required`.
- Mistral sugiere alternativas permitidas, por ejemplo forzar backup sin root si la app lo permite o esperar a un entorno con root autorizado.
- Si la técnica requiere accesibilidad y no está activa, Mistral sugiere activarla mediante el Vector 8.
- No se ejecuta nada que exceda permisos, scope o Policy Engine.

#### Error en la extracción de base de datos

- Si la referencia documental `adb pull` falla por permisos o la ruta no existe en una implementación futura, X5 notifica a Mistral.
- Mistral sugiere intentar con acceso root autorizado o forzar un backup alternativo si la app lo permite.
- Se guardan logs minimizados, paquete objetivo, ruta solicitada, error, timeline y AuditLog.

#### Frida no puede engancharse al proceso

- Si Frida no puede engancharse al proceso, por ejemplo por detección de Frida en la app, X5 notifica a Mistral.
- Mistral sugiere usar objection con ofuscación en laboratorio o solicitar a Hermes un bypass personalizado.
- Se guardan logs minimizados, versión de Frida/objection, paquete objetivo, error y AuditLog.
- Cualquier bypass queda `IMPLEMENTACION_USUARIO_REQUERIDA` hasta sandbox, revisión y promoción.

#### Dispositivo se desconecta durante el ataque

- El panel marca el dispositivo como `disconnected`.
- Se guardan evidencias parciales.
- Si el ataque era automatizado, se pausa y se notifica al usuario.
- X5 evita reintentos automáticos fuera de Policy Engine, scope, permisos y confirmación.

#### Kill Switch activado

- Se detiene inmediatamente cualquier hook, extracción o backup futuro activo.
- Se guardan evidencias pendientes.
- El estado global cambia a `kill_switch_triggered`.
- AuditLog recibe registro prioritario.
- El panel exige revisión antes de reanudar cualquier técnica.

#### Policy bloquea la acción

- El estado cambia a `blocked_by_policy`.
- Se muestra el motivo del bloqueo.
- La técnica no se ejecuta.
- Mistral puede proponer alternativas permitidas por scope, pero no puede saltarse la decisión de Policy Engine.

### Handoff con otros módulos

El Vector 11 puede enviar sus hallazgos a otros módulos mediante contratos auditados, redacción por defecto, confirmación explícita cuando aplique, EvidenceStore y AuditLog. Ningún handoff autoriza ejecución automática en el módulo receptor: cada continuidad debe pasar por scope, Policy Engine, Kill Switch, VersionLock y aprobación humana cuando sea necesario.

#### Handoff con Módulo 5 — Credenciales

Los tokens de sesión, cookies, contraseñas, claves o secretos encontrados en chats, backups, bases de datos, notificaciones o sesiones de mensajería deben empaquetarse como `credential_handoff` y enviarse a M5.

Reglas:

- `source_module = "android"`;
- `source_vector = "messaging"`;
- `source_evidence_id` obligatorio;
- redacción por defecto con valores enmascarados;
- M5 clasifica, deduplica y decide acciones;
- mostrar valores completos requiere confirmación reforzada y AuditLog.

M5 recibe hallazgos normalizados y referencias a evidencias, no texto suelto ni permiso para revelar secretos sin cadena de custodia.

#### Handoff con Módulo 12 — Orquestación

Todas las acciones `android.messaging.*` heredan el flujo M12:

- LaIA/Mistral genera plan y rellena parámetros;
- X5 valida permisos, scope, Policy, Kill Switch y VersionLock;
- EvidenceStore guarda;
- AuditLog registra;
- scoring X5 solo con evidencia válida;
- Hermes Agent se activa si falta parser, bypass de cifrado o soporte para una nueva app.

M12 mantiene la autoridad de orquestación: ninguna técnica de extracción de chats, backup, hook, notificación, multimedia o clonación de sesión puede saltarse confirmaciones reforzadas, redacción por defecto ni parada de emergencia.

#### Handoff interno dentro del Módulo 13

El Vector 11 puede encadenar hallazgos hacia otros vectores Android:

- **Vector 3 Control Remoto**: si se necesita interactuar directamente con la app de mensajería, se transfiere el control del dispositivo mediante contexto revisable. El handoff debe incluir `device_id`, `session_id`, estado de la app, técnica origen y evidencias.
- **Vector 6 Análisis de Apps**: si se requiere análisis más profundo de la app —descompilación, búsqueda de secretos en código, endpoints, permisos, cifrado o componentes exportados— se envía la APK y evidencias relacionadas.
- **Vector 8 Accesibilidad**: la interceptación de notificaciones depende del servicio de accesibilidad. Si no está activo, Mistral sugiere activarlo primero mediante el preflight y las confirmaciones del Vector 8.

### Contrato JSON `messaging_handoff`

Cuando el Vector 11 envía hallazgos a otros módulos, utiliza el contrato `messaging_handoff`. Este contrato es documentación de arquitectura: no representa endpoint, worker, base de datos ni schema implementado.

```json
{
  "type": "messaging_handoff",
  "source_module": "android",
  "source_vector": "M13_V11",
  "session_id": "sess-7890",
  "device_id": "dev-1234",
  "evidence_ids": ["ev-001", "ev-002"],
  "target_module": "M5",
  "handoff_reason": "token_extracted",
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

Reglas documentales:

- `type` debe ser `messaging_handoff`.
- `source_module` debe ser `android`.
- `source_vector` debe ser `M13_V11`.
- `redaction_policy` debe ser `mask_all` por defecto para tokens, cookies, contraseñas, chats, contactos y contenido sensible.
- `requires_confirmation` debe ser `true` si el handoff permite revelar, exportar, correlacionar o actuar sobre material sensible.
- EvidenceStore y AuditLog deben preservar hashes, operador, timestamp, motivo y cadena de custodia antes de cualquier continuidad futura.

### Scoring X5 del Vector 11

Reglas:

- Solo puntúa si hay evidencia válida: chats extraídos, backup parseado, token de sesión o notificación interceptada dentro del scope autorizado.
- `app_not_supported` no penaliza la técnica.
- `blocked_by_policy` no penaliza la técnica.
- Una extracción exitosa de chats sube el score de `android.messaging.extract_chats`.
- Un backup parseado con éxito sube el score de `android.messaging.force_backup`.
- Evidencia corrupta, ausente, sin hash, fuera de scope o no redactada correctamente no sube score.
- Técnicas en estado `IMPLEMENTACION_USUARIO_REQUERIDA` no puntúan hasta promoción.

Campos recomendados:

- `technique_id`
- `session_id`
- `device_id`
- `package_name`
- `evidence_valid`
- `blocked_by_policy`
- `false_positive`
- `score_before`
- `score_after`
- `score_delta`
- `operator`

### Preparación para Módulo 16 — Evidencia / Ops / Calidad

Todas las evidencias del Vector 11 deben cumplir:

- SHA256 de cada archivo de evidencia, incluyendo `chat_database.sqlite`, `backup.ab`, tokens, logs, multimedia y scripts referenciados.
- Hashes encadenados en `timeline_json`.
- Cadena de custodia interna: acceso, revelado, exportación y operador.
- Exportación enmascarada por defecto.
- Exportación completa solo con confirmación reforzada, scope válido, AuditLog y registro de revelado.
- Metadatos obligatorios: `session_id`, `device_id`, `technique_id`, `scope`, `operator`, VersionLock.
- Integridad verificable antes de handoff, exportación o inclusión en informe final.
- Compatibilidad con compilador final de M16 y controles de calidad de evidencia.

Tipos de evidencia:

- `chat_database.sqlite`: base de datos de chats extraída.
- `backup.ab`: archivo de backup forzado.
- `parsed_chats.json`: chats parseados en formato legible.
- `token_session.txt`: token de sesión extraído.
- `notification_log.json`: notificaciones interceptadas.
- `frida_hook_log.txt`: registro de la sesión de Frida.
- capturas del panel, multimedia, timeline, hashes y AuditLog.

### Criterios de aceptación del Vector 11

El Vector 11 queda documentalmente cerrado si `docs/techniques/13_ANDROID.md` contiene:

- [ ] Propósito del Vector 11 documentado.
- [ ] Herramientas nominales y VersionLock documentados: adb, android-backup-toolkit, abpt, Frida, objection, jadx, sqlite3, signal-back, hashcat, Mistral y Hermes.
- [ ] Panel **Android > Mensajería** documentado con sus subpáginas.
- [ ] Pantallas de trabajo por técnica documentadas: extracción, backup, notificaciones, hook, multimedia y clonación.
- [ ] Técnicas `android.messaging.*` documentadas con sus `technique_id`.
- [ ] Contratos `messaging_action` y `messaging_handoff` documentados.
- [ ] Flujo de trabajo asistido (Mistral + X5 + Hermes) documentado.
- [ ] Preflight checklist documentado.
- [ ] Errores y recuperación documentados.
- [ ] Handoffs con M5, M12 y M13 interno —Vectores 3, 6 y 8— documentados.
- [ ] Scoring X5 documentado.
- [ ] Preparación para M16 documentada.
- [ ] Confirmaciones explícitas para técnicas de hook y clonación documentadas.
- [ ] No se afirma implementación real de extracción o manipulación.

### Nota final del Vector 11

El Vector 11 queda definido como especificación de producto/laboratorio para mensajería Android. Esta documentación no crea lógica funcional ni afirma ejecución real de extracción o manipulación. Las partes sensibles permanecen marcadas como:

- `IMPLEMENTACION_USUARIO_REQUERIDA`

## Vectores futuros pendientes

Vector 12 pendiente de definir por el usuario.

Hasta que una ronda futura implemente y promueva capacidades reales, este documento debe leerse como especificación base. No se deben inventar capacidades funcionales, no se debe afirmar que un vector ya ejecuta acciones y no se debe saltar la cadena de control LaIA → X5/OjoRouter → Policy Engine/Scope/Kill Switch → EvidenceStore/AuditLog/scoring.
