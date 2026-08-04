"""Docker worker contract without invoking Docker."""

from app.workers.base_worker import BaseWorker


class DockerWorker(BaseWorker):
    """Worker for controlled Docker-targeted in-process technique handling."""

    worker_name = "docker"
