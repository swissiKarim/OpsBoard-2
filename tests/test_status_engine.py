"""Unit tests for compute_service_status() – covers AC-2 and AC-3.

Tests cover:
- operational: no open incidents
- degraded: only SEV2/SEV3 open incidents
- outage: at least one open SEV1 incident
- transition: outage → operational after SEV1 is resolved
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Incident, Service
from app.status_engine import compute_service_status


@pytest.fixture(scope="module")
def engine():
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture()
def db(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture()
def service(db):
    svc = Service(name="TestService", description="", team="ops", computed_status="operational")
    db.add(svc)
    db.commit()
    db.refresh(svc)
    yield svc
    db.delete(svc)
    db.commit()


def _add_incident(db, service_id, severity, status="open"):
    inc = Incident(
        title=f"{severity} incident",
        service_id=service_id,
        severity=severity,
        status=status,
        description="",
    )
    db.add(inc)
    db.commit()
    db.refresh(inc)
    return inc


def test_operational_no_incidents(db, service):
    """No open incidents → operational."""
    result = compute_service_status(service.id, db)
    assert result == "operational"


def test_outage_open_sev1(db, service):
    """Open SEV1 → outage."""
    inc = _add_incident(db, service.id, "SEV1", "open")
    result = compute_service_status(service.id, db)
    assert result == "outage"
    db.delete(inc)
    db.commit()


def test_degraded_open_sev2(db, service):
    """Open SEV2 (no SEV1) → degraded."""
    inc = _add_incident(db, service.id, "SEV2", "open")
    result = compute_service_status(service.id, db)
    assert result == "degraded"
    db.delete(inc)
    db.commit()


def test_degraded_open_sev3(db, service):
    """Open SEV3 (no SEV1) → degraded."""
    inc = _add_incident(db, service.id, "SEV3", "investigating")
    result = compute_service_status(service.id, db)
    assert result == "degraded"
    db.delete(inc)
    db.commit()


def test_outage_sev1_dominates_sev2(db, service):
    """Open SEV1 and SEV2 together → outage (SEV1 dominates)."""
    inc1 = _add_incident(db, service.id, "SEV1", "open")
    inc2 = _add_incident(db, service.id, "SEV2", "open")
    result = compute_service_status(service.id, db)
    assert result == "outage"
    db.delete(inc1)
    db.delete(inc2)
    db.commit()


def test_transition_outage_to_operational_after_sev1_resolved(db, service):
    """After SEV1 is resolved and no other open incidents remain → operational."""
    inc = _add_incident(db, service.id, "SEV1", "open")
    assert compute_service_status(service.id, db) == "outage"

    # Resolve the SEV1 incident
    inc.status = "resolved"
    db.commit()

    result = compute_service_status(service.id, db)
    assert result == "operational"
    db.delete(inc)
    db.commit()


def test_resolved_sev1_does_not_cause_outage(db, service):
    """A resolved SEV1 incident does not count towards status."""
    inc = _add_incident(db, service.id, "SEV1", "resolved")
    result = compute_service_status(service.id, db)
    assert result == "operational"
    db.delete(inc)
    db.commit()


def test_investigating_sev2_counts_as_open(db, service):
    """An 'investigating' SEV2 is not resolved → degraded."""
    inc = _add_incident(db, service.id, "SEV2", "investigating")
    result = compute_service_status(service.id, db)
    assert result == "degraded"
    db.delete(inc)
    db.commit()
