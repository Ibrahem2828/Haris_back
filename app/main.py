from fastapi import FastAPI

from app import crud
from app.core.config import settings
from app.database import SessionLocal, init_db
from app.routers import alerts, arp, dashboard, detection, events, reports, responses, simulation, users

app = FastAPI(
    title="Haris / حارس Backend",
    description="Educational rule-based network attack detection, ARP analysis, and Cisco IOS response suggestion API.",
    version=settings.version,
)


@app.on_event("startup")
def startup():
    init_db()
    if settings.seed_on_startup:
        db = SessionLocal()
        try:
            crud.seed_defaults(db)
        finally:
            db.close()


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "project": settings.app_name, "version": settings.version}


app.include_router(users.router)
app.include_router(events.router)
app.include_router(simulation.router)
app.include_router(detection.router)
app.include_router(alerts.router)
app.include_router(responses.router)
app.include_router(arp.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
