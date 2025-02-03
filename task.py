import asyncio
import random

from task_pool import TaskPool


class Task:
    def __init__(self, base_url: str, sub_dir: str):
        self.base_url = base_url
        self.sub_dir = sub_dir

    async def run(self, task_pool: TaskPool):
        await asyncio.sleep(1)
        rnd = random.randint(0,100)
        if rnd <= 20:
            for i in range(0,3):
                await task_pool.push(Task(self.base_url, f"{self.sub_dir}/{rnd + i}"))

    def __repr__(self):
        return f"{self.base_url}/{self.sub_dir}"