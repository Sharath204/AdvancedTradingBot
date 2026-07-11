"""
Scheduler for periodic market analysis.
"""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import Callable, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnalysisScheduler:
    """
    Scheduler for periodic market analysis.
    """

    def __init__(self):
        """
        Initialize scheduler.
        """
        self.scheduler = AsyncIOScheduler()
        self.jobs = {}

    def add_interval_job(
        self,
        func: Callable,
        seconds: int = 300,
        job_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Add periodic job.

        Args:
            func: Function to execute
            seconds: Interval in seconds
            job_id: Job ID
            **kwargs: Additional arguments for function

        Returns:
            Job ID
        """
        if job_id is None:
            job_id = f"job_{datetime.now().timestamp()}"

        job = self.scheduler.add_job(
            func,
            IntervalTrigger(seconds=seconds),
            id=job_id,
            replace_existing=True,
            kwargs=kwargs,
        )
        self.jobs[job_id] = job
        logger.info(f"Added job: {job_id} with interval {seconds}s")
        return job_id

    def remove_job(self, job_id: str) -> bool:
        """
        Remove job.

        Args:
            job_id: Job ID to remove

        Returns:
            True if removed, False otherwise
        """
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
            logger.info(f"Removed job: {job_id}")
            return True
        return False

    async def start(self) -> None:
        """
        Start scheduler.
        """
        self.scheduler.start()
        logger.info("Scheduler started")

    async def shutdown(self) -> None:
        """
        Shutdown scheduler.
        """
        self.scheduler.shutdown()
        logger.info("Scheduler shutdown")

    def get_jobs(self) -> dict:
        """
        Get all jobs.

        Returns:
            Dictionary of jobs
        """
        return self.jobs.copy()
