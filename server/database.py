from sqlmodel import create_engine, Session
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def get_session() -> Session:
    with Session(engine) as session:
        yield session