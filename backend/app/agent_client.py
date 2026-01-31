import httpx
from app.config import settings

async def call_skill_agent(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{settings.SKILL_AGENT_URL}/run", json=payload)
        r.raise_for_status()
        return r.json()

async def call_bias_agent(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{settings.BIAS_AGENT_URL}/run", json=payload)
        r.raise_for_status()
        return r.json()

async def call_match_agent(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{settings.MATCH_AGENT_URL}/run", json=payload)
        r.raise_for_status()
        return r.json()
