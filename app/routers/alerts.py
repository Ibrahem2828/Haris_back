from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=list[schemas.AlertRead])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).order_by(models.Alert.created_at.desc()).all()


@router.get("/latest", response_model=list[schemas.AlertRead])
def latest_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).order_by(models.Alert.created_at.desc()).limit(10).all()


@router.get("/severity/{severity}", response_model=list[schemas.AlertRead])
def alerts_by_severity(severity: str, db: Session = Depends(get_db)):
    return db.query(models.Alert).filter(models.Alert.severity == severity).order_by(models.Alert.created_at.desc()).all()


@router.get("/status/{status}", response_model=list[schemas.AlertRead])
def alerts_by_status(status: str, db: Session = Depends(get_db)):
    return db.query(models.Alert).filter(models.Alert.status == status).order_by(models.Alert.created_at.desc()).all()


@router.get("/{alert_id}", response_model=schemas.AlertRead)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return alert


@router.patch("/{alert_id}/status", response_model=schemas.AlertRead)
def update_alert_status(alert_id: int, payload: schemas.AlertStatusUpdate, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    alert.status = payload.status
    db.commit()
    db.refresh(alert)
    return alert
