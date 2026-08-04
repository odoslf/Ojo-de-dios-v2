"""Hardware worker contract without touching hardware."""

from app.workers.base_worker import BaseWorker


class HardwareWorker(BaseWorker):
    """Worker for controlled hardware-targeted in-process technique handling."""

    worker_name = "hardware"
