from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from ..database import Base

class FinancialAccount(Base):
    __tablename__ = "financial_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    masked_account_number = Column(String, unique=True, index=True, nullable=False)
    institution = Column(String)
    account_type = Column(String)
    owner_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    owner_name = Column(String)
    balance_range = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    sender_account = Column(String, index=True)
    sender_account_id = Column(Integer, ForeignKey("financial_accounts.id"), nullable=True)
    receiver_account = Column(String, index=True)
    receiver_account_id = Column(Integer, ForeignKey("financial_accounts.id"), nullable=True)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    location = Column(String)
    transaction_type = Column(String)
    description = Column(Text)
    risk_flag = Column(String, default="NORMAL")
