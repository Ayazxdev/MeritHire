
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Application, Credential

async def d():
    async with async_session_maker() as db:
        # Check all apps for candidate 13
        q = await db.execute(select(Application).where(Application.candidate_id == 13).order_by(Application.created_at.desc()))
        apps = q.scalars().all()
        print(f"Candidate 13 has {len(apps)} applications.")
        for a in apps:
            print(f"App {a.id}: status={a.status}, created={a.created_at}")
            # Check if it has a credential
            qc = await db.execute(select(Credential).where(Credential.application_id == a.id).order_by(Credential.issued_at.desc()))
            cred = qc.scalar_one_or_none()
            if cred:
                print(f"  Credential ID {cred.id}: stage={cred.credential_json.get('current_stage')}, completed={cred.credential_json.get('stages_completed')}")
            else:
                print("  No credential found.")

if __name__ == "__main__":
    asyncio.run(d())
