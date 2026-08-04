"""Connector, AI, panel and Hermes contract tests."""

import pytest

from app.contracts.ai_contract import AIPlan, AIPlanStep, validate_ai_plan
from app.contracts.hermes_contract import (
    HERMES_STATUS_APPROVED_BY_USER,
    HERMES_STATUS_DRAFT,
    HERMES_STATUS_PROMOTED,
    HermesSkillContract,
    validate_hermes_skill_contract,
)
from app.contracts.manual_required import ManualImplementationRequired
from app.contracts.panel_contract import PanelField, TechniquePanelSchema, validate_panel_schema
from app.contracts.tool_connector import BaseToolConnector, ToolExecutionRequest
from app.core.errors import ContractError


def test_base_tool_connector_execute_requires_manual_implementation() -> None:
    connector = BaseToolConnector()
    request = ToolExecutionRequest(tool_name="tool", tool_version="1", runtime="local")

    with pytest.raises(ManualImplementationRequired):
        connector.execute(request)


def test_validate_ai_plan_accepts_valid_plan() -> None:
    plan = AIPlan(
        intent="inspect",
        target_type="demo-target",
        target_value="target-1",
        confidence=0.8,
        risk_score=0.2,
        recommended_plan=[
            AIPlanStep(
                step=1,
                technique_id="technique-1",
                module_id="module-1",
                priority=0.9,
                reason="reason",
            )
        ],
    )

    validate_ai_plan(plan)


def test_validate_ai_plan_rejects_confidence_above_one() -> None:
    plan = AIPlan(
        intent="inspect",
        target_type="demo-target",
        target_value="target-1",
        confidence=1.1,
    )

    with pytest.raises(ContractError):
        validate_ai_plan(plan)


def test_validate_panel_schema_accepts_valid_schema() -> None:
    schema = TechniquePanelSchema(
        technique_id="technique-1",
        module_id="module-1",
        fields=[PanelField(name="field", label="Field", field_type="text")],
    )

    validate_panel_schema(schema)


def test_validate_panel_schema_rejects_field_without_name() -> None:
    schema = TechniquePanelSchema(
        technique_id="technique-1",
        module_id="module-1",
        fields=[PanelField(name="", label="Field", field_type="text")],
    )

    with pytest.raises(ContractError):
        validate_panel_schema(schema)


def test_validate_hermes_skill_contract_accepts_draft() -> None:
    skill = HermesSkillContract(
        skill_id="skill-1",
        name="Skill",
        version="0.1.0",
        module_id="module-1",
        description="Draft skill",
        status=HERMES_STATUS_DRAFT,
    )

    validate_hermes_skill_contract(skill)


def test_validate_hermes_skill_contract_rejects_invalid_status() -> None:
    skill = HermesSkillContract(
        skill_id="skill-1",
        name="Skill",
        version="0.1.0",
        module_id="module-1",
        description="Draft skill",
        status="invalid",
    )

    with pytest.raises(ContractError):
        validate_hermes_skill_contract(skill)


def test_validate_hermes_skill_contract_rejects_promotion_before_approval() -> None:
    skill = HermesSkillContract(
        skill_id="skill-1",
        name="Skill",
        version="0.1.0",
        module_id="module-1",
        description="Draft skill",
        status=HERMES_STATUS_DRAFT,
        promotion_allowed=True,
    )

    with pytest.raises(ContractError):
        validate_hermes_skill_contract(skill)


def test_validate_hermes_skill_contract_allows_promotion_flag_only_when_approved() -> None:
    skill = HermesSkillContract(
        skill_id="skill-1",
        name="Skill",
        version="0.1.0",
        module_id="module-1",
        description="Approved skill",
        status=HERMES_STATUS_APPROVED_BY_USER,
        promotion_allowed=True,
    )

    validate_hermes_skill_contract(skill)


def test_validate_hermes_skill_contract_rejects_direct_promoted_status() -> None:
    skill = HermesSkillContract(
        skill_id="skill-1",
        name="Skill",
        version="0.1.0",
        module_id="module-1",
        description="Promoted skill",
        status=HERMES_STATUS_PROMOTED,
    )

    with pytest.raises(ContractError):
        validate_hermes_skill_contract(skill)
