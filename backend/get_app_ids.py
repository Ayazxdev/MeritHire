
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Application

async def d():
    async with async_session_maker() as db:
        q = await db.execute(select(Application.id).where(Application.candidate_id == 13).order_by(Application.id.desc()))
        print(f"App IDs: {q.scalars().all()}")

if __name__ == "__main__":
    asyncio.run(d())
