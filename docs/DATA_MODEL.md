# DATA MODEL — OJO DE DIOS

## Base de datos

SQLite primero.
PostgreSQL preparado.

## Tablas principales

- users
- roles
- settings
- targets
- target_fingerprints
- jobs
- job_events
- technique_runs
- techniques_snapshot
- evidence
- evidence_files
- scoring_history
- version_locks
- tool_health
- ai_plans
- ai_messages
- service_fingerprints
- attack_surface_graphs
- attack_surface_nodes
- attack_surface_edges
- technique_matches
- attack_paths
- attack_path_steps
- cve_candidates
- hermes_proposals
- hermes_skills
- hermes_approvals
- audit_log
- plugins
- plugin_versions
- plugin_reviews

## Evidence

Cada evidence debe guardar:

- evidence_id;
- job_id;
- run_id;
- target_id;
- module_id;
- technique_id;
- status;
- quality;
- summary;
- files;
- hashes;
- timestamps;
- demo;
- dry_run;
- manual_required;
- raw_output_path;
- normalized_output_json.

## Jobs

Cada job debe guardar:

- job_id;
- target_id;
- created_by;
- mode;
- status;
- selected_modules;
- selected_techniques;
- permissions_snapshot;
- started_at;
- finished_at;
- stop_reason.

## ServiceFingerprint

Debe guardar:

- target_id;
- host;
- ip;
- port;
- protocol;
- service_name;
- product;
- version;
- cpe;
- confidence;
- sources;
- evidence_ids;
- tags;
- first_seen_at;
- last_seen_at.

## Hermes Proposal

Debe guardar:

- proposal_id;
- title;
- module_id;
- technique_id;
- proposal_type;
- status;
- risk_level;
- files_created;
- files_modified;
- tests_created;
- evidence_path;
- diff_path;
- mistral_review_path;
- approval_status;
- promoted_at;
- rollback_path.
