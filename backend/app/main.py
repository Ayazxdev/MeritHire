import logging
from fastapi import FastAPI, Depends, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import engine, Base, get_db
from app.schemas import ApplyRequest

from app.routers.health import router as health_router
from app.routers.company import router as company_router
from app.routers.candidate import router as candidate_router, apply as candidate_apply
from app.routers.passport import router as passport_router 
from app.routers.auth import router as auth_router

app = FastAPI(title="Fair Hiring Backend", version="1.0")
log = logging.getLogger("uvicorn.error")

# CORS: allow local frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(company_router)
app.include_router(candidate_router)
app.include_router(passport_router)
app.include_router(auth_router)

@app.on_event("startup")
async def startup():
    # Simple v1: auto-create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/api/apply")
async def api_apply(payload: ApplyRequest = Body(...), db: AsyncSession = Depends(get_db)):
    """Alias endpoint for frontend compatibility.

    Delegates to the existing `/candidate/apply` handler.
    If it fails, it propagates the HTTPException.
    """
    try:
        return await candidate_apply(payload, db)
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"[API/APPLY] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal error during apply")
