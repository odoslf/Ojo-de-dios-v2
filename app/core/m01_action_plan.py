"""Executable operator work plans derived from persisted M01 evidence and LaIA reviews."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.ai.m01_context import list_m01_target_ai_reviews
from app.core.target_model import TargetRecord
from app.core.target_osint import M01_MODULE_ID, list_target_passive_dns_history
from app.core.target_workspace import bind_target_module_workspace


@dataclass(frozen=True, slots=True)
class M01ActionStep:
    """One traceable operator action; it never executes activity against a target."""

    step_id: str
    title: str
    priority: str
    action_type: str
    instruction: str
    evidence_refs: tuple[str, ...]
    source: str

    def to_dict(self) -> dict[str, object]:
        return {
            "step_id": self.step_id,
            "title": self.title,
            "priority": self.priority,
            "action_type": self.action_type,
            "instruction": self.instruction,
            "evidence_refs": list(self.evidence_refs),
            "source": self.source,
            "execution": "operator_confirmation_required",
            "target_activity_performed": False,
        }


@dataclass(frozen=True, slots=True)
class M01ActionPlan:
    """Target-specific plan built exclusively from local persisted evidence."""

    target_id: str
    generated_at: str
    steps: tuple[M01ActionStep, ...]
    source_history_count: int
    source_review_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "plan_type": "m01_evidence_action_plan",
            "target_id": self.target_id,
            "generated_at": self.generated_at,
            "steps": [step.to_dict() for step in self.steps],
            "step_count": len(self.steps),
            "source_history_count": self.source_history_count,
            "source_review_count": self.source_review_count,
            "uses_persisted_workspace_only": True,
            "target_activity_performed": False,
            "external_ai_call_performed": False,
        }


def _step_id(target_id: str, action_type: str, instruction: str) -> str:
    digest = hashlib.sha256(f"{target_id}:{action_type}:{instruction}".encode("utf-8")).hexdigest()[:12]
    return f"m01-plan-{digest}"


def _step(
    target: TargetRecord,
    title: str,
    priority: str,
    action_type: str,
    instruction: str,
    evidence_refs: tuple[str, ...],
    source: str,
) -> M01ActionStep:
    return M01ActionStep(
        step_id=_step_id(target.target_id, action_type, instruction),
        title=title,
        priority=priority,
        action_type=action_type,
        instruction=instruction,
        evidence_refs=evidence_refs,
        source=source,
    )


def _read_findings(path: Path) -> list[dict[str, object]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [item for item in payload if isinstance(item, dict)] if isinstance(payload, list) else []


def _finding_step(target: TargetRecord, finding: dict[str, object], finding_path: Path) -> M01ActionStep | None:
    title = str(finding.get("title", "")).strip()
    recommendation = str(finding.get("recommendation", "")).strip()
    finding_id = str(finding.get("finding_id", "")).strip()
    reference = f"{finding_path.as_posix()}#{finding_id}" if finding_id else finding_path.as_posix()
    mapped = {
        "Correo publicado sin SPF detectado": ("medium", "review_dns_mail_auth", "Revisar SPF publicado y su alineación con el envío de correo autorizado."),
        "Correo publicado sin DMARC detectado": ("medium", "review_dns_mail_auth", "Revisar DMARC, SPF y DKIM antes de aplicar una política de rechazo."),
        "Nameservers no detectados en la consulta": ("low", "verify_dns_delegation", "Verificar delegación y autoridades DNS dentro del alcance autorizado."),
        "Dominio sin resolución DNS útil": ("medium", "verify_target_scope", "Confirmar el identificador, el alcance y el estado del dominio antes de cualquier técnica posterior."),
        "Superficie observable amplia en Certificate Transparency": ("low", "inventory_passive_certificate_names", "Clasificar nombres de Certificate Transparency como actuales, históricos o fuera de alcance."),
    }
    if title == "Baseline pasivo registrado sin hallazgos priorizados":
        return _step(
            target, "Conservar baseline M01", "info", "preserve_passive_baseline",
            "Conservar este snapshot como referencia y repetir DNS pasivo cuando cambie el alcance o exista una hipótesis concreta.",
            (reference,), "m01_finding",
        )
    if title not in mapped:
        return None
    priority, action_type, instruction = mapped[title]
    if recommendation:
        instruction = f"{instruction} Recomendación registrada: {recommendation}"
    return _step(target, title, priority, action_type, instruction, (reference,), "m01_finding")


def build_m01_action_plan(target: TargetRecord, repo_root: Path | None = None) -> M01ActionPlan:
    """Build a deduplicated operator plan from stored M01 findings and parsed local reviews."""
    root = Path.cwd() if repo_root is None else repo_root
    history = list_target_passive_dns_history(target, repo_root=root, limit=50)
    reviews = list_m01_target_ai_reviews(target, repo_root=root, limit=50)
    steps: list[M01ActionStep] = []
    seen: set[str] = set()

    for entry in history:
        if entry.findings_path is None:
            continue
        for finding in _read_findings(entry.findings_path):
            step = _finding_step(target, finding, entry.findings_path)
            if step is not None and step.step_id not in seen:
                steps.append(step)
                seen.add(step.step_id)

    for review in reviews:
        if review.parsed_content is None:
            continue
        for recommendation in review.parsed_content["recommended_next_steps"]:
            instruction = str(recommendation).strip()
            if not instruction:
                continue
            step = _step(
                target,
                "Recomendación de LaIA/Mistral local",
                "review",
                "review_local_ai_recommendation",
                instruction,
                (review.path.as_posix(),),
                "laia_mistral_review",
            )
            if step.step_id not in seen:
                steps.append(step)
                seen.add(step.step_id)

    if not history:
        steps.append(
            _step(
                target,
                "Recoger evidencia DNS pasiva M01",
                "medium",
                "run_passive_dns",
                "Ejecutar DNS pasivo M01 para crear la primera evidencia del objetivo antes de elaborar conclusiones.",
                (),
                "m01_plan_guardrail",
            )
        )

    priority_order = {"medium": 0, "review": 1, "low": 2, "info": 3}
    steps.sort(key=lambda item: (priority_order.get(item.priority, 4), item.title, item.step_id))
    return M01ActionPlan(
        target_id=target.target_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        steps=tuple(steps),
        source_history_count=len(history),
        source_review_count=len(reviews),
    )


def write_m01_action_plan(target: TargetRecord, repo_root: Path | None = None) -> Path:
    """Build and persist the current M01 operator plan in the target workspace."""
    root = Path.cwd() if repo_root is None else repo_root
    plan = build_m01_action_plan(target, repo_root=root)
    binding = bind_target_module_workspace(target, M01_MODULE_ID, repo_root=root)
    path = binding.root_path / "action_plans" / "current.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
