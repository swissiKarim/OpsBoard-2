"""Central service-status engine for OpsBoard.

Business rules (BR-01, BR-02):
- outage    : at least one open SEV1 incident exists for the service
- degraded  : at least one open SEV2 or SEV3 incident exists (and no SEV1)
- operational: no open incidents remain

This function is the single source of truth used by both the UI and REST API.
"""

from sqlalchemy.orm import Session

from app import models


def compute_service_status(service_id: int, db: Session) -> str:
    """Return the derived status for a service based on its open incidents.

    Parameters
    ----------
    service_id:
        Primary key of the service to evaluate.
    db:
        Active SQLAlchemy session.

    Returns
    -------
    "outage" | "degraded" | "operational"
    """
    open_incidents = (
        db.query(models.Incident)
        .filter(
            models.Incident.service_id == service_id,
            models.Incident.status != "resolved",
        )
        .all()
    )

    if any(i.severity == "SEV1" for i in open_incidents):
        return "outage"
    if any(i.severity in ("SEV2", "SEV3") for i in open_incidents):
        return "degraded"
    return "operational"
