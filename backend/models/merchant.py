"""Merchant model - master data from channel_information."""
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    merchant_id = Column(String(32), primary_key=True)
    merchant_name = Column(String(256), nullable=False)
    category = Column(String(32))
    location = Column(String(128))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transactions = relationship("Transaction", back_populates="merchant")
