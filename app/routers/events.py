from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.services.log_parser import parse_imported_content

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=schemas.EventRead)
def create_event(payload: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db, payload)


@router.get("", response_model=list[schemas.EventRead])
def list_events(db: Session = Depends(get_db)):
    return crud.list_events(db)


@router.post("/import", response_model=schemas.ImportResponse)
async def import_events(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    parsed_events = parse_imported_content(file.filename or "events.log", content)
    for event in parsed_events:
        crud.create_event(db, event)
    return {"imported_events": len(parsed_events), "message": "Events imported successfully."}


@router.get("/normal", response_model=list[schemas.EventRead])
def normal_events(db: Session = Depends(get_db)):
    return db.query(models.Event).filter(models.Event.is_suspicious.is_(False)).order_by(models.Event.timestamp.desc()).all()


@router.get("/suspicious", response_model=list[schemas.EventRead])
def suspicious_events(db: Session = Depends(get_db)):
    return db.query(models.Event).filter(models.Event.is_suspicious.is_(True)).order_by(models.Event.timestamp.desc()).all()


@router.get("/{event_id}", response_model=schemas.EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return event
