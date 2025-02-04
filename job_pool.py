import asyncio
import time
from collections import deque
from typing import Optional

import job

class JobPool:
    def __init__(self):
        self.pool = asyncio.Queue()
        self.active_jobs = 0
        self.lock = asyncio.Lock()
        self.all_jobs_done = asyncio.Event()

        # Rolling job completion tracking
        self.job_timestamps = deque(maxlen=50)
        self.job_per_second = 0
        self.time_to_completion = 0

    async def push(self, new_job: Optional[job.Job]):
        """Push a new job."""
        async with self.lock:
            self.active_jobs += 1
        await self.pool.put(new_job)

    async def pop(self) -> job.Job:
        """Retrieve a job from the pool."""
        return await self.pool.get()
    
    def job_done(self):
        """Mark a job as completed and check if all are done."""
        self.pool.task_done()
        self._track_job_speed()
        asyncio.create_task(self._decrement_active_jobs())

    async def _decrement_active_jobs(self):
        """Decrement active task count safely."""
        async with self.lock:
            self.active_jobs -= 1
            if self.active_jobs == 0:
                self.all_jobs_done.set()

    async def wait_for_completion(self):
        """Wait until all jobs are completed."""
        async with self.lock:
            if self.active_jobs == 0:
                self.all_jobs_done.set()
        await self.all_jobs_done.wait()

    def _track_job_speed(self):
        """Track completed jobs per second using a rolling window."""
        now = time.time()
        self.job_timestamps.append(now)

        if len(self.job_timestamps) > 1:
            elapsed_time = self.job_timestamps[-1] - self.job_timestamps[0]
            if elapsed_time > 0:
                self.job_per_second = len(self.job_timestamps) / elapsed_time
                self.time_to_completion = self.active_jobs / self.job_per_second
