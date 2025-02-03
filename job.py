import asyncio

import httpx
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from job_pool import JobPool

class Job:
    def __init__(self, parent_pool: "JobPool", base_url: str, sub_dir: str):
        self.parent_pool = parent_pool
        self.base_url = base_url
        self.sub_dir = sub_dir

    async def run(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/{self.sub_dir}")
            if response.status_code in [200, 403]:
                print(f"Directory {self.base_url}/{self.sub_dir} : {response.status_code}")


    def __repr__(self):
        return f"{self.base_url}/{self.sub_dir}"