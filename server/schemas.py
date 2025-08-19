from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel

from .models import RoleName, OrderStatus


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(SQLModel):
    username: str
    password: str


class UserRead(SQLModel):
    id: int
    username: str
    employee_number: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: RoleName


class UserCreate(SQLModel):
    username: str
    employee_number: str
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    role: RoleName


class AircraftRead(SQLModel):
    id: int
    number: str
    description: Optional[str] = None


class JobOrderRead(SQLModel):
    id: int
    job_control_number: str
    description: Optional[str] = None
    aircraft_id: int


class PartRead(SQLModel):
    id: int
    part_number: str
    description: Optional[str] = None
    unit: Optional[str] = None
    stock_qty: int
    location: Optional[str] = None


class PartUpsert(SQLModel):
    part_number: str
    description: Optional[str] = None
    unit: Optional[str] = None
    stock_qty: Optional[int] = 0
    location: Optional[str] = None


class OrderCreate(SQLModel):
    aircraft_id: int
    job_order_id: int
    part_id: int
    quantity: int
    request_location: str


class OrderRead(SQLModel):
    id: int
    receipt_number: str
    status: OrderStatus
    quantity: int
    request_location: str
    requester_id: int
    mediator_id: Optional[int] = None
    warehouse_user_id: Optional[int] = None
    aircraft_id: int
    job_order_id: int
    part_id: int
    receiver_employee_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    delivered_at: Optional[datetime] = None


class OrderStatusUpdate(SQLModel):
    new_status: OrderStatus
    note: Optional[str] = None
    receiver_employee_number: Optional[str] = None


class StatusHistoryRead(SQLModel):
    id: int
    order_id: int
    previous_status: Optional[OrderStatus]
    new_status: OrderStatus
    note: Optional[str]
    timestamp: datetime
    user_id: int


class ReportFilter(SQLModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    status: Optional[OrderStatus] = None
    mediator_id: Optional[int] = None
    warehouse_user_id: Optional[int] = None


class PerformanceReport(SQLModel):
    total_orders: int
    avg_pending_to_prep_seconds: Optional[float]
    avg_prep_to_ready_seconds: Optional[float]
    avg_ready_to_delivered_seconds: Optional[float]
    avg_total_cycle_seconds: Optional[float]


class BottleneckItem(SQLModel):
    stage: str
    count: int


class BottleneckReport(SQLModel):
    items: List[BottleneckItem]