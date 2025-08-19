from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
import csv
import io

from ..database import get_session
from ..models import Part, RoleName
from ..schemas import PartRead, PartUpsert
from ..auth import require_roles, get_current_user

router = APIRouter()


@router.get("/", response_model=List[PartRead])
async def list_parts(session: Session = Depends(get_session), _: object = Depends(get_current_user)):
    parts = session.exec(select(Part)).all()
    return [PartRead(**p.model_dump()) for p in parts]  # type: ignore[arg-type]


@router.post("/", response_model=PartRead)
async def upsert_part(payload: PartUpsert, session: Session = Depends(get_session), _: object = Depends(require_roles(RoleName.ADMIN, RoleName.MATERIAL_CONTROL))):
    existing = session.exec(select(Part).where(Part.part_number == payload.part_number)).first()
    if existing:
        existing.description = payload.description
        existing.unit = payload.unit
        existing.stock_qty = payload.stock_qty or 0
        existing.location = payload.location
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return PartRead(**existing.model_dump())  # type: ignore[arg-type]
    part = Part(
        part_number=payload.part_number,
        description=payload.description,
        unit=payload.unit,
        stock_qty=payload.stock_qty or 0,
        location=payload.location,
    )
    session.add(part)
    session.commit()
    session.refresh(part)
    return PartRead(**part.model_dump())  # type: ignore[arg-type]


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), session: Session = Depends(get_session), _: object = Depends(require_roles(RoleName.ADMIN, RoleName.MATERIAL_CONTROL))):
    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    required = {"part_number", "description", "unit", "stock_qty", "location"}
    for idx, row in enumerate(reader, start=1):
        if not required.issubset(set(row.keys())):
            raise HTTPException(status_code=400, detail=f"Missing required columns at row {idx}")
        try:
            stock_qty = int(row.get("stock_qty") or 0)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid stock_qty at row {idx}")
        payload = PartUpsert(
            part_number=row.get("part_number") or "",
            description=row.get("description") or None,
            unit=row.get("unit") or None,
            stock_qty=stock_qty,
            location=row.get("location") or None,
        )
        await upsert_part(payload, session)  # reuse logic
    return {"status": "ok"}