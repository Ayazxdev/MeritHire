
import asyncio
from sqlalchemy import select, func
from app.db import async_session_maker
from app.models import Credential

async def d():
    async with async_session_maker() as db:
        q = await db.execute(select(func.count(Credential.id)).where(Credential.application_id == 26))
        count = q.scalar()
        print(f"Number of Credentials for app 26: {count}")
        
        q2 = await db.execute(select(Credential).where(Credential.application_id == 26))
        creds = q2.scalars().all()
        for c in creds:
            print(f" - ID: {c.id}, Issued At: {c.issued_at}")

if __name__ == "__main__":
    asyncio.run(d())
