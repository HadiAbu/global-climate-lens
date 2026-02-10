import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

url = os.getenv("DATABASE_URL")
if not url:
    raise RuntimeError("DATABASE_URL is not set (inside the API container)")

engine = create_engine(url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_engine():
    return engine


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
