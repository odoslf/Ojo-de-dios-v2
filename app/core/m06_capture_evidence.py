"""M06 packet-capture evidence intake and format inspection without network activity."""

from __future__ import annotations

import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO

from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M06_MODULE_ID = "m06_mitm_network"
MAX_CAPTURE_BYTES = 512 * 1024 * 1024
_CHUNK_SIZE = 1024 * 1024


def _safe_filename(filename: str) -> str:
    base = Path(filename or "capture.bin").name
    safe = "".join(char if char.isalnum() or char in ".-_" else "_" for char in base)
    return safe[:180] or "capture.bin"


def inspect_capture_header(header: bytes) -> dict[str, object]:
    """Identify PCAP/PCAPNG metadata from the global header only."""
    magic = header[:4]
    if magic == b"\x0a\x0d\x0d\x0a":
        return {"format": "pcapng", "format_recognized": True, "byte_order": "section_header_dependent", "linktype": None}
    layouts = {
        b"\xd4\xc3\xb2\xa1": ("<", "microsecond"),
        b"\xa1\xb2\xc3\xd4": (">", "microsecond"),
        b"\x4d\x3c\xb2\xa1": ("<", "nanosecond"),
        b"\xa1\xb2\x3c\x4d": (">", "nanosecond"),
    }
    if magic not in layouts or len(header) < 24:
        return {"format": "unknown", "format_recognized": False, "byte_order": None, "linktype": None}
    byte_order, resolution = layouts[magic]
    major, minor, _zone, _sigfigs, snaplen, linktype = struct.unpack(f"{byte_order}HHIIII", header[4:24])
    return {
        "format": "pcap",
        "format_recognized": True,
        "byte_order": "little" if byte_order == "<" else "big",
        "timestamp_resolution": resolution,
        "version": f"{major}.{minor}",
        "snaplen": snaplen,
        "linktype": linktype,
    }


def write_m06_capture_evidence(
    target: TargetRecord,
    stream: BinaryIO,
    filename: str,
    content_type: str | None = None,
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Stream a supplied capture into M06 evidence and record its immutable file metadata."""
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M06_MODULE_ID, repo_root=root)
    captures_dir = binding.root_path / "evidence" / "captures"
    captures_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _safe_filename(filename)
    capture_path = captures_dir / safe_name
    digest = hashlib.sha256()
    total = 0
    header = bytearray()
    with capture_path.open("wb") as destination:
        while True:
            chunk = stream.read(_CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_CAPTURE_BYTES:
                capture_path.unlink(missing_ok=True)
                raise ValueError("Capture exceeds the 512 MiB intake limit.")
            digest.update(chunk)
            if len(header) < 24:
                header.extend(chunk[: 24 - len(header)])
            destination.write(chunk)
    if total == 0:
        capture_path.unlink(missing_ok=True)
        raise ValueError("Capture file is empty.")
    inspection = inspect_capture_header(bytes(header))
    receipt = {
        "schema_version": 1,
        "target_id": target.target_id,
        "module_id": M06_MODULE_ID,
        "captured_file": capture_path.as_posix(),
        "filename": safe_name,
        "content_type": content_type or "application/octet-stream",
        "size_bytes": total,
        "sha256": digest.hexdigest(),
        "inspection": inspection,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "network_capture_started_by_application": False,
        "target_activity_performed": False,
    }
    receipt_path = captures_dir / f"{digest.hexdigest()[:16]}.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt["receipt_path"] = receipt_path.as_posix()
    return receipt


def list_m06_capture_evidence(target: TargetRecord, repo_root: Path | None = None, limit: int = 100) -> tuple[dict[str, object], ...]:
    """List capture receipts without opening or parsing full packet contents."""
    if limit < 1:
        raise ValueError("limit must be at least 1.")
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M06_MODULE_ID, repo_root=root)
    captures_dir = binding.root_path / "evidence" / "captures"
    if not captures_dir.is_dir():
        return ()
    receipts: list[dict[str, object]] = []
    for path in sorted(captures_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict) and payload.get("target_id") == target.target_id and payload.get("module_id") == M06_MODULE_ID:
            payload["receipt_path"] = path.as_posix()
            receipts.append(payload)
        if len(receipts) >= limit:
            break
    return tuple(receipts)
