"""Seed command for OpsBoard demo data.

Creates 6 services and 25 incidents distributed across the last 30 days.
Covers all severities (SEV1, SEV2, SEV3) and all statuses (open, investigating, resolved).

Usage:
    python -m app.seed

Note: Run on a fresh database or use --clear to wipe existing data first.
The command is idempotent: if data already exists it clears and re-seeds.
"""

import sys
from datetime import datetime, timedelta, timezone


def seed():
    from app import models
    from app.database import SessionLocal, init_db

    init_db()
    db = SessionLocal()

    try:
        # Idempotent: clear existing data
        existing_services = db.query(models.Service).count()
        existing_incidents = db.query(models.Incident).count()
        if existing_services > 0 or existing_incidents > 0:
            print(
                f"Database already has {existing_services} services and "
                f"{existing_incidents} incidents. Clearing and re-seeding...",
                flush=True,
            )
            db.query(models.TimelineEntry).delete()
            db.query(models.Incident).delete()
            db.query(models.Service).delete()
            db.commit()

        now = datetime.now(timezone.utc)

        # ------------------------------------------------------------------
        # 6 Services
        # ------------------------------------------------------------------
        services_data = [
            {
                "name": "API Gateway",
                "description": "Central entry point for all external API traffic.",
                "team": "Platform",
            },
            {
                "name": "Auth Service",
                "description": "Handles authentication and token issuance.",
                "team": "Security",
            },
            {
                "name": "Database Cluster",
                "description": "Primary PostgreSQL cluster for persistent storage.",
                "team": "Data",
            },
            {
                "name": "Frontend CDN",
                "description": "Static asset delivery for the web application.",
                "team": "Web",
            },
            {
                "name": "Notification Service",
                "description": "Email, SMS and push notification dispatch.",
                "team": "Platform",
            },
            {
                "name": "Background Worker",
                "description": "Async job processing and task queue consumer.",
                "team": "Data",
            },
        ]

        services = []
        for svc_data in services_data:
            svc = models.Service(
                name=svc_data["name"],
                description=svc_data["description"],
                team=svc_data["team"],
                computed_status="operational",
                created_at=now - timedelta(days=60),
                updated_at=now - timedelta(days=60),
            )
            db.add(svc)
            services.append(svc)
        db.flush()

        # ------------------------------------------------------------------
        # 25 Incidents spread across last 30 days
        # Covers: SEV1 × SEV2 × SEV3, all statuses (open/investigating/resolved)
        # ------------------------------------------------------------------
        incidents_data = [
            # SEV1 resolved (days_ago_created, days_ago_resolved, service_idx, status, severity, title)
            (29, 28, 0, "resolved", "SEV1", "Total API outage during deployment"),
            (25, 24, 1, "resolved", "SEV1", "Auth service token signing key corrupted"),
            (20, 19, 2, "resolved", "SEV1", "Database primary node unresponsive"),
            (15, 14, 0, "resolved", "SEV1", "API Gateway SSL certificate expired"),
            # SEV1 open/investigating (causes outage status)
            (3, None, 2, "investigating", "SEV1", "Database replication lag critical"),
            (1, None, 1, "open", "SEV1", "Auth service returning 500 errors"),
            # SEV2 resolved
            (28, 27, 3, "resolved", "SEV2", "CDN cache invalidation failure"),
            (22, 21, 4, "resolved", "SEV2", "Notification queue backed up"),
            (18, 17, 5, "resolved", "SEV2", "Background worker crash loop"),
            (14, 13, 0, "resolved", "SEV2", "API rate limiter misconfigured"),
            (10, 9, 3, "resolved", "SEV2", "CDN edge node offline in EU-West"),
            (8, 7, 4, "resolved", "SEV2", "Email delivery delayed over 1 hour"),
            (6, 5, 5, "resolved", "SEV2", "Worker job failures exceeding 5%"),
            # SEV2 investigating
            (2, None, 4, "investigating", "SEV2", "Notification service high latency"),
            (1, None, 5, "investigating", "SEV2", "Background job queue growing"),
            # SEV2 open
            (1, None, 3, "open", "SEV2", "CDN cache hit ratio degraded"),
            # SEV3 resolved
            (27, 26, 0, "resolved", "SEV3", "API docs endpoint returning stale data"),
            (23, 22, 1, "resolved", "SEV3", "Auth login page slow to load"),
            (19, 18, 2, "resolved", "SEV3", "Database vacuum job running long"),
            (16, 15, 3, "resolved", "SEV3", "CDN logs ingestion delayed"),
            (12, 11, 4, "resolved", "SEV3", "Notification template rendering error"),
            (9, 8, 5, "resolved", "SEV3", "Worker dead-letter queue growing"),
            (5, 4, 0, "resolved", "SEV3", "API health check intermittent failures"),
            # SEV3 open
            (1, None, 1, "open", "SEV3", "Auth service response time elevated"),
            (1, None, 2, "open", "SEV3", "Database slow query log filling up"),
        ]

        assert len(incidents_data) == 25, f"Expected 25 incidents, got {len(incidents_data)}"

        for days_created, days_resolved, svc_idx, status, severity, title in incidents_data:
            created_at = now - timedelta(days=days_created)
            resolved_at = None
            if days_resolved is not None:
                resolved_at = now - timedelta(days=days_resolved)

            inc = models.Incident(
                title=title,
                description=f"Automatically seeded demo incident: {title}.",
                severity=severity,
                status=status,
                service_id=services[svc_idx].id,
                created_at=created_at,
                updated_at=resolved_at or created_at,
                resolved_at=resolved_at,
            )
            db.add(inc)
            db.flush()

            # Timeline entry: created
            db.add(models.TimelineEntry(
                incident_id=inc.id,
                author="seed",
                comment="Incident detected and created.",
                status_from=None,
                status_to="open",
                created_at=created_at,
            ))

            if status in ("investigating", "resolved"):
                investigating_at = created_at + timedelta(hours=1)
                db.add(models.TimelineEntry(
                    incident_id=inc.id,
                    author="seed",
                    comment="Team is investigating the root cause.",
                    status_from="open",
                    status_to="investigating",
                    created_at=investigating_at,
                ))

            if status == "resolved":
                db.add(models.TimelineEntry(
                    incident_id=inc.id,
                    author="seed",
                    comment="Root cause identified and resolved.",
                    status_from="investigating",
                    status_to="resolved",
                    created_at=resolved_at,
                ))

        db.commit()

        # ------------------------------------------------------------------
        # Recalculate service statuses
        # ------------------------------------------------------------------
        from app.status_engine import compute_service_status

        for svc in services:
            svc.computed_status = compute_service_status(svc.id, db)
        db.commit()

        # ------------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------------
        final_services = db.query(models.Service).count()
        final_incidents = db.query(models.Incident).count()
        print(
            f"Seed complete: {final_services} services and {final_incidents} incidents created.",
            flush=True,
        )
        return final_services, final_incidents

    finally:
        db.close()


if __name__ == "__main__":
    n_services, n_incidents = seed()
    if n_services != 6 or n_incidents != 25:
        print(
            f"ERROR: Expected 6 services and 25 incidents, got {n_services} and {n_incidents}.",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(0)
