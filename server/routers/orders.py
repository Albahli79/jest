from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Order, OrderStatus, StatusHistory, User, RoleName, Part
from ..schemas import OrderCreate, OrderRead, OrderStatusUpdate, StatusHistoryRead
from ..auth import get_current_user, require_roles
from ..websocket_manager import ws_send
from ..notifications import send_notification, NotificationType, format_order_notification

router = APIRouter()


def generate_receipt_number() -> str:
    return datetime.utcnow().strftime("RCPT%Y%m%d%H%M%S%f")


@router.post("/", response_model=OrderRead)
async def create_order(payload: OrderCreate, session: Session = Depends(get_session), user: User = Depends(require_roles(RoleName.REQUESTER, RoleName.ADMIN))):
    part = session.get(Part, payload.part_id)
    if part is None:
        raise HTTPException(status_code=400, detail="Part not found")
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    order = Order(
        receipt_number=generate_receipt_number(),
        requester_id=user.id,
        mediator_id=None,
        warehouse_user_id=None,
        job_order_id=payload.job_order_id,
        aircraft_id=payload.aircraft_id,
        part_id=payload.part_id,
        quantity=payload.quantity,
        request_location=payload.request_location,
        status=OrderStatus.PENDING,
    )
    session.add(order)
    session.commit()
    session.refresh(order)

    history = StatusHistory(order_id=order.id, previous_status=None, new_status=OrderStatus.PENDING, note="Order created", user_id=user.id)
    session.add(history)
    session.commit()

    message = format_order_notification("New Request", order.receipt_number, order.status)
    await ws_send(user.username, {"type": "order_created", "receipt": order.receipt_number})
    send_notification(NotificationType.IN_APP, user.username, message)
    return OrderRead(**order.model_dump())  # type: ignore[arg-type]


@router.get("/", response_model=List[OrderRead])
async def list_orders(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    query = select(Order)
    if user.role and user.role.name == RoleName.REQUESTER:
        query = query.where(Order.requester_id == user.id)
    orders = session.exec(query.order_by(Order.created_at.desc())).all()
    return [OrderRead(**o.model_dump()) for o in orders]  # type: ignore[arg-type]


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: int, session: Session = Depends(get_session), _: User = Depends(get_current_user)):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderRead(**order.model_dump())  # type: ignore[arg-type]


@router.get("/{order_id}/history", response_model=List[StatusHistoryRead])
async def get_history(order_id: int, session: Session = Depends(get_session), _: User = Depends(get_current_user)):
    rows = session.exec(select(StatusHistory).where(StatusHistory.order_id == order_id).order_by(StatusHistory.timestamp.asc())).all()
    result: List[StatusHistoryRead] = []
    for h in rows:
        result.append(StatusHistoryRead(**h.model_dump()))  # type: ignore[arg-type]
    return result


@router.post("/{order_id}/status", response_model=OrderRead)
async def update_status(order_id: int, payload: OrderStatusUpdate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    allowed_transitions = {
        OrderStatus.PENDING: {OrderStatus.PREPARATION},
        OrderStatus.PREPARATION: {OrderStatus.READY},
        OrderStatus.READY: {OrderStatus.DELIVERED},
        OrderStatus.DELIVERED: {OrderStatus.CLOSED},
        OrderStatus.CLOSED: set(),
    }

    if payload.new_status not in allowed_transitions[order.status]:
        raise HTTPException(status_code=400, detail=f"Invalid transition from {order.status} to {payload.new_status}")

    # Role-based guardrails
    if payload.new_status in {OrderStatus.PREPARATION, OrderStatus.READY} and (not user.role or user.role.name != RoleName.WAREHOUSE):
        raise HTTPException(status_code=403, detail="Only Warehouse can move to PREPARATION/READY")
    if payload.new_status == OrderStatus.DELIVERED and (not user.role or user.role.name != RoleName.MEDIATOR):
        raise HTTPException(status_code=403, detail="Only Mediator can move to DELIVERED")
    if payload.new_status == OrderStatus.CLOSED and (not user.role or user.role.name not in {RoleName.MEDIATOR, RoleName.ADMIN}):
        raise HTTPException(status_code=403, detail="Only Mediator/Admin can close")

    previous = order.status
    order.status = payload.new_status
    order.updated_at = datetime.utcnow()
    if payload.new_status == OrderStatus.DELIVERED:
        order.delivered_at = datetime.utcnow()
        if payload.receiver_employee_number:
            order.receiver_employee_number = payload.receiver_employee_number
    session.add(order)
    session.commit()
    session.refresh(order)

    session.add(StatusHistory(order_id=order.id, previous_status=previous, new_status=order.status, note=payload.note, user_id=user.id))
    session.commit()

    await ws_send(user.username, {"type": "order_status", "receipt": order.receipt_number, "status": order.status})
    send_notification(NotificationType.IN_APP, user.username, format_order_notification("Status", order.receipt_number, order.status))
    return OrderRead(**order.model_dump())  # type: ignore[arg-type]