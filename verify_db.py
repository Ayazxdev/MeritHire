import asyncio
from sqlalchemy import text
from app.db import engine

async def query():
    async with engine.connect() as conn:
        print("--- Applications ---")
        res = await conn.execute(text("SELECT id, job_id, candidate_id, status, match_score FROM applications ORDER BY id DESC LIMIT 5"))
        for row in res:
            print(row)
            
        print("\n--- Candidates ---")
        res = await conn.execute(text("SELECT id, anon_id, email FROM candidates ORDER BY id DESC LIMIT 5"))
        for row in res:
            print(row)
            
        try:
            print("\n--- Agent Runs ---")
            res = await conn.execute(text("SELECT id, agent_name, status, created_at FROM agent_runs ORDER BY id DESC LIMIT 10"))
            for row in res:
                print(row)
        except Exception as e:
            print(f"\nAgent runs table check: {e}")

if __name__ == '__main__':
    asyncio.run(query())
