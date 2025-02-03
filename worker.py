import asyncio

from job_pool import JobPool


class Worker:
    """
    A worker that continuously processes jobs from a JobPool.
    Runs as an asynchronous task and can be gracefully stopped.
    """

    def __init__(self, worker_id: int, job_pool: JobPool):
        """
        Initializes a worker.

        Args:
            worker_id (int): A unique identifier for the worker.
            job_pool (JobPool): The shared job queue from which the worker retrieves tasks.
        """
        self.id = worker_id  # Unique worker ID
        self.job_pool = job_pool  # Reference to the shared job queue
        self.worker_task = None  # Stores the worker's running task

    async def start(self):
        """
        Starts the worker loop as a background task.
        Ensures that only one instance of the worker runs at a time.
        """

        self.worker_task = asyncio.create_task(self._run())  # Start worker loop asynchronously

    async def _run(self):
        """
        Main worker loop that continuously retrieves and executes jobs.
        Exits when a stop signal (`None` job) is received.
        """
        try:
            while True:
                job = await self.job_pool.pop()
                if job is None:  # Stop signal received (graceful exit)
                    break

                try:
                    await job.run()  # Execute the job asynchronously
                    self.job_pool.job_done()  # Notify the pool that the job is complete
                except Exception as e:
                    print(f"Worker {self.id} failed to execute job: {e}")  # Handle job-specific errors
        except asyncio.CancelledError:
            print(f"Worker {self.id} was cancelled.")  # Handles forced cancellation
        finally:
            print(f"Worker {self.id} stopped cleanly.")  # Ensures proper cleanup

    async def stop(self, timeout: float = 5.0):
        """
        Gracefully stops the worker by waiting for it to finish within a timeout.

        Args:
            timeout (float): Maximum time (in seconds) to wait for the worker to stop.
        """
        if self.worker_task:  # Ensure the worker is running before stopping
            try:
                await asyncio.wait_for(self.worker_task, timeout=timeout)  # Wait for the task to finish
            except asyncio.TimeoutError:
                print(f"Worker {self.id} did not stop in time, cancelling...")
                self.worker_task.cancel()  # Forcefully cancel if the timeout is exceeded
