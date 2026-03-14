"""Transaction model - fact table."""
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String(64), primary_key=True)
    batch_id = Column(Integer, ForeignKey("batches.batch_id", ondelete="RESTRICT"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.account_id", ondelete="RESTRICT"), nullable=False)
    merchant_id = Column(String(32), ForeignKey("merchants.merchant_id", ondelete="SET NULL"))
    reference_number = Column(String(64))
    transaction_date = Column(Date, nullable=False)
    transaction_datetime = Column(DateTime(timezone=True))
    transaction_type = Column(String(64))
    transaction_category = Column(String(128))
    transaction_code = Column(String(32))
    currency_code = Column(String(8), default="INR")
    transaction_amount = Column(Numeric(18, 2), nullable=False)
    net_amount = Column(Numeric(18, 2))
    status = Column(String(32))
    status_code = Column(String(16))
    payment_network = Column(String(32))
    channel_type = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    batch = relationship("Batch", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
