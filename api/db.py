from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    wallet_balance = Column(Float, default=0.0)
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    telegram_id = Column(String, index=True)
    type = Column(String)  # deposit|withdrawal
    method = Column(String)  # bank|upi
    details = Column(Text)  # json text for extra fields
    amount = Column(Float, default=0.0)
    status = Column(String, default="pending")  # pending|completed|cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
