
import asyncio
from app.db import async_session_maker
from app.models import Candidate, Application, Credential
from sqlalchemy import select

async def dump_candidates():
    print("Dumping candidates...")
    async with async_session_maker() as db:
        q = await db.execute(select(Candidate))
        cands = q.scalars().all()
        for c in cands:
            print(f"ID: {c.id}, Email: {c.email}, AnonID: {c.anon_id}, Name: {c.name}")
            
            # Applications
            q_app = await db.execute(select(Application).where(Application.candidate_id == c.id))
            apps = q_app.scalars().all()
            for a in apps:
                print(f"  Application ID: {a.id}, Status: {a.status}, Match Score: {a.match_score}")
                
            # Credentials
            q_cred = await db.execute(select(Credential).where(Credential.candidate_id == c.id))
            creds = q_cred.scalars().all()
            for cr in creds:
                print(f"  Credential ID: {cr.id}, Cred ID: {cr.credential_json.get('credential_id') if cr.credential_json else 'N/A'}")
                print(f"  JSON Sample: {str(cr.credential_json)[:200]}...")
    print("Done.")

if __name__ == "__main__":
    asyncio.run(dump_candidates())
