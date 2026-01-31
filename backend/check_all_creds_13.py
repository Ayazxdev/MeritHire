
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Credential

async def d():
    async with async_session_maker() as db:
        q = await db.execute(select(Credential).where(Credential.candidate_id == 13).order_by(Credential.issued_at.desc()))
        creds = q.scalars().all()
        print(f"Candidate 13 has {len(creds)} credentials.")
        for c in creds:
            st = c.credential_json
            print(f"App {c.application_id} | Stage: {st.get('current_stage')} | Completed: {st.get('stages_completed')}")

if __name__ == "__main__":
    asyncio.run(d())
