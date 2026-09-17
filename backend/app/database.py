from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import os

# Handle DATABASE_URL for both postgres and sqlite
database_url = settings.DATABASE_URL

# For sqlite, need check_same_thread
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # Ensure path is absolute for sqlite
    if database_url == "sqlite:///./crimenet.db":
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crimenet.db")
        database_url = f"sqlite:///{db_path}"

engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from .models import all_models  # noqa
    Base.metadata.create_all(bind=engine)
