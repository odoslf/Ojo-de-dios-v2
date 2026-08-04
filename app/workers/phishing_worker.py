"""Phishing worker contract without campaign or email execution."""

from app.workers.base_worker import BaseWorker


class PhishingWorker(BaseWorker):
    """Worker for controlled phishing-targeted in-process technique handling."""

    worker_name = "phishing"
