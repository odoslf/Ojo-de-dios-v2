# Módulo 16 — Estación Hermes Agent Lab

## Estado M16

Los Vectores 1 y 2 están documentados y pendientes de validación operativa en
Windows. El Módulo 16 no se considera cerrado hasta completar Vectores 3-10.

## Verdad única Hermes Agent

- Nombre oficial: `Hermes Agent`.
- Repositorio oficial: `https://github.com/NousResearch/hermes-agent`.
- Documentación oficial: `https://hermes-agent.nousresearch.com/docs/`.

- Nombre interno: `hermes_lab`.
- Nombre visible: `Hermes Agent Lab`.
- Alias histórico deprecated: no usar como nombre operativo.
- Workspace autorizado: `modules/laboratory/`.
- Archivo por propuesta: `PROMOTION_MANIFEST.json`.
- Archivo central promovido: `modules/laboratory/_promoted_manifest/`.
- Preparación de workspace: `LAB_WORKSPACE_READY`.
- API comprobada + controles válidos: `READY_CONTROLLED`.

Hermes Agent no sustituye a X5/OjoRouter, Policy Engine, Kill Switch,
EvidenceStore ni AuditLog. Sus propuestas son material de laboratorio hasta que
exista revisión explícita, aprobación, promoción controlada y rollback posible.

## Requisitos

- Clave real de DeepSeek API configurada solo en `.env` local.
- `.env` creado a partir de `.env.example` y revisado por el operador.
- Conexión a internet hacia `https://api.deepseek.com`.
- Python disponible en Windows para las comprobaciones auxiliares.

No se deben escribir claves reales en documentación, repositorio, ejemplos,
logs, JSON de estado ni salida de consola. Nunca imprimir ni registrar
`DEEPSEEK_API_KEY`.

## Regla Codex / primera estación Windows

En Codex no se instala Hermes Agent ni se invoca la API externa. Se deja todo
vinculado mediante configuración, contratos, scripts y rutas. La conexión real
con DeepSeek y la preparación de estación se validan después en Windows con `.env`
local y claves reales nunca commiteadas.


## Instalador completo M16 desde ZIP

Para una estación nueva descargada como ZIP desde GitHub y extraída en Windows, el punto de entrada recomendado es:

```bat
scripts\windows\ia\instalar_modulo16_completo.bat
```

Ese BAT no contiene lógica ficticia: delega en los scripts reales de preflight, instalación de Ollama/modelo, healthcheck LaIA/Mistral, construcción de base de conocimiento y preparación/comprobación de Hermes Agent. Genera `storage\runtime\m16_full_install_status.json` y `storage\logs\ia\m16_full_install.log` para poder saber exactamente hasta dónde llegó la instalación.

Para arrancar la aplicación web en Windows después de extraer el ZIP de GitHub, usa:

```bat
scripts\windows\iniciar_ojo_de_dios_windows.bat
```

Ese arranque crea `.venv`, instala `requirements.txt`, crea `.env` desde `.env.example` si falta, prepara carpetas locales y abre la aplicación en `http://127.0.0.1:8000/modules`.

## Preparación y comprobación

1. Abre una consola en la raíz del proyecto.
2. Prepara el workspace controlado:

   ```bat
   scripts\windows\ia\preparar_estacion_angel_hermes.bat
   ```

3. Edita `.env` y sustituye el marcador de `DEEPSEEK_API_KEY` por la clave local.
4. Comprueba la conexión, la disponibilidad del modelo y el estado:

   ```bat
   scripts\windows\ia\comprobar_angel_hermes.bat
   ```

## Workspace

El workspace autorizado para propuestas Hermes Agent es `modules/laboratory/`.
Sus subcarpetas separan entradas, revisiones, sandbox y manifiestos promovidos.
Las propuestas no se consideran funcionales hasta pasar revisión, aprobación,
promoción controlada y registro documental.

| Ruta | Uso |
| --- | --- |
| `modules/laboratory/_inbox` | Entradas y propuestas pendientes. |
| `modules/laboratory/_reviews` | Revisión humana o técnica. |
| `modules/laboratory/_sandbox` | Pruebas controladas. |
| `modules/laboratory/_promoted_manifest/` | Manifiestos centrales promovidos. |
| `PROMOTION_MANIFEST.json` | Manifiesto obligatorio por propuesta. |

## API DeepSeek y configuración

- Base URL: `https://api.deepseek.com`.
- Modelos configurados: `deepseek-v4-pro`, `deepseek-v4-flash`.
- Endpoints documentados:
  - `GET /models`
  - `POST /chat/completions`
- El healthcheck debe validar disponibilidad del modelo mediante `/models` antes
  de declarar `READY_CONTROLLED`.

| Variable | Uso |
| --- | --- |
| `ANGEL_PROVIDER` | Proveedor configurado para Hermes Agent. |
| `DEEPSEEK_API_KEY` | Clave local privada, nunca documentada ni registrada con valor real. |
| `DEEPSEEK_API_URL` | Endpoint base de DeepSeek: `https://api.deepseek.com`. |
| `DEEPSEEK_MODEL` | Modelo principal: `deepseek-v4-pro`. |
| `DEEPSEEK_FAST_MODEL` | Modelo rápido/fallback/healthcheck: `deepseek-v4-flash`. |
| `ANGEL_WORKSPACE` | Ruta del workspace controlado: `modules/laboratory`. |
| `ANGEL_REQUIRE_APPROVAL` | Fuerza revisión humana antes de promoción. |
| `ANGEL_SANDBOX_ONLY` | Mantiene propuestas en laboratorio controlado. |

## Precedencia de variables IA

- `AI_ENABLED` es el interruptor global.
- `ANGEL_ENABLED` solo se evalúa si `AI_ENABLED=1`.
- La estación puede estar preparada con `AI_ENABLED=0`, pero la aplicación no
  debe usar DeepSeek ni Hermes Agent hasta activarlo explícitamente.
- `.env.example` debe permanecer seguro por defecto.

## Logs y runtime

| Uso | Ruta |
| --- | --- |
| Estado Hermes Agent | `storage\runtime\angel_hermes_status.json` |
| Healthcheck | `storage\logs\ia\angel_hermes_healthcheck.log` |
| Workspace | `modules\laboratory` |

## Errores comunes

| Error | Causa probable | Solución |
| --- | --- | --- |
| API key no configurada | `.env` no existe, está vacío o conserva un marcador. | Crea `.env` desde `.env.example` y añade la clave local real. |
| Modelo no disponible | `/models` no muestra el modelo configurado o la clave no tiene permiso. | Revisa `DEEPSEEK_MODEL`, permisos de la clave y respuesta de `/models`. |
| Conexión fallida | Endpoint no disponible, red bloqueada o credencial inválida. | Revisa conectividad, `DEEPSEEK_API_URL`, modelo y permisos de la clave. |
| Workspace ausente | No se ejecutó el preparador. | Ejecuta `preparar_estacion_angel_hermes.bat`. |
| Secreto en logs | El healthcheck imprimió o persistió `DEEPSEEK_API_KEY`. | Invalidar el log, rotar la clave local y corregir el flujo antes de reintentar. |
| `FAILED` | Falta configuración básica o falló una verificación. | Revisa el JSON de estado y repite la preparación. |

## Estados posibles

| Estado | Significado |
| --- | --- |
| `LAB_WORKSPACE_READY` | `modules/laboratory/` existe y está preparado para propuestas. |
| `READY_CONTROLLED` | Hermes Agent está listo bajo controles de sandbox, aprobación y política. |
| `MISSING_API_KEY` | Falta la clave API local o no está configurada. |
| `API_UNREACHABLE` | La API externa no responde o no es alcanzable. |
| `FAILED` | La comprobación se ejecutó, pero no alcanzó un estado válido. |
