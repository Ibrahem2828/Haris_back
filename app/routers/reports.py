from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/security-summary")
def security_summary(db: Session = Depends(get_db)):
    return {
        "project": "Haris",
        "summary": DashboardService(db).summary(),
        "note": "Educational report. Cisco IOS commands are suggestions only.",
    }


@router.get("/incidents", response_model=list[schemas.AlertRead])
def incidents_report(db: Session = Depends(get_db)):
    return db.query(models.Alert).order_by(models.Alert.created_at.desc()).all()


@router.get("/rules", response_model=list[schemas.DetectionRuleRead])
def rules_report(db: Session = Depends(get_db)):
    return db.query(models.DetectionRule).order_by(models.DetectionRule.id).all()
