# TECHNIQUE CONNECTION CONTRACT — OJO DE DIOS

Cada técnica debe implementar este contrato conceptual:

## Campos mínimos

- technique_id
- module_id
- display_name
- description
- tool_name
- recommended_version
- runtime
- worker
- permission_level
- risk_level
- noise_level
- required_inputs
- optional_inputs
- ai_fillable_inputs
- panel_fields
- expected_evidence
- success_markers
- failure_markers
- configurable_parameters
- implementation_status
- requires_user_implementation
- requires_confirmation
- requires_hardware
- can_run_in_demo
- can_run_in_dry_run
- hermes_enabled
- mistral_assistant
- evidence_schema
- version_lock_id
- user_logic_hook

## UI/PANEL

Cada técnica debe tener campos propios.

Ejemplo Android:

- apk_path;
- android_version;
- lab_profile;
- callback_host;
- callback_port;
- payload_profile;
- signing_profile;
- output_path;
- listener_profile.

Ejemplo HackRF:

- device_id;
- center_frequency;
- sample_rate;
- rx_gain;
- tx_gain;
- modulation;
- iq_file;
- duration_seconds;
- tx_confirmation.

Ejemplo Scraping:

- natural_language_query;
- source;
- base_url;
- css_selector;
- xpath_selector;
- max_pages;
- concurrency;
- export_format;
- use_x4;
- x5_plan_enabled.

Ejemplo Cloud:

- provider;
- account_profile;
- region;
- cluster;
- namespace;
- image;
- severity_threshold;
- read_only_mode;
- mutation_confirmation.

## INPUT_SCHEMA

Cada técnica debe validar sus inputs antes de pasar a worker.

## WORKER_BINDING

Cada técnica debe declarar worker:

- WindowsWorker;
- WSLWorker;
- DockerWorker;
- HardwareWorker;
- HackRFWorker;
- AndroidWorker;
- PhishingWorker;
- CloudWorker;
- ScrapingWorker;
- OpsWorker;
- HermesLabWorker.

## EVIDENCE_CONTRACT

Cada técnica debe indicar qué evidencia espera.

Ejemplos:

Android:

- artifact_path;
- artifact_hash;
- build_log;
- validation_summary.

HackRF:

- iq_file_hash;
- waterfall_snapshot;
- frequency_observed;
- modulation_guess;
- signal_summary.

Scraping:

- extracted_rows;
- source_urls;
- normalized_json;
- export_path;
- errors.

Cloud:

- findings_count;
- critical_count;
- report_path;
- image_digest.

## USER_LOGIC_HOOK

Si falta lógica privada:

```python
raise ManualImplementationRequired(
    "IMPLEMENTACION_USUARIO_REQUERIDA: conecta aquí tu lógica privada."
)
```
