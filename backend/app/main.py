from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth as auth_router
from .routers import topics as topics_router
from .routers import documents as documents_router
from .routers import entities as entities_router
from .routers import relationships as rel_router
from .routers import graph as graph_router
from .routers import jobs as jobs_router, audit as audit_router, admin as admin_router
from .routers import cognitive as cog_router
from .routers import blueprint as bp_router
from .config import settings

app = FastAPI(title="NKG", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(topics_router.router)
app.include_router(documents_router.router)
app.include_router(entities_router.router)
app.include_router(rel_router.router)
app.include_router(graph_router.router)
app.include_router(jobs_router.router)
app.include_router(audit_router.router)
app.include_router(admin_router.router)
app.include_router(cog_router.router)
app.include_router(bp_router.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "rag_enabled": settings.rag_enabled,
            "sql_console_enabled": settings.sql_console_enabled}
