import asyncio

import task


class TaskPool:
    def __init__(self):
        self.pool = asyncio.Queue()
        self.active_tasks = 0
        self.lock = asyncio.Lock()
        self.all_tasks_done = asyncio.Event()

    async def push(self, task: Task):
        """Push a new task."""
        async with self.lock:
            self.active_tasks += 1
        await self.pool.put(task)

    async def pop(self) -> Task:
        """Retrieve a task from the pool."""
        return await self.pool.get()
    
    def task_done(self):
        """Mark a task as completed and check if all are done."""
        self.pool.task_done()
        asyncio.create_task(self._decrement_active_tasks())

    async def _decrement_active_tasks(self):
        """Decrement active task count safely."""
        async with self.lock:
            self.active_tasks -= 1
            if self.active_tasks == 0:
                self.all_tasks_done.set()

    async def wait_for_completion(self):
        """Wait until all tasks are completed."""
        async with self.lock:
            if self.active_tasks == 0:
                self.all_tasks_done.set()
        await self.all_tasks_done.wait()
