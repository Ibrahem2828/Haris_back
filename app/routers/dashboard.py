from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    return DashboardService(db).summary()


@router.get("/statistics")
def dashboard_statistics(db: Session = Depends(get_db)):
    return DashboardService(db).statistics()


@router.get("/attack-distribution")
def attack_distribution(db: Session = Depends(get_db)):
    return DashboardService(db).attack_distribution()


@router.get("/latest-alerts", response_model=list[schemas.AlertRead])
def latest_dashboard_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).order_by(models.Alert.created_at.desc()).limit(5).all()


@router.get("/network-status")
def network_status(db: Session = Depends(get_db)):
    return DashboardService(db).network_status()
