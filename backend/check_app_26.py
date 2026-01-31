
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import AgentRun

async def d():
    async with async_session_maker() as db:
        q = await db.execute(select(AgentRun).where(AgentRun.application_id == 26).order_by(AgentRun.created_at.desc()))
        for r in q.scalars().all():
            print(f'{r.agent_name}: {r.status} {r.created_at}')

if __name__ == "__main__":
    asyncio.run(d())
