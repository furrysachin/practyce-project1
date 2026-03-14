"""Customer model - master data from account_information."""
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(32), primary_key=True)
    name = Column(String(256), nullable=False)
    email = Column(String(256))
    phone = Column(String(32))
    pan_number = Column(String(32))
    customer_segment = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    accounts = relationship("Account", back_populates="customer")
