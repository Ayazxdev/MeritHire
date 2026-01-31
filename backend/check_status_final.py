
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Application

async def d():
    async with async_session_maker() as db:
        q = await db.execute(select(Application).where(Application.id == 26))
        a = q.scalar_one()
        print(f'Status: {a.status}, Test Required: {a.test_required}')

if __name__ == "__main__":
    asyncio.run(d())
