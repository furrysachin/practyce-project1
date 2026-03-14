"""Account model - one per account_number, linked to customer."""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(32), ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False)
    account_number = Column(String(64), nullable=False, unique=True)
    account_type = Column(String(64))
    status = Column(String(32))
    branch_code = Column(String(32))
    iban = Column(String(64))
    swift_code = Column(String(32))
    sort_code = Column(String(32))
    account_open_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    balance = relationship("Balance", back_populates="account", uselist=False, cascade="all, delete-orphan")
