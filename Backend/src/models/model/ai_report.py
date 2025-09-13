
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from db_schemes.schemes.base import Base
from ..enums import ReportType


class AI_Report(Base):
    __tablename__ = "ai_reports"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    summary_text = Column(Text, nullable=False)
    file_path = Column(String(512))
    report_type = Column(Enum(ReportType), nullable=False)
    
    user = relationship("User", back_populates="ai_reports")
