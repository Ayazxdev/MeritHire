
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import AgentRun

async def d():
    async with async_session_maker() as db:
        q = await db.execute(select(AgentRun).where(AgentRun.application_id == 26, AgentRun.agent_name == 'SKILL').order_by(AgentRun.created_at.desc()))
        r = q.scalars().first()
        if r:
            print(f"SKILL Explanation: {r.output_payload.get('explanation')}")
            print(f"SKILL Output: {r.output_payload.get('output')}")

if __name__ == "__main__":
    asyncio.run(d())
