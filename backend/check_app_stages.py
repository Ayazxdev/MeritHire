
import asyncio
import sys
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Credential

async def d(app_id):
    async with async_session_maker() as db:
        q = await db.execute(select(Credential).where(Credential.application_id == app_id))
        c = q.scalar_one_or_none()
        if c:
            st = c.credential_json
            print(f"App {app_id} | Stage: {st.get('current_stage')} | Completed: {st.get('stages_completed')}")
            print(f"Status in JSON: {st.get('status')}")
            print(f"Test Required: {st.get('test_required')}")
        else:
            print(f"No credential for App {app_id}.")

if __name__ == "__main__":
    app_id = int(sys.argv[1]) if len(sys.argv) > 1 else 26
    asyncio.run(d(app_id))
