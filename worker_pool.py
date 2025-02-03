import asyncio

from job_pool import JobPool
from worker import Worker


class WorkerPool:
    """
    Manages a pool of Worker instances that process jobs from a shared JobPool.
    Provides methods to dynamically add, remove, and stop workers.
    """

    def __init__(self, job_pool: JobPool):
        """
        Initializes the WorkerPool.

        Args:
            job_pool (JobPool): The shared job queue from which workers retrieve tasks.
        """
        self.job_pool = job_pool  # Shared queue for workers to pull jobs from
        self.workers: list[Worker] = []  # List of active worker instances
        self._worker_id_counter = 0  # Ensures each worker has a unique ID

    async def add_workers(self, count=1):
        """
        Dynamically adds workers to the pool and starts them.

        Args:
            count (int): Number of workers to add.
        """
        new_workers = []
        for _ in range(count):
            worker = Worker(self._worker_id_counter, self.job_pool)  # Create a new worker with a unique ID
            self._worker_id_counter += 1  # Increment worker ID counter
            new_workers.append(worker)

        self.workers.extend(new_workers)  # Add new workers to the active worker list
        await asyncio.gather(*(worker.start() for worker in new_workers))  # Start all new workers concurrently


    async def remove_worker(self, worker_id):
        """
        Removes a worker from the pool by stopping it and removing it from the list.

        Args:
            worker_id (int): The ID of the worker to remove.
        """
        worker = next((w for w in self.workers if w.id == worker_id), None)  # Find the worker by ID
        if worker:
            await worker.stop()  # Stop the worker gracefully
            self.workers.remove(worker)  # Remove it from the active worker list

    async def stop_all_workers(self):
        """
        Gracefully stops all workers by sending stop signals and waiting for them to exit.
        """
        for _ in self.workers:
            await self.job_pool.push(None)  # Send stop signals to workers (they exit when they receive None)

        await asyncio.gather(*(worker.stop() for worker in self.workers))  # Wait for all workers to stop
