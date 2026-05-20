from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.services.arp_analyzer import ARPAnalyzer

router = APIRouter(prefix="/arp", tags=["ARP"])


@router.post("/analyze", response_model=schemas.ARPAnalysisRead)
def analyze_arp(payload: schemas.ARPAnalyzeRequest, db: Session = Depends(get_db)):
    if payload.event_id:
        event = crud.get_event(db, payload.event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found.")
    else:
        if not payload.ip_address or not payload.mac_address:
            raise HTTPException(status_code=400, detail="ip_address and mac_address are required when event_id is not provided.")
        event = models.Event(
            source_ip=payload.ip_address,
            protocol="ARP",
            event_type="arp_event",
            status="unsolicited_reply" if payload.is_unsolicited else "reply",
            source_mac=payload.mac_address,
            raw_message=payload.observation_type,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
    analyzer = ARPAnalyzer(db)
    analysis = analyzer.analyze_arp_event(event)
    analyzer.generate_arp_alert(event)
    return analysis


@router.get("/results", response_model=list[schemas.ARPAnalysisRead])
def arp_results(db: Session = Depends(get_db)):
    return db.query(models.ARPAnalysis).order_by(models.ARPAnalysis.timestamp.desc()).all()


@router.get("/suspicious", response_model=list[schemas.ARPAnalysisRead])
def suspicious_arp(db: Session = Depends(get_db)):
    return db.query(models.ARPAnalysis).filter(models.ARPAnalysis.severity.in_(["High", "Critical"])).order_by(models.ARPAnalysis.timestamp.desc()).all()
