import asyncio
from app.db import async_session_maker
from app.models import Job
from sqlalchemy import select

async def check():
    async with async_session_maker() as db:
        q = await db.execute(select(Job))
        jobs = q.scalars().all()
        print(f"Jobs found: {len(jobs)}")
        for j in jobs:
            print(f"ID: {j.id}, Title: {j.title}, Published: {j.published}")

if __name__ == "__main__":
    asyncio.run(check())
