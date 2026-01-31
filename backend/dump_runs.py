
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import AgentRun

async def dump_all_runs():
    async with async_session_maker() as db:
        q = await db.execute(select(AgentRun).order_by(AgentRun.created_at.desc()).limit(20))
        runs = q.scalars().all()
        for r in runs:
            print(f"App {r.application_id} | Agent {r.agent_name} | Status {r.status} | Created {r.created_at}")

if __name__ == "__main__":
    asyncio.run(dump_all_runs())
