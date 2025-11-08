"""
Job Manager - Manage background jobs with SSE streaming

Handles:
- Job creation and tracking
- Stage-based progress updates
- SSE event emission
- Job completion and cleanup
"""

import uuid
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class JobStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    DEGRADED = "degraded"  # Completed but with warnings


class StageStatus:
    IDLE = "idle"
    RUNNING = "running"
    DONE = "done"
    WARN = "warn"
    FAIL = "fail"


class JobManager:
    """
    Manage background recommendation jobs with SSE streaming

    In-memory storage with TTL cleanup (suitable for MVP)
    In production, use Redis or similar
    """

    def __init__(self, ttl_seconds: int = 3600):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.job_queues: Dict[str, asyncio.Queue] = {}
        self.ttl_seconds = ttl_seconds

    def create_job(self, city: str, concept: str, limit: int, include_crime: bool) -> str:
        """Create a new recommendation job"""
        job_id = str(uuid.uuid4())

        self.jobs[job_id] = {
            'job_id': job_id,
            'status': JobStatus.PENDING,
            'city': city,
            'concept': concept,
            'limit': limit,
            'include_crime': include_crime,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(seconds=self.ttl_seconds),
            'stages': {},
            'degraded': [],
            'result': None,
            'error': None
        }

        # Create event queue for SSE
        self.job_queues[job_id] = asyncio.Queue()

        logger.info(f"Created job {job_id} for {concept} in {city}")
        return job_id

    async def emit_stage_update(
        self,
        job_id: str,
        stage: str,
        status: str,
        metrics: Optional[Dict[str, Any]] = None,
        ms: Optional[int] = None,
        cached: bool = False
    ):
        """
        Emit a stage update event for SSE streaming

        Args:
            job_id: Job identifier
            stage: Stage name (e.g., "GEO", "DEMO", "COMP")
            status: Stage status (idle|running|done|warn|fail)
            metrics: Optional metrics data
            ms: Milliseconds taken for this stage
            cached: Whether data was served from cache
        """
        if job_id not in self.jobs:
            logger.warning(f"Attempted to update non-existent job {job_id}")
            return

        # Update job stages
        self.jobs[job_id]['stages'][stage] = {
            'status': status,
            'metrics': metrics or {},
            'ms': ms,
            'cached': cached,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Create SSE event
        event = {
            'job_id': job_id,
            'stage': stage,
            'status': status,
            'metrics': metrics or {},
            'ms': ms,
            'cached': cached
        }

        # Push to queue for SSE stream
        if job_id in self.job_queues:
            await self.job_queues[job_id].put(event)

        logger.debug(f"Job {job_id}: {stage} → {status} ({ms}ms)")

    async def complete_job(
        self,
        job_id: str,
        result: Dict[str, Any],
        degraded: Optional[List[str]] = None
    ):
        """Mark job as complete with final result"""
        if job_id not in self.jobs:
            return

        self.jobs[job_id]['status'] = (
            JobStatus.DEGRADED if degraded else JobStatus.COMPLETE
        )
        self.jobs[job_id]['result'] = result
        self.jobs[job_id]['degraded'] = degraded or []
        self.jobs[job_id]['completed_at'] = datetime.utcnow()

        # Send completion event
        completion_event = {
            'job_id': job_id,
            'stage': 'COMPLETE',
            'status': 'done',
            'result': result
        }

        if job_id in self.job_queues:
            await self.job_queues[job_id].put(completion_event)
            # Signal end of stream
            await self.job_queues[job_id].put(None)

        logger.info(f"Job {job_id} completed")

    async def fail_job(self, job_id: str, error: str):
        """Mark job as failed"""
        if job_id not in self.jobs:
            return

        self.jobs[job_id]['status'] = JobStatus.FAILED
        self.jobs[job_id]['error'] = error
        self.jobs[job_id]['completed_at'] = datetime.utcnow()

        # Send failure event
        failure_event = {
            'job_id': job_id,
            'stage': 'ERROR',
            'status': 'fail',
            'error': error
        }

        if job_id in self.job_queues:
            await self.job_queues[job_id].put(failure_event)
            await self.job_queues[job_id].put(None)

        logger.error(f"Job {job_id} failed: {error}")

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and result"""
        return self.jobs.get(job_id)

    async def stream_job_events(self, job_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream SSE events for a job

        Yields events until job completes or fails
        """
        if job_id not in self.job_queues:
            logger.warning(f"No event queue for job {job_id}")
            return

        queue = self.job_queues[job_id]

        while True:
            try:
                # Wait for next event (with timeout)
                event = await asyncio.wait_for(queue.get(), timeout=60.0)

                if event is None:
                    # End of stream signal
                    break

                yield event

            except asyncio.TimeoutError:
                # Send keepalive
                yield {'type': 'keepalive'}
                continue
            except Exception as e:
                logger.error(f"Error streaming job {job_id}: {e}")
                break

    async def cleanup_expired_jobs(self):
        """Clean up expired jobs (run periodically)"""
        now = datetime.utcnow()
        expired_jobs = [
            job_id for job_id, job in self.jobs.items()
            if job['expires_at'] < now
        ]

        for job_id in expired_jobs:
            logger.info(f"Cleaning up expired job {job_id}")
            del self.jobs[job_id]
            if job_id in self.job_queues:
                del self.job_queues[job_id]

        if expired_jobs:
            logger.info(f"Cleaned up {len(expired_jobs)} expired jobs")


# Global job manager instance
job_manager = JobManager()
