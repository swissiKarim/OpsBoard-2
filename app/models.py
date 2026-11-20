"""SQLAlchemy ORM models for OpsBoard."""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class Service(Base):
    __tablename__ = "service"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, default="")
    team = Column(String(255), default="")
    # computed_status is always derived via compute_service_status(); never set directly
    computed_status = Column(
        String(50),
        default="operational",
        nullable=False,
    )
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    incidents = relationship("Incident", back_populates="service")


class Incident(Base):
    __tablename__ = "incident"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    severity = Column(Enum("SEV1", "SEV2", "SEV3", name="severity_enum"), nullable=False)
    status = Column(
        Enum("open", "investigating", "resolved", name="incident_status_enum"),
        default="open",
        nullable=False,
    )
    service_id = Column(Integer, ForeignKey("service.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime, nullable=True)

    service = relationship("Service", back_populates="incidents")
    timeline_entries = relationship(
        "TimelineEntry",
        back_populates="incident",
        order_by="TimelineEntry.created_at",
    )


class TimelineEntry(Base):
    __tablename__ = "timeline_entry"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incident.id"), nullable=False)
    author = Column(String(255), default="system")
    comment = Column(Text, default="")
    status_from = Column(String(50), nullable=True)
    status_to = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())

    incident = relationship("Incident", back_populates="timeline_entries")
