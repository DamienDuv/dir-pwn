import asyncio
import time

from session import Session


async def main():
    start_time = time.time()

    session = Session("http://localhost", "", "")
    await session.start_pwn()

    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.6f} seconds")

if __name__ == "__main__":
    asyncio.run(main())