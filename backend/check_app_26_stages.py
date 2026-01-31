
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Credential

async def d():
    async with async_session_maker() as db:
        q = await db.execute(select(Credential).where(Credential.application_id == 26))
        c = q.scalar_one_or_none()
        if c:
            st = c.credential_json
            print(f"App 26 | Stage: {st.get('current_stage')} | Completed: {st.get('stages_completed')}")
            print(f"Status in JSON: {st.get('status')}")
            print(f"Test Required: {st.get('test_required')}")
        else:
            print("No credential for App 26.")

if __name__ == "__main__":
    asyncio.run(d())
