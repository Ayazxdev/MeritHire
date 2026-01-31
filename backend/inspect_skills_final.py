
import asyncio
import sys
import json
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Credential

async def d(app_id):
    async with async_session_maker() as db:
        q = await db.execute(select(Credential).where(Credential.application_id == app_id))
        cred = q.scalar_one_or_none()
        if cred:
            evidence = cred.credential_json.get('evidence', {})
            skills_data = evidence.get('skills', {})
            print(f"Skill Verification Data Type: {type(skills_data)}")
            if isinstance(skills_data, dict):
                 print(f"Final Skills: {list(skills_data.get('output', {}).get('skills', {}).keys())}")
                 print(f"Confidence: {skills_data.get('output', {}).get('confidence')}")
                 print(f"Signal Strength: {skills_data.get('output', {}).get('signal_strength')}")
            else:
                 print(f"Skills Data: {skills_data}")

if __name__ == "__main__":
    app_id = int(sys.argv[1]) if len(sys.argv) > 1 else 27
    asyncio.run(d(app_id))
