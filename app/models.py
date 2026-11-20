"""SQLAlchemy ORM models for OpsBoard."""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, default="")
    team = Column(String(255), default="")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    incidents = relationship("Incident", back_populates="service")

    @property
    def status(self) -> str:
        """Derive status from open incidents."""
        open_incidents = [i for i in self.incidents if i.status != "resolved"]
        if any(i.severity == "SEV1" for i in open_incidents):
            return "outage"
        if any(i.severity in ("SEV2", "SEV3") for i in open_incidents):
            return "degraded"
        return "operational"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    severity = Column(Enum("SEV1", "SEV2", "SEV3", name="severity_enum"), nullable=False)
    status = Column(
        Enum("open", "investigating", "resolved", name="incident_status_enum"),
        default="open",
        nullable=False,
    )
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime, nullable=True)

    service = relationship("Service", back_populates="incidents")
    timeline_entries = relationship("TimelineEntry", back_populates="incident", order_by="TimelineEntry.created_at")


class TimelineEntry(Base):
    __tablename__ = "timeline_entries"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    author = Column(String(255), default="system")
    comment = Column(Text, default="")
    status_from = Column(String(50), nullable=True)
    status_to = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())

    incident = relationship("Incident", back_populates="timeline_entries")
