"""Read-only M15 cloud, container and Kubernetes posture techniques.

Ronda 17 deliberately implements defensive/read-only auditing only.  These
techniques consume operator-supplied inventories, IAM/RBAC policies and scanner
reports; they never mutate cloud resources, never deploy workloads, never extract
secrets, and never contact cloud metadata endpoints.
"""

from __future__ import annotations

import json
import importlib
import os
from pathlib import Path
from typing import Any

from app.contracts.evidence_contract import EVIDENCE_QUALITY_HIGH, EVIDENCE_QUALITY_MEDIUM, EvidenceRecord, RESULT_MISSING_TOOL, RESULT_SUCCESS
from app.contracts.technique_contract import BaseTechnique, STATUS_READY_CONTROLLED, TechniqueExecutionContext, TechniqueExecutionResult
from app.core.errors import ContractError
from app.core.technique_evidence_utils import stable_evidence_id, utc_now_iso
from app.core.m15_cloud_inventory import CloudAsset, cloud_asset_from_payload, summarize_cloud_assets
from app.core.permission_levels import PERMISSION_PASSIVE

M15_MODULE_ID = "m15_cloud"
_SECRET_KEYS = ("secret", "password", "token", "credential", "private_key", "access_key")


def _evidence(context: TechniqueExecutionContext, technique_id: str, suffix: str, summary: str, content: dict[str, Any], *, quality: str = EVIDENCE_QUALITY_HIGH) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=stable_evidence_id(context.run_id, technique_id, suffix),
        run_id=context.run_id,
        target_id=context.target_id,
        technique_id=technique_id,
        module_id=M15_MODULE_ID,
        evidence_type=suffix,
        quality=quality,
        summary=summary,
        content=content,
        source="m15-readonly-audit",
        demo=False,
        real_execution=True,
        created_at=utc_now_iso(),
    )


def _read_json_parameter(parameters: dict[str, Any], content_name: str, path_name: str) -> Any:
    if parameters.get(content_name) is not None:
        raw = parameters[content_name]
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except json.JSONDecodeError as error:
                raise ContractError(f"{content_name} must be valid JSON when provided as text.") from error
        return raw
    path_value = str(parameters.get(path_name, "")).strip()
    if not path_value:
        raise ContractError(f"{content_name} or {path_name} is required.")
    path = Path(path_value)
    if not path.is_file():
        raise ContractError(f"{path_name} does not point to a readable file.")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ContractError(f"{path_name} must contain valid JSON.") from error


def _asset_dicts(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("assets"), list):
        raw_assets = payload["assets"]
    elif isinstance(payload, list):
        raw_assets = payload
    else:
        raise ContractError("cloud inventory must be a list or an object with assets list.")
    assets: list[dict[str, Any]] = []
    for item in raw_assets:
        if not isinstance(item, dict):
            raise ContractError("cloud inventory entries must be objects.")
        assets.append(dict(item))
    if not assets:
        raise ContractError("cloud inventory must include at least one asset.")
    return assets


def _normalize_assets(payload: Any) -> list[CloudAsset]:
    assets: list[CloudAsset] = []
    for index, item in enumerate(_asset_dicts(payload)):
        try:
            assets.append(cloud_asset_from_payload(item))
        except ValueError as error:
            raise ContractError(f"cloud inventory asset {index} is invalid: {error}") from error
    return assets


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            if any(part in str(key).casefold() for part in _SECRET_KEYS):
                return True
            if _contains_sensitive_key(nested):
                return True
    if isinstance(value, list):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _asset_findings(asset: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    provider = str(asset.get("provider", "other")).casefold()
    resource_type = str(asset.get("resource_type", "unknown")).casefold()
    exposure = str(asset.get("exposure", "unknown")).casefold()
    attributes = asset.get("attributes", {}) if isinstance(asset.get("attributes", {}), dict) else {}
    ref = str(asset.get("asset_id") or asset.get("resource_id") or "unknown")
    if exposure == "public":
        findings.append({"severity": "high", "asset_ref": ref, "rule_id": "public_exposure", "message": "Asset is marked public in supplied inventory."})
    if provider == "container" and resource_type in {"docker_api", "docker"} and attributes.get("auth_required") is False:
        findings.append({"severity": "high", "asset_ref": ref, "rule_id": "docker_api_without_auth", "message": "Docker API inventory says authentication is not required."})
    if provider == "kubernetes" and str(attributes.get("anonymous_auth", "")).lower() == "true":
        findings.append({"severity": "high", "asset_ref": ref, "rule_id": "k8s_anonymous_auth", "message": "Kubernetes asset reports anonymous authentication enabled."})
    if provider == "aws" and "bucket" in resource_type and exposure == "public":
        findings.append({"severity": "high", "asset_ref": ref, "rule_id": "public_storage_bucket", "message": "Cloud storage bucket is public."})
    if _contains_sensitive_key(attributes):
        findings.append({"severity": "medium", "asset_ref": ref, "rule_id": "sensitive_attribute_key", "message": "Supplied attributes contain sensitive-looking key names; values should remain redacted."})
    return findings


def _flatten_statements(policy: Any) -> list[dict[str, Any]]:
    if isinstance(policy, dict) and isinstance(policy.get("Statement"), list):
        raw = policy["Statement"]
    elif isinstance(policy, dict) and isinstance(policy.get("statements"), list):
        raw = policy["statements"]
    elif isinstance(policy, list):
        raw = policy
    else:
        raise ContractError("IAM policy must include a Statement/statements list or be a statement list.")
    statements = [dict(item) for item in raw if isinstance(item, dict)]
    if not statements:
        raise ContractError("IAM policy must include at least one statement object.")
    return statements


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _iam_findings(statements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for index, statement in enumerate(statements):
        effect = str(statement.get("Effect") or statement.get("effect") or "").casefold()
        actions = _as_list(statement.get("Action", statement.get("action")))
        resources = _as_list(statement.get("Resource", statement.get("resource")))
        normalized_actions = [action.casefold() for action in actions]
        normalized_resources = [resource.casefold() for resource in resources]
        if effect != "allow":
            continue
        if "*" in normalized_actions or any(action.endswith(":*") for action in normalized_actions):
            findings.append({"severity": "high", "statement": index, "rule_id": "wildcard_action", "message": "Allow statement grants wildcard actions."})
        if "*" in normalized_resources:
            findings.append({"severity": "medium", "statement": index, "rule_id": "wildcard_resource", "message": "Allow statement applies to all resources."})
        if any(action in {"iam:passrole", "sts:assumerole", "iam:createaccesskey"} for action in normalized_actions):
            findings.append({"severity": "high", "statement": index, "rule_id": "privilege_sensitive_action", "message": "Allow statement grants privilege-sensitive IAM action."})
    return findings


def _rbac_findings(payload: Any) -> list[dict[str, Any]]:
    items = payload.get("items", payload) if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        raise ContractError("Kubernetes RBAC input must be a list or an object with items.")
    findings: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind", "unknown"))
        metadata = item.get("metadata", {}) if isinstance(item.get("metadata", {}), dict) else {}
        name = str(metadata.get("name") or item.get("name") or f"item-{index}")
        rules = item.get("rules", [])
        subjects = item.get("subjects", [])
        if isinstance(rules, list):
            for rule in rules:
                if not isinstance(rule, dict):
                    continue
                verbs = [verb.casefold() for verb in _as_list(rule.get("verbs"))]
                resources = [resource.casefold() for resource in _as_list(rule.get("resources"))]
                if "*" in verbs and "*" in resources:
                    findings.append({"severity": "critical", "kind": kind, "name": name, "rule_id": "cluster_admin_like_rule", "message": "RBAC rule grants all verbs over all resources."})
                elif any(verb in {"create", "update", "patch", "delete", "deletecollection"} for verb in verbs):
                    findings.append({"severity": "medium", "kind": kind, "name": name, "rule_id": "mutation_verbs", "message": "RBAC rule includes mutation verbs."})
        if isinstance(subjects, list):
            for subject in subjects:
                if isinstance(subject, dict) and str(subject.get("kind", "")).casefold() == "group" and subject.get("name") == "system:anonymous":
                    findings.append({"severity": "high", "kind": kind, "name": name, "rule_id": "anonymous_subject", "message": "RBAC binding includes system:anonymous."})
    return findings


def _trivy_findings(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise ContractError("Trivy report must be a JSON object.")
    findings: list[dict[str, Any]] = []
    for result in payload.get("Results", []):
        if not isinstance(result, dict):
            continue
        target = str(result.get("Target") or "unknown")
        for vulnerability in result.get("Vulnerabilities", []) or []:
            if not isinstance(vulnerability, dict):
                continue
            severity = str(vulnerability.get("Severity") or "UNKNOWN").lower()
            if severity in {"critical", "high"}:
                findings.append({
                    "severity": severity,
                    "target": target,
                    "vulnerability_id": str(vulnerability.get("VulnerabilityID") or "unknown"),
                    "package_name": str(vulnerability.get("PkgName") or "unknown"),
                    "installed_version": str(vulnerability.get("InstalledVersion") or "unknown"),
                    "fixed_version": str(vulnerability.get("FixedVersion") or ""),
                })
    return findings


class CloudInventoryReadOnlyAuditTechnique(BaseTechnique):
    technique_id = "cloud.readonly.inventory_audit"
    module_id = M15_MODULE_ID
    display_name = "Read-only cloud inventory audit"
    description = "Audit supplied cloud/container/Kubernetes inventory exports for exposure and posture issues without remote calls."
    tool_name = "internal_cloud_inventory_auditor"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = []
    optional_inputs = ["inventory_json", "inventory_path"]
    expected_evidence = ["cloud_inventory_summary", "posture_findings", "normalized_json"]
    input_schema = {"inventory_json": {"type": "object"}, "inventory_path": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "inventory_json", "label": "Cloud inventory JSON", "type": "textarea"}]
    success_markers = ["posture_findings", "cloud_inventory_summary"]
    failure_markers = ["invalid_inventory"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"cloud_inventory_summary": "dict", "posture_findings": "list"}
    version_lock_id = "m15_cloud/read-only-inventory-audit"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        assets = _normalize_assets(_read_json_parameter(context.parameters, "inventory_json", "inventory_path"))
        asset_dicts = [asset.to_dict() for asset in assets]
        findings = [finding for asset in asset_dicts for finding in _asset_findings(asset)]
        content = {
            "cloud_inventory_summary": summarize_cloud_assets(assets),
            "posture_findings": findings,
            "assets": asset_dicts,
            "remote_collection_performed": False,
            "mutation_performed": False,
        }
        evidence = _evidence(context, self.technique_id, "cloud_inventory_posture", "Read-only cloud inventory posture audit completed.", content)
        return TechniqueExecutionResult(self.technique_id, M15_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class CloudIamReadOnlyAuditTechnique(BaseTechnique):
    technique_id = "cloud.readonly.iam_policy_audit"
    module_id = M15_MODULE_ID
    display_name = "Read-only IAM policy audit"
    description = "Analyze supplied IAM policy JSON for wildcard and privilege-sensitive grants without using cloud credentials."
    tool_name = "internal_iam_policy_auditor"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = []
    optional_inputs = ["policy_json", "policy_path"]
    expected_evidence = ["iam_findings", "normalized_json"]
    input_schema = {"policy_json": {"type": "object"}, "policy_path": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "policy_json", "label": "IAM policy JSON", "type": "textarea"}]
    success_markers = ["iam_findings"]
    failure_markers = ["invalid_policy"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"iam_findings": "list"}
    version_lock_id = "m15_cloud/read-only-iam-policy-audit"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        statements = _flatten_statements(_read_json_parameter(context.parameters, "policy_json", "policy_path"))
        findings = _iam_findings(statements)
        content = {"statement_count": len(statements), "iam_findings": findings, "remote_collection_performed": False, "mutation_performed": False}
        evidence = _evidence(context, self.technique_id, "iam_policy_posture", "Read-only IAM policy audit completed.", content)
        return TechniqueExecutionResult(self.technique_id, M15_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class KubernetesRbacReadOnlyAuditTechnique(BaseTechnique):
    technique_id = "cloud.readonly.k8s_rbac_audit"
    module_id = M15_MODULE_ID
    display_name = "Read-only Kubernetes RBAC audit"
    description = "Analyze supplied Kubernetes RBAC JSON for broad or anonymous permissions without calling the cluster."
    tool_name = "internal_k8s_rbac_auditor"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = []
    optional_inputs = ["rbac_json", "rbac_path"]
    expected_evidence = ["rbac_findings", "normalized_json"]
    input_schema = {"rbac_json": {"type": "object"}, "rbac_path": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "rbac_json", "label": "Kubernetes RBAC JSON", "type": "textarea"}]
    success_markers = ["rbac_findings"]
    failure_markers = ["invalid_rbac"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"rbac_findings": "list"}
    version_lock_id = "m15_cloud/read-only-k8s-rbac-audit"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        findings = _rbac_findings(_read_json_parameter(context.parameters, "rbac_json", "rbac_path"))
        content = {"rbac_findings": findings, "remote_collection_performed": False, "mutation_performed": False}
        evidence = _evidence(context, self.technique_id, "k8s_rbac_posture", "Read-only Kubernetes RBAC audit completed.", content)
        return TechniqueExecutionResult(self.technique_id, M15_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class ContainerImageReportReadOnlyAuditTechnique(BaseTechnique):
    technique_id = "cloud.readonly.container_image_report_audit"
    module_id = M15_MODULE_ID
    display_name = "Read-only container image report audit"
    description = "Parse an existing Trivy-style JSON report and summarize high/critical image vulnerabilities without running scanners."
    tool_name = "trivy_json_parser"
    recommended_version = "Trivy JSON schema"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = []
    optional_inputs = ["trivy_json", "trivy_path"]
    expected_evidence = ["vulnerability_report", "normalized_json"]
    input_schema = {"trivy_json": {"type": "object"}, "trivy_path": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "trivy_json", "label": "Trivy report JSON", "type": "textarea"}]
    success_markers = ["vulnerability_report"]
    failure_markers = ["invalid_trivy_report"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"vulnerability_report": "dict"}
    version_lock_id = "m15_cloud/read-only-container-image-report-audit"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        findings = _trivy_findings(_read_json_parameter(context.parameters, "trivy_json", "trivy_path"))
        content = {
            "vulnerability_report": {"high_or_critical_count": len(findings), "findings": findings},
            "remote_collection_performed": False,
            "scanner_executed": False,
            "mutation_performed": False,
        }
        evidence = _evidence(context, self.technique_id, "container_image_report", "Read-only container image vulnerability report audit completed.", content, quality=EVIDENCE_QUALITY_MEDIUM)
        return TechniqueExecutionResult(self.technique_id, M15_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


def _missing_connector_result(technique_id: str, missing_packages: list[str]) -> TechniqueExecutionResult:
    return TechniqueExecutionResult(
        technique_id=technique_id,
        module_id=M15_MODULE_ID,
        result_status=RESULT_MISSING_TOOL,
        summary=f"Missing read-only connector package(s): {', '.join(missing_packages)}.",
        evidence=[],
        raw_result={"missing_packages": missing_packages, "remote_collection_performed": False, "mutation_performed": False, "real_execution": False},
    )


def _import_optional(package_name: str):
    try:
        return importlib.import_module(package_name)
    except ImportError:
        return None


class AwsReadOnlyConnectorTechnique(BaseTechnique):
    technique_id = "cloud.readonly.aws_connector"
    module_id = M15_MODULE_ID
    display_name = "AWS read-only connector"
    description = "Collect AWS S3/IAM inventory with boto3 read-only list calls; never mutates resources."
    tool_name = "boto3"
    recommended_version = "boto3 1.x"
    runtime = "python_lib"
    worker = "CloudWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs: list[str] = []
    optional_inputs = ["profile_name", "region_name", "include_iam"]
    expected_evidence = ["assets", "cloud_inventory_summary", "normalized_json"]
    input_schema = {"profile_name": {"type": "string"}, "region_name": {"type": "string"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "profile_name", "label": "AWS profile", "type": "text"}]
    success_markers = ["assets"]
    failure_markers = ["missing_boto3", "aws_readonly_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"assets": "list", "cloud_inventory_summary": "dict"}
    version_lock_id = "m15_cloud/aws-readonly-connector"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        boto3 = _import_optional("boto3")
        if boto3 is None:
            return _missing_connector_result(self.technique_id, ["boto3"])
        profile_name = str(context.parameters.get("profile_name", "")).strip() or None
        region_name = str(context.parameters.get("region_name", "")).strip() or None
        session = boto3.Session(profile_name=profile_name, region_name=region_name)
        assets = []
        for bucket in session.client("s3").list_buckets().get("Buckets", []):
            name = str(bucket.get("Name"))
            assets.append({"provider": "aws", "resource_type": "s3_bucket", "resource_id": name, "region": region_name or "global", "exposure": "unknown", "attributes": {"creation_date": str(bucket.get("CreationDate", ""))}})
        if bool(context.parameters.get("include_iam", True)):
            for role in session.client("iam").list_roles().get("Roles", []):
                assets.append({"provider": "aws", "resource_type": "iam_role", "resource_id": str(role.get("RoleName")), "region": "global", "exposure": "internal", "attributes": {"arn": role.get("Arn")}})
        normalized_assets = [cloud_asset_from_payload(asset).to_dict() for asset in assets]
        content = {"assets": normalized_assets, "cloud_inventory_summary": summarize_cloud_assets([cloud_asset_from_payload(asset) for asset in assets]), "remote_collection_performed": True, "mutation_performed": False, "readonly_api_calls": ["s3:list_buckets", "iam:list_roles"]}
        evidence = _evidence(context, self.technique_id, "aws_readonly_inventory", "AWS read-only connector inventory completed.", content)
        return TechniqueExecutionResult(self.technique_id, M15_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class GcpReadOnlyConnectorTechnique(BaseTechnique):
    technique_id = "cloud.readonly.gcp_connector"
    module_id = M15_MODULE_ID
    display_name = "GCP read-only connector"
    description = "Collect GCP Cloud Storage inventory with google-cloud-storage read-only list calls."
    tool_name = "google-cloud-storage"
    recommended_version = "google-cloud-storage 2.x"
    runtime = "python_lib"
    worker = "CloudWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs: list[str] = []
    optional_inputs = ["project_id"]
    expected_evidence = ["assets", "cloud_inventory_summary", "normalized_json"]
    input_schema = {"project_id": {"type": "string"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "project_id", "label": "GCP project", "type": "text"}]
    success_markers = ["assets"]
    failure_markers = ["missing_google_cloud_storage", "gcp_readonly_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"assets": "list", "cloud_inventory_summary": "dict"}
    version_lock_id = "m15_cloud/gcp-readonly-connector"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        storage = _import_optional("google.cloud.storage")
        if storage is None:
            return _missing_connector_result(self.technique_id, ["google-cloud-storage"])
        project_id = str(context.parameters.get("project_id", "")).strip() or None
        client = storage.Client(project=project_id)
        assets = []
        for bucket in client.list_buckets():
            assets.append({"provider": "gcp", "resource_type": "storage_bucket", "resource_id": str(bucket.name), "region": str(getattr(bucket, "location", "global") or "global"), "exposure": "unknown", "attributes": {"storage_class": getattr(bucket, "storage_class", None)}})
        normalized_assets = [cloud_asset_from_payload(asset).to_dict() for asset in assets]
        content = {"assets": normalized_assets, "cloud_inventory_summary": summarize_cloud_assets([cloud_asset_from_payload(asset) for asset in assets]), "remote_collection_performed": True, "mutation_performed": False, "readonly_api_calls": ["storage:list_buckets"]}
        evidence = _evidence(context, self.technique_id, "gcp_readonly_inventory", "GCP read-only connector inventory completed.", content)
        return TechniqueExecutionResult(self.technique_id, M15_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class AzureReadOnlyConnectorTechnique(BaseTechnique):
    technique_id = "cloud.readonly.azure_connector"
    module_id = M15_MODULE_ID
    display_name = "Azure read-only connector"
    description = "Collect Azure resource inventory with azure SDK read-only list calls."
    tool_name = "azure-mgmt-resource"
    recommended_version = "azure-identity 1.x + azure-mgmt-resource 23.x"
    runtime = "python_lib"
    worker = "CloudWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["subscription_id"]
    optional_inputs = []
    expected_evidence = ["assets", "cloud_inventory_summary", "normalized_json"]
    input_schema = {"subscription_id": {"type": "string"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "subscription_id", "label": "Azure subscription", "type": "text"}]
    success_markers = ["assets"]
    failure_markers = ["missing_azure_sdk", "azure_readonly_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"assets": "list", "cloud_inventory_summary": "dict"}
    version_lock_id = "m15_cloud/azure-readonly-connector"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        identity = _import_optional("azure.identity")
        resources = _import_optional("azure.mgmt.resource")
        if identity is None or resources is None:
            return _missing_connector_result(self.technique_id, ["azure-identity", "azure-mgmt-resource"])
        subscription_id = str(context.parameters.get("subscription_id", "")).strip()
        if not subscription_id:
            raise ContractError("subscription_id is required.")
        credential = identity.DefaultAzureCredential()
        client = resources.ResourceManagementClient(credential, subscription_id)
        assets = []
        for resource in client.resources.list():
            assets.append({"provider": "azure", "resource_type": str(getattr(resource, "type", "resource")), "resource_id": str(getattr(resource, "id", getattr(resource, "name", "unknown"))), "region": str(getattr(resource, "location", "global") or "global"), "exposure": "unknown", "attributes": {"name": getattr(resource, "name", None)}})
        normalized_assets = [cloud_asset_from_payload(asset).to_dict() for asset in assets]
        content = {"assets": normalized_assets, "cloud_inventory_summary": summarize_cloud_assets([cloud_asset_from_payload(asset) for asset in assets]), "remote_collection_performed": True, "mutation_performed": False, "readonly_api_calls": ["resources:list"]}
        evidence = _evidence(context, self.technique_id, "azure_readonly_inventory", "Azure read-only connector inventory completed.", content)
        return TechniqueExecutionResult(self.technique_id, M15_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class KubernetesReadOnlyConnectorTechnique(BaseTechnique):
    technique_id = "cloud.readonly.kubernetes_connector"
    module_id = M15_MODULE_ID
    display_name = "Kubernetes read-only connector"
    description = "Collect Kubernetes namespace/pod inventory with read-only list calls using the Kubernetes Python client."
    tool_name = "kubernetes"
    recommended_version = "kubernetes 30.x"
    runtime = "python_lib"
    worker = "CloudWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs: list[str] = []
    optional_inputs = ["kubeconfig_path"]
    expected_evidence = ["assets", "cloud_inventory_summary", "normalized_json"]
    input_schema = {"kubeconfig_path": {"type": "string"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "kubeconfig_path", "label": "Kubeconfig", "type": "text"}]
    success_markers = ["assets"]
    failure_markers = ["missing_kubernetes_client", "kubernetes_readonly_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"assets": "list", "cloud_inventory_summary": "dict"}
    version_lock_id = "m15_cloud/kubernetes-readonly-connector"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        kube_client = _import_optional("kubernetes.client")
        kube_config = _import_optional("kubernetes.config")
        if kube_client is None or kube_config is None:
            return _missing_connector_result(self.technique_id, ["kubernetes"])
        kubeconfig_path = str(context.parameters.get("kubeconfig_path", "")).strip() or None
        if kubeconfig_path:
            kube_config.load_kube_config(config_file=kubeconfig_path)
        else:
            kube_config.load_kube_config()
        api = kube_client.CoreV1Api()
        assets = []
        for namespace in api.list_namespace().items:
            name = namespace.metadata.name
            assets.append({"provider": "kubernetes", "resource_type": "namespace", "resource_id": name, "region": "cluster", "exposure": "internal", "attributes": {"labels": getattr(namespace.metadata, "labels", {})}})
        for pod in api.list_pod_for_all_namespaces().items:
            assets.append({"provider": "kubernetes", "resource_type": "pod", "resource_id": f"{pod.metadata.namespace}/{pod.metadata.name}", "region": "cluster", "exposure": "internal", "attributes": {"namespace": pod.metadata.namespace, "node_name": getattr(pod.spec, "node_name", None)}})
        normalized_assets = [cloud_asset_from_payload(asset).to_dict() for asset in assets]
        content = {"assets": normalized_assets, "cloud_inventory_summary": summarize_cloud_assets([cloud_asset_from_payload(asset) for asset in assets]), "remote_collection_performed": True, "mutation_performed": False, "readonly_api_calls": ["corev1:list_namespace", "corev1:list_pod_for_all_namespaces"]}
        evidence = _evidence(context, self.technique_id, "kubernetes_readonly_inventory", "Kubernetes read-only connector inventory completed.", content)
        return TechniqueExecutionResult(self.technique_id, M15_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


def _optional_json_parameter(parameters: dict[str, Any], content_name: str, path_name: str) -> Any | None:
    if parameters.get(content_name) is not None or str(parameters.get(path_name, "")).strip():
        return _read_json_parameter(parameters, content_name, path_name)
    return None


def _safe_report_path(parameters: dict[str, Any]) -> Path:
    raw_path = str(parameters.get("output_path", "")).strip()
    if not raw_path:
        raise ContractError("output_path is required.")
    path = Path(raw_path)
    if path.exists() and path.is_dir():
        raise ContractError("output_path must be a file path, not a directory.")
    if path.suffix.lower() != ".json":
        raise ContractError("output_path must end with .json.")
    return path


class CloudMisconfigurationReportTechnique(BaseTechnique):
    technique_id = "cloud.readonly.misconfiguration_report"
    module_id = M15_MODULE_ID
    display_name = "Read-only cloud misconfiguration report"
    description = "Combine supplied cloud inventory, IAM and Kubernetes RBAC data into an exportable findings report without remediation or mutation."
    tool_name = "internal_cloud_misconfiguration_reporter"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["output_path"]
    optional_inputs = ["inventory_json", "inventory_path", "policy_json", "policy_path", "rbac_json", "rbac_path"]
    expected_evidence = ["report_path", "posture_findings", "finding_summary", "normalized_json"]
    input_schema = {"output_path": {"type": "string"}, "inventory_json": {"type": "object"}, "policy_json": {"type": "object"}, "rbac_json": {"type": "object"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "output_path", "label": "Report JSON path", "type": "text"}]
    success_markers = ["report_path", "posture_findings"]
    failure_markers = ["invalid_report_input", "invalid_output_path"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"report_path": "string", "posture_findings": "list", "finding_summary": "dict"}
    version_lock_id = "m15_cloud/read-only-misconfiguration-report"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        output_path = _safe_report_path(context.parameters)
        findings: list[dict[str, Any]] = []
        assets_payload = _optional_json_parameter(context.parameters, "inventory_json", "inventory_path")
        assets: list[CloudAsset] = []
        if assets_payload is not None:
            assets = _normalize_assets(assets_payload)
            for asset in [item.to_dict() for item in assets]:
                findings.extend(_asset_findings(asset))
        policy_payload = _optional_json_parameter(context.parameters, "policy_json", "policy_path")
        if policy_payload is not None:
            findings.extend(_iam_findings(_flatten_statements(policy_payload)))
        rbac_payload = _optional_json_parameter(context.parameters, "rbac_json", "rbac_path")
        if rbac_payload is not None:
            findings.extend(_rbac_findings(rbac_payload))
        if assets_payload is None and policy_payload is None and rbac_payload is None:
            raise ContractError("At least one of inventory_json/policy_json/rbac_json or corresponding path inputs is required.")
        summary: dict[str, Any] = {"finding_count": len(findings), "by_severity": {}, "by_rule_id": {}}
        for finding in findings:
            severity = str(finding.get("severity") or "unknown")
            rule_id = str(finding.get("rule_id") or "unknown")
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            summary["by_rule_id"][rule_id] = summary["by_rule_id"].get(rule_id, 0) + 1
        report = {
            "schema_version": "m15.misconfiguration_report.v1",
            "module_id": M15_MODULE_ID,
            "finding_summary": summary,
            "posture_findings": findings,
            "cloud_inventory_summary": summarize_cloud_assets(assets) if assets else None,
            "report_only": True,
            "remote_collection_performed": False,
            "mutation_performed": False,
            "remediation_performed": False,
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
        temporary_path.write_text(json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary_path.replace(output_path)
        content = {"report_path": output_path.as_posix(), **report}
        evidence = _evidence(context, self.technique_id, "cloud_misconfiguration_report", "Read-only cloud misconfiguration report exported.", content)
        return TechniqueExecutionResult(self.technique_id, M15_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)
