import asyncio
from app.db import engine, Base
from app.models import Candidate, Company, Job, Application, AgentRun, Credential, AuditLog, ReviewCase, Blacklist

async def verify_db():
    print("Attempting to create tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    asyncio.run(verify_db())
