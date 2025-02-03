import asyncio

from session import Session


async def main():
    session = Session("www.test.com", "", "")
    await session.start_pwn()

if __name__ == "__main__":
    asyncio.run(main())