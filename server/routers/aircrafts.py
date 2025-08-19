from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Aircraft, RoleName
from ..schemas import AircraftRead
from ..auth import require_roles

router = APIRouter()


@router.get("/", response_model=List[AircraftRead])
async def list_aircrafts(session: Session = Depends(get_session), _: object = Depends(require_roles(RoleName.ADMIN, RoleName.MATERIAL_CONTROL, RoleName.REQUESTER))):
    rows = session.exec(select(Aircraft).order_by(Aircraft.number)).all()
    return [AircraftRead(**a.model_dump()) for a in rows]  # type: ignore[arg-type]


@router.post("/", response_model=AircraftRead)
async def create_aircraft(payload: AircraftRead, session: Session = Depends(get_session), _: object = Depends(require_roles(RoleName.ADMIN))):
    if session.exec(select(Aircraft).where(Aircraft.number == payload.number)).first():
        raise HTTPException(status_code=400, detail="Aircraft number exists")
    a = Aircraft(number=payload.number, description=payload.description)
    session.add(a)
    session.commit()
    session.refresh(a)
    return AircraftRead(**a.model_dump())  # type: ignore[arg-type]