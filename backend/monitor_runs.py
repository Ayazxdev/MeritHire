
import asyncio
import sys
from sqlalchemy import select
from app.db import async_session_maker
from app.models import AgentRun

async def d(app_id=None):
    async with async_session_maker() as db:
        if app_id:
            q = await db.execute(select(AgentRun).where(AgentRun.application_id == app_id).order_by(AgentRun.created_at.desc()))
        else:
            q = await db.execute(select(AgentRun).order_by(AgentRun.created_at.desc()).limit(15))
            
        runs = q.scalars().all()
        print(f"Recent runs:")
        for r in runs:
            print(f" - App {r.application_id} | {r.agent_name}: {r.status} ({r.created_at})")

if __name__ == "__main__":
    app_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    asyncio.run(d(app_id))
