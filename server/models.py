from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, JSON


class RoleName(str, Enum):
    ADMIN = "ADMIN"
    MATERIAL_CONTROL = "MATERIAL_CONTROL"
    WAREHOUSE = "WAREHOUSE"
    MEDIATOR = "MEDIATOR"
    REQUESTER = "REQUESTER"


class Permission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    description: Optional[str] = None


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: RoleName = Field(index=True, unique=True)
    permissions: List["RolePermission"] = Relationship(back_populates="role")


class RolePermission(SQLModel, table=True):
    role_id: int = Field(foreign_key="role.id", primary_key=True)
    permission_id: int = Field(foreign_key="permission.id", primary_key=True)
    role: Role = Relationship(back_populates="permissions")
    permission: Permission = Relationship()


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    employee_number: str = Field(index=True)
    email: Optional[str] = Field(default=None, index=True)
    phone: Optional[str] = None
    hashed_password: str
    role_id: int = Field(foreign_key="role.id")
    role: Optional[Role] = Relationship()
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Aircraft(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: str = Field(index=True, unique=True)
    description: Optional[str] = None


class JobOrder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_control_number: str = Field(index=True)
    description: Optional[str] = None
    aircraft_id: int = Field(foreign_key="aircraft.id")
    aircraft: Optional[Aircraft] = Relationship()
    status: str = Field(default="OPEN")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Part(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    part_number: str = Field(index=True, unique=True)
    description: Optional[str] = None
    unit: Optional[str] = None
    stock_qty: int = Field(default=0)
    location: Optional[str] = None
    metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PREPARATION = "PREPARATION"
    READY = "READY"
    DELIVERED = "DELIVERED"
    CLOSED = "CLOSED"


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    receipt_number: str = Field(index=True, unique=True)
    requester_id: int = Field(foreign_key="user.id")
    mediator_id: Optional[int] = Field(default=None, foreign_key="user.id")
    warehouse_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    job_order_id: int = Field(foreign_key="joborder.id")
    aircraft_id: int = Field(foreign_key="aircraft.id")
    part_id: int = Field(foreign_key="part.id")
    quantity: int
    request_location: str
    status: OrderStatus = Field(default=OrderStatus.PENDING, index=True)
    receiver_employee_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None

    aircraft: Optional[Aircraft] = Relationship()
    job_order: Optional[JobOrder] = Relationship()
    part: Optional[Part] = Relationship()


class StatusHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    previous_status: Optional[OrderStatus] = None
    new_status: OrderStatus
    note: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")


class NotificationType(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    IN_APP = "IN_APP"


class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: NotificationType
    user_id: int = Field(foreign_key="user.id")
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    content: str
    status: str = Field(default="SENT")
    sent_at: datetime = Field(default_factory=datetime.utcnow)


class ReportSnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    report_type: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    payload: Optional[dict] = Field(default=None, sa_column=Column(JSON))