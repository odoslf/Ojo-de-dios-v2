"""Hermes lab worker contract without generating or promoting artifacts."""

from app.workers.base_worker import BaseWorker


class HermesLabWorker(BaseWorker):
    """Worker for controlled lab-only in-process technique handling."""

    worker_name = "hermes_lab"
