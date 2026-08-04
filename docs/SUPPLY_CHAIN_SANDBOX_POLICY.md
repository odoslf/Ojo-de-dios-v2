# Supply Chain & Sandbox Policy

## Propósito

Este documento bloquea las reglas mínimas de supply-chain y sandbox para cualquier herramienta, repositorio, PoC, técnica, dependencia o integración externa que pueda ser investigada por DeepSeekAssist, revisada por Mistral/LaIA, preparada por Hermes Agent Lab o validada por X5/OjoRouter.

Esto forma parte del diseño base de Ojo de Dios v0.1 Lab Core, no de una versión 2.

## Reglas bloqueantes

- Ningún repo externo puede ejecutarse directamente en host.
- Ningún repo externo puede tocar `.env`, DB real, evidence real, locks reales ni claves.
- Ningún repo externo puede modificar producción.
- Ningún repo externo puede instalar servicios persistentes.
- Ningún repo externo puede ejecutar scripts de postinstall sin revisión.
- Ningún repo externo puede abrir red real sin aprobación.
- Ningún modelo puede decidir ejecutar comandos por sí solo.
- Ningún output de LLM se considera confiable hasta validación.

## Política de cuarentena

Toda entrada externa debe conservar:

- commit SHA;
- origen;
- timestamp;
- hash de archivos relevantes;
- inventario de dependencias;
- resultado de escaneos;
- decisión final.

La cuarentena es obligatoria antes de build, smoke test, sandbox test o promoción.

## Sandbox mínimo

El sandbox mínimo debe cumplir:

- Usuario sin privilegios.
- Directorio aislado.
- Sin secretos.
- Sin `.env` real.
- Sin credenciales.
- Sin token GitHub salvo lectura si hace falta.
- Red apagada por defecto.
- Red limitada solo con permiso.
- Timeout obligatorio.
- Límite CPU/RAM cuando aplique.
- Logs completos.
- Kill switch operativo.
- Limpieza controlada.

## Modos de prueba

- `build_test`
- `smoke_test`
- `demo_fixture_test`
- `authorized_lab_test`
- `controlled_real_test`

## Reglas por modo

### build_test

- Solo compilar/preparar.
- Sin target.
- Sin red salvo descarga permitida de dependencias en sandbox.
- No promociona.

### smoke_test

- Versión, ayuda, import básico, parser básico.
- Sin target real.
- No promociona.

### demo_fixture_test

- Usa fixtures falsos.
- `real_execution=false`.
- Puede generar evidencia demo.

### authorized_lab_test

- Solo laboratorio allowlist.
- Requiere aprobación.
- Requiere evidence contract.
- Requiere kill switch.

### controlled_real_test

- Solo activos propios autorizados.
- Requiere confirmación explícita.
- Requiere permisos adecuados.
- Requiere evidencia.
- Requiere posibilidad de parada.
- No puede ser modo por defecto.

## Validación de outputs LLM

Cualquier recomendación de DeepSeekAssist o Mistral/LaIA debe tratarse como propuesta no confiable hasta pasar validación:

- JSON válido;
- fuentes revisadas;
- scope revisado;
- permisos revisados;
- risks documentados;
- evidence contract presente;
- kill switch definido;
- usuario/Admin aprueba si procede.

## Reglas finales

- Producción nunca es sandbox.
- Cuarentena nunca es promoción.
- Build exitoso no equivale a confianza.
- Sandbox exitoso no equivale a aprobación.
- Aprobación no elimina scope, allowlist, evidence, ToolHealth, VersionLock ni kill switch.
