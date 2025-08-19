from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import JobOrder, Aircraft, RoleName
from ..schemas import JobOrderRead
from ..auth import require_roles

router = APIRouter()


@router.get("/", response_model=List[JobOrderRead])
async def list_jobs(session: Session = Depends(get_session), _: object = Depends(require_roles(RoleName.ADMIN, RoleName.MATERIAL_CONTROL, RoleName.REQUESTER))):
    rows = session.exec(select(JobOrder).order_by(JobOrder.created_at.desc())).all()
    return [JobOrderRead(**j.model_dump()) for j in rows]  # type: ignore[arg-type]


@router.post("/", response_model=JobOrderRead)
async def create_job(payload: JobOrderRead, session: Session = Depends(get_session), _: object = Depends(require_roles(RoleName.ADMIN))):
    if session.exec(select(JobOrder).where(JobOrder.job_control_number == payload.job_control_number)).first():
        raise HTTPException(status_code=400, detail="Job control number exists")
    ac = session.get(Aircraft, payload.aircraft_id)
    if ac is None:
        raise HTTPException(status_code=400, detail="Aircraft not found")
    j = JobOrder(job_control_number=payload.job_control_number, description=payload.description, aircraft_id=payload.aircraft_id)
    session.add(j)
    session.commit()
    session.refresh(j)
    return JobOrderRead(**j.model_dump())  # type: ignore[arg-type]