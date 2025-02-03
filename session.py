import asyncio
from typing import Optional

from task import Task
from task_pool import TaskPool


class Session:
    def __init__(self, base_url: str, dictionary_path: str , output_db_path: Optional[str] = None):
        self.base_url = base_url
        self.dictionary_path = dictionary_path
        self.output_db_path = output_db_path
        self.task_pool = TaskPool()


    async def start_pwn(self):
        num_workers = 3  # Number of concurrent workers

        # Start worker tasks
        workers = [asyncio.create_task(self.worker(i)) for i in range(num_workers)]

        for i in range(10):
            print(f"Adding new task {i}")
            await self.task_pool.push(Task(self.base_url, f"{i}"))
            await asyncio.sleep(0.5)

        await self.task_pool.wait_for_completion()

        # Stop workers by sending `None` sentinel values
        for _ in range(num_workers):
            await self.task_pool.push(None)

        # Wait for workers to finish
        await asyncio.gather(*workers)


    async def worker(self, worker_id: int):
        while True:
            task = await self.task_pool.pop()
            if task is None:
                break
            print(f"Worker {worker_id} processing task: {task}")
            await task.run(self.task_pool)
            print(f"Worker {worker_id} finished task: {task}")
            self.task_pool.task_done()


