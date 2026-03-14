"""Balance model - latest balance per account."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class Balance(Base):
    __tablename__ = "balances"

    balance_id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False, unique=True)
    current_balance = Column(Numeric(18, 2))
    available_balance = Column(Numeric(18, 2))
    ledger_balance = Column(Numeric(18, 2))
    as_of_transaction_id = Column(String(64))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    account = relationship("Account", back_populates="balance")
