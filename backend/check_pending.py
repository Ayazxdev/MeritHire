
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Application

async def d():
    async with async_session_maker() as db:
        q = await db.execute(select(Application).where(Application.status == 'pending'))
        apps = q.scalars().all()
        if apps:
            print(f"Pending applications: {[a.id for a in apps]}")
        else:
            print("No pending applications.")

if __name__ == "__main__":
    asyncio.run(d())
