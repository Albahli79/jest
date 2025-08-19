from sqlmodel import Session, select
from .database import engine
from .models import Role, RoleName, User, Aircraft, JobOrder, Part
from .auth import get_password_hash


def ensure_role(session: Session, name: RoleName) -> Role:
    role = session.exec(select(Role).where(Role.name == name)).first()
    if role is None:
        role = Role(name=name)
        session.add(role)
        session.commit()
        session.refresh(role)
    return role


def ensure_user(session: Session, username: str, password: str, employee_number: str, role: Role) -> None:
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        user = User(
            username=username,
            employee_number=employee_number,
            hashed_password=get_password_hash(password),
            role_id=role.id,
        )
        session.add(user)
        session.commit()


def ensure_aircraft(session: Session, number: str, description: str = "") -> Aircraft:
    ac = session.exec(select(Aircraft).where(Aircraft.number == number)).first()
    if ac is None:
        ac = Aircraft(number=number, description=description)
        session.add(ac)
        session.commit()
        session.refresh(ac)
    return ac


def ensure_job(session: Session, jcn: str, aircraft: Aircraft, description: str = "") -> JobOrder:
    job = session.exec(select(JobOrder).where(JobOrder.job_control_number == jcn)).first()
    if job is None:
        job = JobOrder(job_control_number=jcn, description=description, aircraft_id=aircraft.id)
        session.add(job)
        session.commit()
        session.refresh(job)
    return job


def ensure_part(session: Session, part_number: str, description: str, stock_qty: int, location: str) -> Part:
    part = session.exec(select(Part).where(Part.part_number == part_number)).first()
    if part is None:
        part = Part(part_number=part_number, description=description, unit="EA", stock_qty=stock_qty, location=location)
        session.add(part)
        session.commit()
        session.refresh(part)
    return part


if __name__ == "__main__":
    with Session(engine) as session:
        roles = {r: ensure_role(session, r) for r in RoleName}
        ensure_user(session, "admin", "admin123", "E0001", roles[RoleName.ADMIN])
        ensure_user(session, "mcadmin", "mc123", "E0002", roles[RoleName.MATERIAL_CONTROL])
        ensure_user(session, "warehouse1", "wh123", "E0003", roles[RoleName.WAREHOUSE])
        ensure_user(session, "mediator1", "med123", "E0004", roles[RoleName.MEDIATOR])
        ensure_user(session, "requester1", "req123", "E0005", roles[RoleName.REQUESTER])

        ac = ensure_aircraft(session, "AC-1001", "Boeing 737")
        job = ensure_job(session, "JCN-2025-0001", ac, "Engine maintenance")
        ensure_part(session, "P-0001", "Hydraulic Pump", 10, "A1-01")
        ensure_part(session, "P-0002", "Fuel Filter", 25, "B2-03")

        print("Seed complete.")