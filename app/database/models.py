from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    event_name = Column(String(255), nullable=False)

    status = Column(String(50), nullable=False, default="QUEUED")

    total_count = Column(Integer, nullable=False, default=0)

    completed_count = Column(Integer, nullable=False, default=0)

    failed_count = Column(Integer, nullable=False, default=0)

    created_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc)
)
    completed_at = Column(DateTime, nullable=True)

    certificates = relationship(
        "Certificate",
        back_populates="job",
        cascade="all, delete-orphan"
    )

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False
    )

    recipient_name = Column(String(255), nullable=False)

    recipient_email = Column(String(255), nullable=True)

    status = Column(
        String(50),
        nullable=False,
        default="PENDING"
    )

    file_path = Column(String(500), nullable=True)

    error_message = Column(Text, nullable=True)

    created_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc)
)

    job = relationship(
        "Job",
        back_populates="certificates"
    )