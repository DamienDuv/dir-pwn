from typing import Optional

from job import Job
from job_pool import JobPool
from worker_pool import WorkerPool


class Session:
    def __init__(self, base_url: str, dictionary_path: str , output_db_path: Optional[str] = None):
        self.base_url = base_url
        self.dictionary_path = dictionary_path
        self.output_db_path = output_db_path
        self.job_pool = JobPool()
        self.worker_pool = WorkerPool(self.job_pool)


    async def start_pwn(self):
        await self.worker_pool.add_workers(5)

        with open("dictionaries/directory-list-2.3-small.txt") as dictionary:
            lines = dictionary.readlines()[:1000]
            lines = [line.strip() for line in lines]

            for sub_dir in lines:
                await self.job_pool.push(Job(self.job_pool, self.base_url, sub_dir))

        await self.job_pool.wait_for_completion()
        await self.worker_pool.stop_all_workers()



