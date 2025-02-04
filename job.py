import httpx
from typing import TYPE_CHECKING

from httpx import Response

if TYPE_CHECKING:
    from job_pool import JobPool

NEED_RECHECK = [408, 429, 500, 501, 502, 503, 504, 505]
PROBABLY_EXIST = [200, 204, 301, 302, 307, 308, 401, 403, 405, 406, 407, 411]
PROBABLY_NOTHING = [400, 404, 410, 413, 414, 415, 416, 418]


def _has_file_extension(url):
    return any(url.endswith(ext) for ext in ['.html', '.php', '.png', '.jpg', '.css', '.js', '.json'])

def _is_likely_directory(url, response):
    # If URL ends with '/' or redirects to a '/' version
    if url.endswith('/') or response.status_code in [301, 302, 307, 308]:
        return True
    # If response content-type is text/html and doesn’t look like a file
    if 'text/html' in response.headers.get('Content-Type', '') and not _has_file_extension(url):
        return True
    return False

class Job:
    def __init__(self, parent_pool: "JobPool", base_url: str, sub_dir: str, recursion_depth = 0):
        self.parent_pool = parent_pool
        self.url = f"{base_url}/{sub_dir}"
        self.recursion_depth = recursion_depth

    async def run(self):
        response = await self._request_url()

        if response.status_code in PROBABLY_EXIST:
            if self.recursion_depth > 0 and _is_likely_directory(self.url, response):
                pass # recurse

            # ADD TO RESULTS

    async def _request_url(self) -> Response:
        async with httpx.AsyncClient() as client:
            return await client.get(self.url)

    def __repr__(self):
        return self.url