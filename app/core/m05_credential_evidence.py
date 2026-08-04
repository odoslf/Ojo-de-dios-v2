"""M05 credential evidence intake that never persists supplied secret material."""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M05_MODULE_ID = "m05_credentials"
VALID_CREDENTIAL_TYPES = frozenset({"password", "api_token", "session_token", "private_key", "hash", "ticket", "other"})
MAX_SECRET_MATERIAL_LENGTH = 16_384
MAX_LABEL_LENGTH = 512


@dataclass(frozen=True, slots=True)
class CredentialEvidence:
    """Irreversible fingerprint and metadata for supplied credential material."""

    credential_type: str
    label: str
    fingerprint_sha256: str
    material_length: int
    source: str
    evidence_ref: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "credential_type": self.credential_type,
            "label": self.label,
            "fingerprint_sha256": self.fingerprint_sha256,
            "material_length": self.material_length,
            "source": self.source,
            "evidence_ref": self.evidence_ref,
            "secret_material_persisted": False,
        }


def credential_evidence_from_payload(payload: dict[str, Any]) -> CredentialEvidence:
    """Validate transient secret material and return only an irreversible evidence record."""
    credential_type = str(payload.get("credential_type", "")).strip()
    if credential_type not in VALID_CREDENTIAL_TYPES:
        raise ValueError("credential_type is invalid.")
    label = str(payload.get("label", "")).strip()
    source = str(payload.get("source", "operator_provided",)).strip()
    material = str(payload.get("secret_material", ""))
    evidence_ref_raw = payload.get("evidence_ref")
    evidence_ref = str(evidence_ref_raw).strip() if evidence_ref_raw is not None else None
    if not label or len(label) > MAX_LABEL_LENGTH or "\x00" in label:
        raise ValueError("label is invalid or too long.")
    if not source or len(source) > MAX_LABEL_LENGTH or "\x00" in source:
        raise ValueError("source is invalid or too long.")
    if not material or len(material) > MAX_SECRET_MATERIAL_LENGTH:
        raise ValueError("secret_material must be non-empty and at most 16384 characters.")
    if evidence_ref is not None and (len(evidence_ref) > MAX_LABEL_LENGTH or "\x00" in evidence_ref):
        raise ValueError("evidence_ref is invalid or too long.")
    return CredentialEvidence(
        credential_type=credential_type,
        label=label,
        fingerprint_sha256=hashlib.sha256(material.encode("utf-8")).hexdigest(),
        material_length=len(material),
        source=source,
        evidence_ref=evidence_ref or None,
    )


def write_m05_credential_evidence(target: TargetRecord, evidence: CredentialEvidence, repo_root: Path | None = None) -> Path:
    """Persist a secret-free credential evidence receipt in the target M05 workspace."""
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M05_MODULE_ID, repo_root=root)
    evidence_dir = binding.root_path / "evidence" / "credential_receipts"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    receipt_id = hashlib.sha256(f"{target.target_id}:{evidence.fingerprint_sha256}".encode("utf-8")).hexdigest()[:16]
    path = evidence_dir / f"{receipt_id}.json"
    path.write_text(json.dumps({
        "schema_version": 1,
        "receipt_id": receipt_id,
        "target_id": target.target_id,
        "module_id": M05_MODULE_ID,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence": evidence.to_dict(),
        "secret_material_persisted": False,
        "target_activity_performed": False,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def list_m05_credential_evidence(target: TargetRecord, repo_root: Path | None = None, limit: int = 100) -> tuple[dict[str, object], ...]:
    """List valid secret-free M05 receipts without exposing or reconstructing secrets."""
    if limit < 1:
        raise ValueError("limit must be at least 1.")
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M05_MODULE_ID, repo_root=root)
    evidence_dir = binding.root_path / "evidence" / "credential_receipts"
    if not evidence_dir.is_dir():
        return ()
    receipts: list[dict[str, object]] = []
    for path in sorted(evidence_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict) or payload.get("target_id") != target.target_id:
            continue
        if payload.get("module_id") != M05_MODULE_ID or payload.get("secret_material_persisted") is not False:
            continue
        receipt = dict(payload)
        receipt["path"] = path.as_posix()
        receipts.append(receipt)
        if len(receipts) >= limit:
            break
    return tuple(receipts)


def verify_m05_credential_material(
    target: TargetRecord,
    receipt_id: str,
    secret_material: str,
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Cryptographically verify transient material against an M05 receipt without exposing it.

    This proves whether the supplied material matches the recorded evidence
    fingerprint. It intentionally does not attempt authentication against a
    remote service, which would require a separately approved connector.
    """
    if not receipt_id or len(receipt_id) > 128 or any(char not in "0123456789abcdef" for char in receipt_id):
        raise ValueError("receipt_id is invalid.")
    if not secret_material or len(secret_material) > MAX_SECRET_MATERIAL_LENGTH:
        raise ValueError("secret_material must be non-empty and at most 16384 characters.")
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M05_MODULE_ID, repo_root=root)
    receipt_path = binding.root_path / "evidence" / "credential_receipts" / f"{receipt_id}.json"
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Credential receipt was not found or is invalid.") from exc
    evidence = receipt.get("evidence") if isinstance(receipt, dict) else None
    expected = evidence.get("fingerprint_sha256") if isinstance(evidence, dict) else None
    if receipt.get("target_id") != target.target_id or not isinstance(expected, str):
        raise ValueError("Credential receipt does not belong to this target or is invalid.")
    actual = hashlib.sha256(secret_material.encode("utf-8")).hexdigest()
    verified = hmac.compare_digest(expected, actual)
    verification_id = hashlib.sha256(f"{receipt_id}:{actual}:{datetime.now(timezone.utc).isoformat()}".encode("utf-8")).hexdigest()[:16]
    verification_path = binding.root_path / "evidence" / "credential_verifications" / f"{verification_id}.json"
    verification_path.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "verification_id": verification_id,
        "target_id": target.target_id,
        "module_id": M05_MODULE_ID,
        "receipt_id": receipt_id,
        "verified": verified,
        "verification_scope": "local_fingerprint_match_only",
        "remote_authentication_attempted": False,
        "secret_material_persisted": False,
        "verified_at": datetime.now(timezone.utc).isoformat(),
    }
    verification_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result["path"] = verification_path.as_posix()
    return result
