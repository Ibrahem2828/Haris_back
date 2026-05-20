from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.constants import RESPONSE_APPROVED, RESPONSE_REJECTED
from app.database import get_db
from app.services.response_module import ResponseModule

router = APIRouter(prefix="/responses", tags=["Responses"])


@router.get("", response_model=list[schemas.ResponseRead])
def list_responses(db: Session = Depends(get_db)):
    return db.query(models.Response).order_by(models.Response.created_at.desc()).all()


@router.get("/{response_id}", response_model=schemas.ResponseRead)
def get_response(response_id: int, db: Session = Depends(get_db)):
    response = db.query(models.Response).filter(models.Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found.")
    return response


@router.post("/generate/{alert_id}", response_model=schemas.ResponseRead)
def generate_response(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    existing = db.query(models.Response).filter(models.Response.alert_id == alert.id).first()
    if existing:
        return existing
    data = ResponseModule().generate_response(alert)
    response = models.Response(
        alert_id=alert.id,
        action_type=data["recommended_action"],
        description=data["explanation"],
        cisco_command=data["cisco_command"],
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    return response


@router.patch("/{response_id}/approve", response_model=schemas.ResponseRead)
def approve_response(response_id: int, db: Session = Depends(get_db)):
    response = db.query(models.Response).filter(models.Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found.")
    response.execution_status = RESPONSE_APPROVED
    db.commit()
    db.refresh(response)
    return response


@router.patch("/{response_id}/reject", response_model=schemas.ResponseRead)
def reject_response(response_id: int, db: Session = Depends(get_db)):
    response = db.query(models.Response).filter(models.Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found.")
    response.execution_status = RESPONSE_REJECTED
    db.commit()
    db.refresh(response)
    return response
