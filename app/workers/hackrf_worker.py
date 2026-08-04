"""HackRF worker contract without radio operations."""

from app.workers.base_worker import BaseWorker


class HackRFWorker(BaseWorker):
    """Worker for controlled HackRF-targeted in-process technique handling."""

    worker_name = "hackrf"
