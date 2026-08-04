"""Windows worker contract without external command execution."""

from app.workers.base_worker import BaseWorker


class WindowsWorker(BaseWorker):
    """Worker for controlled Windows-hosted in-process technique handling."""

    worker_name = "windows"
