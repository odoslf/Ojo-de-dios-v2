"""Cloud worker contract without cloud connections or mutations."""

from app.workers.base_worker import BaseWorker


class CloudWorker(BaseWorker):
    """Worker for controlled cloud-targeted in-process technique handling."""

    worker_name = "cloud"
