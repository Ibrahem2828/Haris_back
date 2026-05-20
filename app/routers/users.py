from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=schemas.UserRead)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail="Username already exists.")
    return crud.create_user(db, payload)


@router.get("", response_model=list[schemas.UserRead])
def list_users(db: Session = Depends(get_db)):
    return crud.get_users(db)


@router.get("/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.post("/login")
def simple_login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, payload.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": "Login accepted for educational version.", "user_id": user.id, "username": user.username, "role": user.role}
