
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Application, Candidate

async def d():
    async with async_session_maker() as db:
        q = await db.execute(select(Candidate).where(Candidate.anon_id == 'ANON-1FCEA2335592'))
        cand = q.scalar_one_or_none()
        if not cand:
            print("Candidate not found")
            return
            
        q2 = await db.execute(select(Application).where(Application.candidate_id == cand.id))
        apps = q2.scalars().all()
        print(f"Applications for candidate {cand.id}:")
        for a in apps:
            print(f" - ID: {a.id}, Status: {a.status}, Created: {a.created_at}")

if __name__ == "__main__":
    asyncio.run(d())
