"""Metadata model - batch-level key-value metadata."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class Metadata(Base):
    __tablename__ = "metadata"

    metadata_id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("batches.batch_id", ondelete="CASCADE"), nullable=False)
    meta_key = Column(String(128), nullable=False)
    meta_value = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    batch = relationship("Batch", back_populates="metadata_entries")
