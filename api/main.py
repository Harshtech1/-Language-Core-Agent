"""
HSK Agent API — FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.db import connect_db, close_db
from api.routes.cron import router as cron_router
from api.routes.vocab import router as vocab_router
from api.routes.stats import router as stats_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage Motor connection lifecycle."""
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="语言核心 — Language Core Agent",
    description="730-Day Autonomous HSK 1-4 Tutor API",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS (allow Next.js dashboard) ─────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──────────────────────────────────────────────
app.include_router(cron_router, tags=["Cron"])
app.include_router(vocab_router, tags=["Vocabulary"])
app.include_router(stats_router, tags=["Stats"])


# ── Global Cron Security Middleware ─────────────────────
@app.middleware("http")
async def secure_cron_routes(request, call_next):
    """
    Global check for x-cron-secret on all /cron/* paths.
    This prevents unauthorized triggers of SRS events.
    """
    from api.config import get_settings
    settings = get_settings()

    if request.url.path.startswith("/cron/") and settings.cron_secret:
        header_secret = request.headers.get("x-cron-secret")
        if header_secret != settings.cron_secret:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401, 
                content={"detail": "Unauthorized: Invalid cron secret"}
            )
    
    return await call_next(request)


@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "agent": "语言核心",
        "version": "0.1.0",
    }
