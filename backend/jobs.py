"""Async job queue management for long-running tasks."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from rich.console import Console

console = Console()


class JobStatus(str, Enum):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    """Represents an async job."""

    job_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: Any = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
        }


class JobQueue:
    """Simple in-memory job queue for async tasks."""

    def __init__(self):
        self.jobs: dict[str, Job] = {}

    def create_job(self) -> Job:
        """Create and register a new job."""
        job = Job()
        self.jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str) -> Job | None:
        """Get job by ID."""
        return self.jobs.get(job_id)

    def update_job(self, job_id: str, **kwargs) -> Job | None:
        """Update job status/result."""
        job = self.jobs.get(job_id)
        if job:
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
        return job

    async def submit_task(
        self,
        coro: Callable[..., Any],
        *args,
        **kwargs,
    ) -> Job:
        """Submit an async task and return job."""
        job = self.create_job()
        asyncio.create_task(self._run_task(job, coro, *args, **kwargs))
        return job

    async def _run_task(self, job: Job, coro: Callable[..., Any], *args, **kwargs) -> None:
        """Execute task and update job status."""
        try:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()

            result = await coro(*args, **kwargs) if asyncio.iscoroutinefunction(coro) else coro(*args, **kwargs)
            job.result = result
            job.status = JobStatus.COMPLETED

            console.log(f"[green]✓ Job {job.job_id} completed[/green]")
        except Exception as e:
            job.error = str(e)
            job.status = JobStatus.FAILED
            console.log(f"[red]✗ Job {job.job_id} failed: {e}[/red]")
        finally:
            job.completed_at = datetime.now()


job_queue = JobQueue()
