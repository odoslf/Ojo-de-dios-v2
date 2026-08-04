import json

import pytest

from app.contracts.evidence_contract import RESULT_MISSING_TOOL, RESULT_SUCCESS
from app.contracts.technique_contract import STATUS_READY_CONTROLLED, TechniqueExecutionContext
from app.core.errors import ContractError
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.registry_loader import load_registry_from_package
from app.modules.m15_cloud.techniques import (
    AwsReadOnlyConnectorTechnique,
    AzureReadOnlyConnectorTechnique,
    CloudIamReadOnlyAuditTechnique,
    CloudInventoryReadOnlyAuditTechnique,
    CloudMisconfigurationReportTechnique,
    ContainerImageReportReadOnlyAuditTechnique,
    GcpReadOnlyConnectorTechnique,
    KubernetesRbacReadOnlyAuditTechnique,
    KubernetesReadOnlyConnectorTechnique,
)


def _context(parameters: dict[str, object]) -> TechniqueExecutionContext:
    return TechniqueExecutionContext(target_id="target-1", run_id="run-1", mode="controlled", parameters=parameters, confirmed=True)


def test_m15_registers_only_readonly_passive_techniques() -> None:
    registry = load_registry_from_package("app.modules.m15_cloud")

    assert registry.list_ids() == [
        "cloud.readonly.aws_connector",
        "cloud.readonly.azure_connector",
        "cloud.readonly.container_image_report_audit",
        "cloud.readonly.gcp_connector",
        "cloud.readonly.iam_policy_audit",
        "cloud.readonly.inventory_audit",
        "cloud.readonly.k8s_rbac_audit",
        "cloud.readonly.kubernetes_connector",
        "cloud.readonly.misconfiguration_report",
    ]
    for technique_cls in registry.list_all():
        technique = technique_cls()
        technique.validate_metadata()
        assert technique.module_id == "m15_cloud"
        assert technique.permission_level == PERMISSION_PASSIVE
        assert technique.implementation_status == STATUS_READY_CONTROLLED
        assert technique.requires_user_implementation is False
        assert technique.requires_network is technique.technique_id.endswith("_connector")
        assert "readonly" in technique.technique_id
        assert not any(word in technique.technique_id for word in ("deploy", "steal", "breakout", "persist", "execute_command"))


def test_cloud_inventory_audit_flags_public_and_unauthenticated_assets_without_mutation() -> None:
    result = CloudInventoryReadOnlyAuditTechnique().execute(
        _context(
            {
                "inventory_json": [
                    {"provider": "container", "resource_type": "docker_api", "resource_id": "dock-1", "exposure": "public", "attributes": {"auth_required": False}},
                    {"provider": "aws", "resource_type": "s3_bucket", "resource_id": "bucket-1", "exposure": "public", "attributes": {"token": "redacted"}},
                ]
            }
        )
    )
    content = result.evidence[0].content
    rule_ids = {finding["rule_id"] for finding in content["posture_findings"]}

    assert result.result_status == RESULT_SUCCESS
    assert {"public_exposure", "docker_api_without_auth", "public_storage_bucket"} <= rule_ids
    assert content["cloud_inventory_summary"]["redacted_attribute_count"] == 1
    assert content["remote_collection_performed"] is False
    assert content["mutation_performed"] is False


def test_iam_policy_audit_flags_wildcards_and_sensitive_actions() -> None:
    result = CloudIamReadOnlyAuditTechnique().execute(
        _context({"policy_json": {"Statement": [{"Effect": "Allow", "Action": ["s3:*", "iam:PassRole"], "Resource": "*"}]}})
    )
    rule_ids = {finding["rule_id"] for finding in result.evidence[0].content["iam_findings"]}

    assert {"wildcard_action", "wildcard_resource", "privilege_sensitive_action"} == rule_ids
    assert result.evidence[0].content["mutation_performed"] is False


def test_kubernetes_rbac_audit_flags_cluster_admin_and_anonymous_subjects() -> None:
    result = KubernetesRbacReadOnlyAuditTechnique().execute(
        _context(
            {
                "rbac_json": [
                    {"kind": "ClusterRole", "metadata": {"name": "danger"}, "rules": [{"verbs": ["*"], "resources": ["*"]}]},
                    {"kind": "ClusterRoleBinding", "metadata": {"name": "anon"}, "subjects": [{"kind": "Group", "name": "system:anonymous"}]},
                ]
            }
        )
    )
    rule_ids = {finding["rule_id"] for finding in result.evidence[0].content["rbac_findings"]}

    assert rule_ids == {"cluster_admin_like_rule", "anonymous_subject"}
    assert result.evidence[0].content["remote_collection_performed"] is False


def test_container_image_report_audit_parses_existing_trivy_json_without_running_scanner() -> None:
    result = ContainerImageReportReadOnlyAuditTechnique().execute(
        _context(
            {
                "trivy_json": {
                    "Results": [
                        {
                            "Target": "nginx:latest",
                            "Vulnerabilities": [
                                {"VulnerabilityID": "CVE-1", "Severity": "CRITICAL", "PkgName": "openssl", "InstalledVersion": "1.0", "FixedVersion": "1.1"},
                                {"VulnerabilityID": "CVE-2", "Severity": "LOW", "PkgName": "zlib"},
                            ],
                        }
                    ]
                }
            }
        )
    )
    report = result.evidence[0].content["vulnerability_report"]

    assert report["high_or_critical_count"] == 1
    assert report["findings"][0]["vulnerability_id"] == "CVE-1"
    assert result.evidence[0].content["scanner_executed"] is False
    assert result.evidence[0].content["mutation_performed"] is False


def test_cloud_inventory_audit_accepts_path_input_and_wraps_invalid_assets(tmp_path) -> None:
    inventory_path = tmp_path / "inventory.json"
    inventory_path.write_text(
        json.dumps(
            {
                "assets": [
                    {
                        "provider": "kubernetes",
                        "resource_type": "api_server",
                        "resource_id": "cluster-1",
                        "exposure": "internal",
                        "attributes": {"anonymous_auth": "true"},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = CloudInventoryReadOnlyAuditTechnique().execute(_context({"inventory_path": str(inventory_path)}))

    assert result.result_status == RESULT_SUCCESS
    assert result.evidence[0].content["assets"][0]["provider"] == "kubernetes"
    assert result.evidence[0].content["remote_collection_performed"] is False

    with pytest.raises(ContractError, match="cloud inventory asset 0 is invalid"):
        CloudInventoryReadOnlyAuditTechnique().execute(
            _context(
                {
                    "inventory_json": [
                        {"provider": "unsupported", "resource_type": "bucket", "resource_id": "b-1", "exposure": "public"}
                    ]
                }
            )
        )


def test_iam_and_rbac_audits_normalize_case_without_remote_calls() -> None:
    iam_result = CloudIamReadOnlyAuditTechnique().execute(
        _context({"policy_json": [{"Effect": "Allow", "Action": ["S3:*", "IAM:CreateAccessKey"], "Resource": "*"}]})
    )
    iam_rule_ids = {finding["rule_id"] for finding in iam_result.evidence[0].content["iam_findings"]}

    assert iam_rule_ids == {"wildcard_action", "wildcard_resource", "privilege_sensitive_action"}
    assert iam_result.evidence[0].content["remote_collection_performed"] is False

    rbac_result = KubernetesRbacReadOnlyAuditTechnique().execute(
        _context(
            {
                "rbac_json": {
                    "items": [
                        {"kind": "Role", "metadata": {"name": "writer"}, "rules": [{"verbs": ["Patch"], "resources": ["pods"]}]},
                        {"kind": "RoleBinding", "metadata": {"name": "anon"}, "subjects": [{"kind": "group", "name": "system:anonymous"}]},
                    ]
                }
            }
        )
    )
    rbac_rule_ids = {finding["rule_id"] for finding in rbac_result.evidence[0].content["rbac_findings"]}

    assert rbac_rule_ids == {"mutation_verbs", "anonymous_subject"}
    assert rbac_result.evidence[0].content["mutation_performed"] is False


def test_cloud_readonly_connectors_report_missing_sdks_without_fake_success(monkeypatch) -> None:
    monkeypatch.setattr("app.modules.m15_cloud.techniques._import_optional", lambda package: None)

    cases = [
        (AwsReadOnlyConnectorTechnique(), {}),
        (GcpReadOnlyConnectorTechnique(), {}),
        (AzureReadOnlyConnectorTechnique(), {"subscription_id": "sub-1"}),
        (KubernetesReadOnlyConnectorTechnique(), {}),
    ]

    for technique, parameters in cases:
        result = technique.execute(_context(parameters))
        assert result.result_status == RESULT_MISSING_TOOL
        assert result.evidence == []
        assert result.raw_result["remote_collection_performed"] is False
        assert result.raw_result["mutation_performed"] is False


def test_aws_readonly_connector_uses_list_calls_and_normalizes_assets(monkeypatch) -> None:
    class FakeClient:
        def __init__(self, name):
            self.name = name

        def list_buckets(self):
            return {"Buckets": [{"Name": "bucket-a", "CreationDate": "2026-01-01"}]}

        def list_roles(self):
            return {"Roles": [{"RoleName": "ReadOnlyRole", "Arn": "arn:aws:iam::123:role/ReadOnlyRole"}]}

    class FakeSession:
        def __init__(self, profile_name=None, region_name=None):
            self.profile_name = profile_name
            self.region_name = region_name

        def client(self, name):
            return FakeClient(name)

    class FakeBoto3:
        Session = FakeSession

    monkeypatch.setattr("app.modules.m15_cloud.techniques._import_optional", lambda package: FakeBoto3 if package == "boto3" else None)

    result = AwsReadOnlyConnectorTechnique().execute(_context({"profile_name": "audit", "region_name": "us-east-1"}))
    content = result.evidence[0].content

    assert result.result_status == RESULT_SUCCESS
    assert content["remote_collection_performed"] is True
    assert content["mutation_performed"] is False
    assert content["readonly_api_calls"] == ["s3:list_buckets", "iam:list_roles"]
    assert {asset["resource_type"] for asset in content["assets"]} == {"s3_bucket", "iam_role"}


def test_cloud_misconfiguration_report_exports_findings_json(tmp_path) -> None:
    output_path = tmp_path / "m15_report.json"
    result = CloudMisconfigurationReportTechnique().execute(
        _context(
            {
                "output_path": output_path.as_posix(),
                "inventory_json": [
                    {"provider": "aws", "resource_type": "s3_bucket", "resource_id": "bucket-public", "exposure": "public", "attributes": {}}
                ],
                "policy_json": {"Statement": [{"Effect": "Allow", "Action": "iam:PassRole", "Resource": "*"}]},
                "rbac_json": [{"kind": "ClusterRole", "metadata": {"name": "admin"}, "rules": [{"verbs": ["*"], "resources": ["*"]}]}],
            }
        )
    )
    exported = json.loads(output_path.read_text(encoding="utf-8"))
    rule_ids = {finding["rule_id"] for finding in exported["posture_findings"]}

    assert result.result_status == RESULT_SUCCESS
    assert result.evidence[0].content["report_path"] == output_path.as_posix()
    assert exported["schema_version"] == "m15.misconfiguration_report.v1"
    assert {"public_storage_bucket", "privilege_sensitive_action", "cluster_admin_like_rule"} <= rule_ids
    assert exported["report_only"] is True
    assert exported["mutation_performed"] is False
    assert exported["remediation_performed"] is False


def test_cloud_misconfiguration_report_requires_json_output_and_input(tmp_path) -> None:
    with pytest.raises(ContractError, match="At least one"):
        CloudMisconfigurationReportTechnique().execute(_context({"output_path": (tmp_path / "report.json").as_posix()}))
    with pytest.raises(ContractError, match="must end with .json"):
        CloudMisconfigurationReportTechnique().execute(_context({"output_path": (tmp_path / "report.txt").as_posix(), "policy_json": {"Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}}))
