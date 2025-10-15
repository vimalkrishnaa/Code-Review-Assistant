from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from database.db import Base

class ReviewRecord(Base):
    """SQLAlchemy model for storing code review records"""
    __tablename__ = "review_records"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False, index=True)
    review_json = Column(JSON, nullable=False)
    overall_score = Column(Float, nullable=False, index=True)
    language = Column(String, nullable=True)
    file_size = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)
    total_issues = Column(Integer, nullable=True, default=0)
    critical_issues = Column(Integer, nullable=True, default=0)
    high_issues = Column(Integer, nullable=True, default=0)
    medium_issues = Column(Integer, nullable=True, default=0)
    low_issues = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ReviewRecord(id={self.id}, filename='{self.filename}', score={self.overall_score}, created_at='{self.created_at}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            "id": self.id,
            "filename": self.filename,
            "overall_score": self.overall_score,
            "language": self.language,
            "file_size": self.file_size,
            "processing_time": self.processing_time,
            "total_issues": self.total_issues,
            "critical_issues": self.critical_issues,
            "high_issues": self.high_issues,
            "medium_issues": self.medium_issues,
            "low_issues": self.low_issues,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
