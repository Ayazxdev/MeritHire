
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
            print(f"Credential for App {app_id}:")
            # print(f"JSON: {json.dumps(cred.credential_json, indent=2)}")
            data = cred.credential_json
            print(f"Status: {data.get('status')}")
            print(f"Stages: {data.get('stages_completed')}")
            print(f"Test Required: {data.get('test_required')}")
            print(f"Skill Confidence: {data.get('evidence', {}).get('skill_confidence', 'N/A')}")
            print(f"Skills: {list(data.get('evidence', {}).get('skills', {}).keys())}")
        else:
            print(f"No credential found for App {app_id}")

if __name__ == "__main__":
    app_id = int(sys.argv[1]) if len(sys.argv) > 1 else 27
    asyncio.run(d(app_id))
