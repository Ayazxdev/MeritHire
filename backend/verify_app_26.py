
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Application

async def d():
    async with async_session_maker() as db:
        q = await db.execute(select(Application).where(Application.id == 26))
        a = q.scalar_one_or_none()
        if a:
            print(f"App 26 exists. Candidate ID: {a.candidate_id}")
        else:
            print("App 26 NOT found.")

if __name__ == "__main__":
    asyncio.run(d())
