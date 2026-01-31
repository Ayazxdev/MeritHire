
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
            # print(json.dumps(evidence, indent=2))
            
            # Check for skill verification output
            skill_output = evidence.get('skill', {})
            if not skill_output:
                 # Check if it's directly in evidence or nested elsewhere
                 pass
            
            print("Keys in evidence:", evidence.keys())
            
            # Try to find the skills list
            if 'output' in evidence:
                print("Skills in 'output':", evidence['output'].get('skills', {}).keys())
            elif 'skill_verification' in evidence:
                print("Skills in 'skill_verification':", evidence['skill_verification'].get('skills', {}).keys())
            
        else:
            print(f"No credential found for App {app_id}")

if __name__ == "__main__":
    app_id = int(sys.argv[1]) if len(sys.argv) > 1 else 27
    asyncio.run(d(app_id))
