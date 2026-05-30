from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Occupancy, OccupancyStatus, RentDue, RentDueStatus, Tenant
from app.risk_logic import generate_tenant_risk_summary


def money(value) -> Decimal:
    return Decimal(value or 0)


def get_landlord_active_tenants(
    db: Session,
    landlord_id,
) -> list[Tenant]:
    tenant_ids = (
        db.query(Occupancy.tenant_id)
        .filter(
            Occupancy.landlord_id == landlord_id,
            Occupancy.status == OccupancyStatus.active,
        )
        .distinct()
        .all()
    )

    ids = [row[0] for row in tenant_ids]

    if not ids:
        return []

    return db.query(Tenant).filter(Tenant.id.in_(ids)).all()


def calculate_landlord_risk_distribution(
    db: Session,
    landlord_id,
) -> dict:
    tenants = get_landlord_active_tenants(db, landlord_id)

    distribution = {
        "stable": 0,
        "watchlist": 0,
        "risky": 0,
        "critical": 0,
    }

    for tenant in tenants:
        summary = generate_tenant_risk_summary(db, tenant.id)
        risk_level = summary["risk_level"]

        if risk_level in distribution:
            distribution[risk_level] += 1

    return distribution


def calculate_portfolio_collection_health(
    db: Session,
    landlord_id,
) -> dict:
    dues = (
        db.query(RentDue)
        .filter(RentDue.landlord_id == landlord_id)
        .all()
    )

    total_due = sum((money(due.amount_due) for due in dues), Decimal("0"))
    total_paid = sum((money(due.amount_paid) for due in dues), Decimal("0"))

    collection_health = 100.0

    if total_due > 0:
        collection_health = round(float((total_paid / total_due) * 100), 2)

    return {
        "total_due": total_due,
        "total_paid": total_paid,
        "portfolio_collection_health": collection_health,
    }


def calculate_high_risk_tenants(
    db: Session,
    landlord_id,
) -> list[dict]:
    tenants = get_landlord_active_tenants(db, landlord_id)
    high_risk: list[dict] = []

    for tenant in tenants:
        summary = generate_tenant_risk_summary(db, tenant.id)

        if summary["risk_level"] in {"risky", "critical"}:
            high_risk.append(summary)

    return high_risk


def calculate_overdue_clusters(
    db: Session,
    landlord_id,
) -> dict:
    overdue_dues = (
        db.query(RentDue)
        .filter(
            RentDue.landlord_id == landlord_id,
            RentDue.status == RentDueStatus.overdue,
        )
        .all()
    )

    clusters = {
        "1_6_days": 0,
        "7_13_days": 0,
        "14_29_days": 0,
        "30_plus_days": 0,
    }

    for due in overdue_dues:
        days = due.days_overdue or 0

        if days >= 30:
            clusters["30_plus_days"] += 1
        elif days >= 14:
            clusters["14_29_days"] += 1
        elif days >= 7:
            clusters["7_13_days"] += 1
        else:
            clusters["1_6_days"] += 1

    return clusters


def generate_landlord_portfolio_risk_summary(
    db: Session,
    landlord_id,
) -> dict:
    distribution = calculate_landlord_risk_distribution(db, landlord_id)
    collection_health = calculate_portfolio_collection_health(db, landlord_id)
    high_risk_tenants = calculate_high_risk_tenants(db, landlord_id)
    overdue_clusters = calculate_overdue_clusters(db, landlord_id)

    total_tenants = sum(distribution.values())

    portfolio_risk_level = "stable"

    if distribution["critical"] > 0:
        portfolio_risk_level = "critical"
    elif distribution["risky"] > 0:
        portfolio_risk_level = "risky"
    elif distribution["watchlist"] > 0:
        portfolio_risk_level = "watchlist"

    return {
        "total_tenants": total_tenants,
        "portfolio_risk_level": portfolio_risk_level,
        "risk_distribution": distribution,
        "collection_health": collection_health,
        "high_risk_tenants": high_risk_tenants,
        "overdue_clusters": overdue_clusters,
    }
