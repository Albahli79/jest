from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .database import engine
from .routers import users, orders, parts, reports
from .websocket_manager import router as ws_router
from .routers import aircrafts, jobs

app = FastAPI(title="Order Parts and Items System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    SQLModel.metadata.create_all(engine)


app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(parts.router, prefix="/api/parts", tags=["parts"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(aircrafts.router, prefix="/api/aircrafts", tags=["aircrafts"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(ws_router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root() -> dict:
    return {"service": "Order Parts and Items System", "status": "ok"}