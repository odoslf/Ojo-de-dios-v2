"""WSL worker contract without invoking WSL."""

from app.workers.base_worker import BaseWorker


class WSLWorker(BaseWorker):
    """Worker for controlled WSL-targeted in-process technique handling."""

    worker_name = "wsl"
