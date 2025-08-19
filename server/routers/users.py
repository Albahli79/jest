from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from ..database import get_session
from ..models import User, Role, RoleName
from ..schemas import Token, UserCreate, UserRead
from ..auth import create_access_token, get_password_hash, verify_password, get_current_user, require_roles

router = APIRouter()


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)):
    return UserRead(
        id=user.id,
        username=user.username,
        employee_number=user.employee_number,
        email=user.email,
        phone=user.phone,
        role=user.role.name if user.role else RoleName.REQUESTER,
    )


@router.post("/", response_model=UserRead)
async def create_user(payload: UserCreate, session: Session = Depends(get_session), _: User = Depends(require_roles(RoleName.ADMIN))):
    role = session.exec(select(Role).where(Role.name == payload.role)).first()
    if role is None:
        raise HTTPException(status_code=400, detail="Role not found")
    if session.exec(select(User).where(User.username == payload.username)).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=payload.username,
        employee_number=payload.employee_number,
        email=payload.email,
        phone=payload.phone,
        hashed_password=get_password_hash(payload.password),
        role_id=role.id,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserRead(
        id=user.id,
        username=user.username,
        employee_number=user.employee_number,
        email=user.email,
        phone=user.phone,
        role=role.name,
    )


@router.get("/", response_model=List[UserRead])
async def list_users(session: Session = Depends(get_session), _: User = Depends(require_roles(RoleName.ADMIN))):
    users = session.exec(select(User)).all()
    result: List[UserRead] = []
    for u in users:
        result.append(UserRead(
            id=u.id,
            username=u.username,
            employee_number=u.employee_number,
            email=u.email,
            phone=u.phone,
            role=u.role.name if u.role else RoleName.REQUESTER,
        ))
    return result