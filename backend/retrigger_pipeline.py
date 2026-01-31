
import asyncio
from sqlalchemy import select
from app.models import Application
from app.services.pipeline_orchestrator import PipelineOrchestrator
from app.db import async_session_maker

async def retrigger(app_id):
    async with async_session_maker() as db:
        print(f"Retriggering pipeline for app {app_id}...")
        
        # Fetch app data
        q = await db.execute(select(Application).where(Application.id == app_id))
        app = q.scalar_one_or_none()
        if not app:
            print("App not found")
            return
            
        orchestrator = PipelineOrchestrator(db)
        # Call with all required arguments
        result = await orchestrator.execute_pipeline(
            application_id=app_id,
            resume_text=app.resume_text,
            resume_path=app.resume_file_path,
            github_url=app.github_url,
            leetcode_url=app.leetcode_url,
            codeforces_url=app.codeforces_url,
            linkedin_pdf_path=None, 
            linkedin_text=""
        )
        print(f"Pipeline finished. Status: {result.get('status')}")
        print(f"Stages Completed: {result.get('stages_completed')}")

if __name__ == "__main__":
    import sys
    app_id = int(sys.argv[1]) if len(sys.argv) > 1 else 26
    asyncio.run(retrigger(app_id))
