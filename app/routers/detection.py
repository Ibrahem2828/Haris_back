from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.services.detection_engine import DetectionEngine

router = APIRouter(tags=["Detection"])


@router.post("/detect", response_model=schemas.DetectResponse)
def detect_all(db: Session = Depends(get_db)):
    analyzed, created = DetectionEngine(db).analyze_all_events()
    return {"analyzed_events": analyzed, "created_alerts": created, "message": "Detection completed."}


@router.post("/detect/event/{event_id}")
def detect_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    alerts = DetectionEngine(db).analyze_event(event)
    return {"event_id": event_id, "created_or_matched_alerts": len(alerts), "alerts": [alert.id for alert in alerts]}


@router.post("/detect/run-all", response_model=schemas.DetectResponse)
def detect_run_all(db: Session = Depends(get_db)):
    analyzed, created = DetectionEngine(db).analyze_all_events()
    return {"analyzed_events": analyzed, "created_alerts": created, "message": "All events analyzed."}


@router.get("/rules", response_model=list[schemas.DetectionRuleRead])
def list_rules(db: Session = Depends(get_db)):
    return db.query(models.DetectionRule).order_by(models.DetectionRule.id).all()


@router.post("/rules", response_model=schemas.DetectionRuleRead)
def create_rule(payload: schemas.DetectionRuleCreate, db: Session = Depends(get_db)):
    return crud.create_rule(db, payload)


@router.put("/rules/{rule_id}", response_model=schemas.DetectionRuleRead)
def update_rule(rule_id: int, payload: schemas.DetectionRuleUpdate, db: Session = Depends(get_db)):
    rule = db.query(models.DetectionRule).filter(models.DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found.")
    return crud.update_rule(db, rule, payload)


@router.patch("/rules/{rule_id}/enable", response_model=schemas.DetectionRuleRead)
def enable_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(models.DetectionRule).filter(models.DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found.")
    rule.enabled = True
    db.commit()
    db.refresh(rule)
    return rule


@router.patch("/rules/{rule_id}/disable", response_model=schemas.DetectionRuleRead)
def disable_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(models.DetectionRule).filter(models.DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found.")
    rule.enabled = False
    db.commit()
    db.refresh(rule)
    return rule
