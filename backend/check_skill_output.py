
import asyncio
import json
from sqlalchemy import select
from app.db import async_session_maker
from app.models import AgentRun

async def d():
    async with async_session_maker() as db:
        q = await db.execute(select(AgentRun).where(AgentRun.application_id == 26, AgentRun.agent_name == 'SKILL'))
        r = q.scalar_one_or_none()
        if r:
            print(f"SKILL Output: {json.dumps(r.output_payload, indent=2)}")

if __name__ == "__main__":
    asyncio.run(d())
