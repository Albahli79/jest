from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..database import get_session
from ..models import Order, OrderStatus
from ..schemas import ReportFilter, PerformanceReport, BottleneckReport, BottleneckItem
from ..auth import require_roles
from ..models import RoleName

router = APIRouter()


def _avg(seconds_list):
    vals = [s for s in seconds_list if s is not None]
    return sum(vals) / len(vals) if vals else None


@router.post("/performance", response_model=PerformanceReport)
async def performance(filter: ReportFilter, session: Session = Depends(get_session), _: object = Depends(require_roles(RoleName.ADMIN))):
    query = select(Order)
    if filter.start:
        query = query.where(Order.created_at >= filter.start)
    if filter.end:
        query = query.where(Order.created_at <= filter.end)
    if filter.status:
        query = query.where(Order.status == filter.status)
    if filter.mediator_id:
        query = query.where(Order.mediator_id == filter.mediator_id)
    if filter.warehouse_user_id:
        query = query.where(Order.warehouse_user_id == filter.warehouse_user_id)

    orders = session.exec(query).all()
    p2prep = []
    prep2ready = []
    ready2del = []
    total = []
    for o in orders:
        # We infer times via updated_at and delivered_at simplistically; for accuracy use StatusHistory in production
        if o.status in {OrderStatus.PREPARATION, OrderStatus.READY, OrderStatus.DELIVERED, OrderStatus.CLOSED}:
            p2prep.append((o.updated_at - o.created_at).total_seconds())
        else:
            p2prep.append(None)
        if o.status in {OrderStatus.READY, OrderStatus.DELIVERED, OrderStatus.CLOSED}:
            prep2ready.append(0.0)  # Placeholder; compute from history table in a richer implementation
        else:
            prep2ready.append(None)
        if o.delivered_at:
            ready2del.append(0.0)  # Placeholder; compute from history
            total.append((o.delivered_at - o.created_at).total_seconds())
        else:
            ready2del.append(None)
            total.append(None)

    return PerformanceReport(
        total_orders=len(orders),
        avg_pending_to_prep_seconds=_avg(p2prep),
        avg_prep_to_ready_seconds=_avg(prep2ready),
        avg_ready_to_delivered_seconds=_avg(ready2del),
        avg_total_cycle_seconds=_avg(total),
    )


@router.post("/bottlenecks", response_model=BottleneckReport)
async def bottlenecks(filter: ReportFilter, session: Session = Depends(get_session), _: object = Depends(require_roles(RoleName.ADMIN))):
    query = select(Order)
    if filter.start:
        query = query.where(Order.created_at >= filter.start)
    if filter.end:
        query = query.where(Order.created_at <= filter.end)
    orders = session.exec(query).all()
    counts = {
        OrderStatus.PENDING: 0,
        OrderStatus.PREPARATION: 0,
        OrderStatus.READY: 0,
        OrderStatus.DELIVERED: 0,
        OrderStatus.CLOSED: 0,
    }
    for o in orders:
        counts[o.status] += 1
    items = [BottleneckItem(stage=s.name, count=c) for s, c in counts.items() if c > 0]
    return BottleneckReport(items=items)