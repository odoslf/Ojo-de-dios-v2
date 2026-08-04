"""Scraping worker contract without network scraping."""

from app.workers.base_worker import BaseWorker


class ScrapingWorker(BaseWorker):
    """Worker for controlled scraping-targeted in-process technique handling."""

    worker_name = "scraping"
