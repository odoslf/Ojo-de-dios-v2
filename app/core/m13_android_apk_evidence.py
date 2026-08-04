"""M13 Android APK evidence intake and structural archive inspection."""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO

from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M13_MODULE_ID = "m13_android"
MAX_APK_BYTES = 512 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 20_000
MAX_UNCOMPRESSED_ARCHIVE_BYTES = 1024 * 1024 * 1024
MAX_LISTED_ARCHIVE_ENTRIES = 100
_CHUNK_SIZE = 1024 * 1024


def _safe_filename(filename: str) -> str:
    base = Path(filename or "application.apk").name
    safe = "".join(char if char.isalnum() or char in ".-_" else "_" for char in base)
    return safe[:180] or "application.apk"


def inspect_m13_apk_archive(apk_path: Path) -> dict[str, object]:
    """Read APK ZIP metadata without executing code or loading Android bytecode."""
    try:
        with zipfile.ZipFile(apk_path) as archive:
            entries = archive.infolist()
    except (OSError, zipfile.BadZipFile):
        return {
            "format": "unknown",
            "zip_recognized": False,
            "member_count": 0,
            "uncompressed_size_bytes": 0,
            "archive_limits_exceeded": False,
            "has_android_manifest": False,
            "dex_entry_count": 0,
            "has_resources_arsc": False,
            "has_meta_inf": False,
            "listed_entries": [],
        }

    names = [entry.filename for entry in entries]
    uncompressed_size = sum(max(0, entry.file_size) for entry in entries)
    dex_entry_count = sum(
        1
        for name in names
        if name.rsplit("/", 1)[-1].startswith("classes") and name.rsplit("/", 1)[-1].endswith(".dex")
    )
    return {
        "format": "apk_zip" if "AndroidManifest.xml" in names else "zip",
        "zip_recognized": True,
        "member_count": len(entries),
        "uncompressed_size_bytes": uncompressed_size,
        "archive_limits_exceeded": len(entries) > MAX_ARCHIVE_ENTRIES or uncompressed_size > MAX_UNCOMPRESSED_ARCHIVE_BYTES,
        "has_android_manifest": "AndroidManifest.xml" in names,
        "dex_entry_count": dex_entry_count,
        "has_resources_arsc": "resources.arsc" in names,
        "has_meta_inf": any(name.startswith("META-INF/") for name in names),
        "listed_entries": names[:MAX_LISTED_ARCHIVE_ENTRIES],
    }


def write_m13_apk_evidence(
    target: TargetRecord,
    stream: BinaryIO,
    filename: str,
    content_type: str | None = None,
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Store an APK sample, hash it, and persist a structural inspection receipt."""
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M13_MODULE_ID, repo_root=root)
    evidence_dir = binding.root_path / "evidence" / "apk"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _safe_filename(filename)
    temporary_path = evidence_dir / f".{safe_name}.{os.getpid()}.incoming"
    digest = hashlib.sha256()
    total = 0
    try:
        with temporary_path.open("xb") as destination:
            while True:
                chunk = stream.read(_CHUNK_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_APK_BYTES:
                    raise ValueError("APK exceeds the 512 MiB intake limit.")
                digest.update(chunk)
                destination.write(chunk)
        if total == 0:
            raise ValueError("APK file is empty.")
        sha256 = digest.hexdigest()
        apk_path = evidence_dir / f"{sha256[:16]}_{safe_name}"
        if apk_path.exists():
            temporary_path.unlink(missing_ok=True)
        else:
            temporary_path.replace(apk_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    inspection = inspect_m13_apk_archive(apk_path)
    receipt = {
        "schema_version": 1,
        "target_id": target.target_id,
        "module_id": M13_MODULE_ID,
        "apk_file": apk_path.as_posix(),
        "filename": safe_name,
        "content_type": content_type or "application/vnd.android.package-archive",
        "size_bytes": total,
        "sha256": sha256,
        "inspection": inspection,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "dynamic_analysis_performed": False,
        "device_interaction_performed": False,
    }
    receipt_path = evidence_dir / f"{sha256[:16]}.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt["receipt_path"] = receipt_path.as_posix()
    return receipt


def list_m13_apk_evidence(
    target: TargetRecord, repo_root: Path | None = None, limit: int = 100
) -> tuple[dict[str, object], ...]:
    """List persisted M13 APK receipts without reopening archived entries."""
    if limit < 1:
        raise ValueError("limit must be at least 1.")
    root = Path.cwd() if repo_root is None else repo_root
    evidence_dir = bind_target_module_workspace(target, M13_MODULE_ID, repo_root=root).root_path / "evidence" / "apk"
    if not evidence_dir.is_dir():
        return ()
    receipts: list[dict[str, object]] = []
    for path in sorted(evidence_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(receipt, dict) and receipt.get("target_id") == target.target_id and receipt.get("module_id") == M13_MODULE_ID:
            receipt["receipt_path"] = path.as_posix()
            receipts.append(receipt)
        if len(receipts) >= limit:
            break
    return tuple(receipts)
