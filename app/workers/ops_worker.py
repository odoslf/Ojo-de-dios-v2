"""Operations worker contract."""

from app.workers.base_worker import BaseWorker


class OpsWorker(BaseWorker):
    """Worker for controlled operations in-process technique handling."""

    worker_name = "ops"
