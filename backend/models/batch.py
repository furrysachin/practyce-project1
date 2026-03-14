"""Batch model - one per uploaded JSON file."""
from sqlalchemy import Column, Integer, String, Date, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class Batch(Base):
    __tablename__ = "batches"

    batch_id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(512), nullable=False, unique=True)
    source_batch = Column(String(64), nullable=True)
    total_records = Column(Integer, default=0)
    date_from = Column(Date)
    date_to = Column(Date)
    generated_at = Column(DateTime(timezone=True))
    uploaded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    transactions = relationship("Transaction", back_populates="batch")
    metadata_entries = relationship("Metadata", back_populates="batch", cascade="all, delete-orphan")
