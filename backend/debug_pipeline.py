
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import AgentRun, Credential, Application

async def dump_status(app_id):
    async with async_session_maker() as db:
        # App status
        app_q = await db.execute(select(Application).where(Application.id == app_id))
        app = app_q.scalar_one_or_none()
        if app:
            print(f"Application {app_id} Status: {app.status}")
            print(f"Resume Path: {app.resume_file_path}")
            print(f"Resume Text (len): {len(app.resume_text)}")
        
        # Agent Runs
        q = await db.execute(select(AgentRun).where(AgentRun.application_id == app_id))
        runs = q.scalars().all()
        print(f"Agent Runs for {app_id}:")
        for r in runs:
            print(f" - {r.agent_name}: {r.status} (Created: {r.created_at})")
            if r.status == "failed":
                print(f"   Error: {r.output_payload}")
        
        # Credential
        c_q = await db.execute(select(Credential).where(Credential.application_id == app_id))
        cred = c_q.scalar_one_or_none()
        if cred:
            print(f"Credential JSON Stage: {cred.credential_json.get('current_stage')}")
            print(f"Stages Completed: {cred.credential_json.get('stages_completed')}")

if __name__ == "__main__":
    import sys
    app_id = int(sys.argv[1]) if len(sys.argv) > 1 else 26
    asyncio.run(dump_status(app_id))
