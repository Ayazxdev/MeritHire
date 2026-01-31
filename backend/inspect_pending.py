
import asyncio
from sqlalchemy import select
from app.db import async_session_maker
from app.models import Application

async def d():
    async with async_session_maker() as db:
        for app_id in [5, 6]:
            q = await db.execute(select(Application).where(Application.id == app_id))
            app = q.scalar_one_or_none()
            if app:
                print(f"App {app_id}:")
                print(f"  Status: {app.status}")
                print(f"  Resume Path: {app.resume_file_path}")
                print(f"  Resume Text Length: {len(app.resume_text) if app.resume_text else 0}")
                print(f"  GitHub: {app.github_url}")

if __name__ == "__main__":
    asyncio.run(d())
