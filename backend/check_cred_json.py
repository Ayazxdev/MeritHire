
import asyncio
import json
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Credential

async def d():
    async with async_session_maker() as db:
        q = await db.execute(select(Credential).where(Credential.application_id == 26))
        c = q.scalar_one_or_none()
        if c:
            print(f"Credential JSON: {json.dumps(c.credential_json, indent=2)}")

if __name__ == "__main__":
    asyncio.run(d())
