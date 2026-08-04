"""Android worker contract without invoking device tooling."""

from app.workers.base_worker import BaseWorker


class AndroidWorker(BaseWorker):
    """Worker for controlled Android-targeted in-process technique handling."""

    worker_name = "android"
