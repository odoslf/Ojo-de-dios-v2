"""Tests for operator-only progress tracking of M01 action plans."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.m01_action_tracking import build_m01_action_board, update_m01_action_progress
from app.core.target_model import TARGET_DOMAIN, TARGET_MODE_DRY_RUN, TargetRecord
from app.main import create_app


def _target() -> TargetRecord:
    return TargetRecord(
        target_id="target-action-tracking",
        name="Action Tracking Target",
        target_type=TARGET_DOMAIN,
        value="example.com",
        normalized_value="example.com",
        mode=TARGET_MODE_DRY_RUN,
        allowed_modules=["m01_osint"],
    )


def test_action_board_tracks_confirmed_operator_progress(tmp_path: Path) -> None:
    target = _target()
    initial = build_m01_action_board(target, repo_root=tmp_path)
    step_id = initial["steps"][0]["step_id"]

    updated = update_m01_action_progress(
        target, step_id=step_id, status="completed", note="Baseline revisado por operador.", repo_root=tmp_path
    )

    assert updated["completed_count"] == 1
    assert updated["steps"][0]["progress"]["status"] == "completed"
    assert updated["steps"][0]["progress"]["events"][0]["note"] == "Baseline revisado por operador."
    assert updated["target_activity_performed"] is False
    progress_path = tmp_path / "storage" / "targets" / target.target_id / "modules" / "m01_osint" / "action_plans" / "progress.json"
    assert progress_path.is_file()


def test_action_board_rejects_unknown_step_and_terminal_transition_without_note(tmp_path: Path) -> None:
    target = _target()
    try:
        update_m01_action_progress(target, "unknown", "in_progress", repo_root=tmp_path)
    except ValueError as exc:
        assert "not present" in str(exc)
    else:
        raise AssertionError("Expected unknown current action to be rejected")

    step_id = build_m01_action_board(target, repo_root=tmp_path)["steps"][0]["step_id"]
    try:
        update_m01_action_progress(target, step_id, "completed", repo_root=tmp_path)
    except ValueError as exc:
        assert "note is required" in str(exc)
    else:
        raise AssertionError("Expected terminal status without note to be rejected")


def test_action_board_api_and_page_progress() -> None:
    with TestClient(create_app()) as client:
        created = client.post(
            "/api/targets/create",
            json={
                "name": "Action Board Localhost",
                "target_type": "domain",
                "value": "localhost",
                "mode": "dry_run",
                "allowed_modules": ["m01_osint"],
            },
        )
        target_id = created.json()["target"]["target_id"]
        board = client.get(f"/api/targets/{target_id}/m01/action-board")
        step_id = board.json()["action_board"]["steps"][0]["step_id"]
        updated = client.post(
            f"/api/targets/{target_id}/m01/action-board/progress",
            json={"step_id": step_id, "status": "in_progress", "note": "Pendiente de revisión."},
        )
        page = client.post(
            f"/targets/{target_id}/m01/action-board/progress",
            data={"step_id": step_id, "status": "completed", "note": "Revisión terminada."},
        )

    assert board.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["action_board"]["steps"][0]["progress"]["status"] == "in_progress"
    assert page.status_code == 200
    assert "Estado del paso M01 guardado" in page.text
