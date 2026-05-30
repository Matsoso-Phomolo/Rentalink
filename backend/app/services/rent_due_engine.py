from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    Occupancy,
    OccupancyStatus,
    RentDue,
    RentDueStatus,
)


def first_day_of_month(value: date | None = None) -> date:
    today = value or date.today()
    return date(today.year, today.month, 1)


def calculate_rent_due_status(due: RentDue) -> RentDueStatus:
    amount_due = Decimal(due.amount_due or 0)
    amount_paid = Decimal(due.amount_paid or 0)

    if amount_paid >= amount_due:
        return RentDueStatus.paid

    if amount_paid > 0:
        return RentDueStatus.partial

    return RentDueStatus.unpaid


def generate_rent_due_for_occupancy(
    db: Session,
    occupancy: Occupancy,
    due_month: date | None = None,
) -> RentDue:
    target_month = first_day_of_month(due_month)

    existing_due = (
        db.query(RentDue)
        .filter(
            RentDue.occupancy_id == occupancy.id,
            RentDue.due_month == target_month,
        )
        .first()
    )

    if existing_due:
        existing_due.status = calculate_rent_due_status(existing_due)
        return existing_due

    due = RentDue(
        landlord_id=occupancy.landlord_id,
        tenant_id=occupancy.tenant_id,
        occupancy_id=occupancy.id,
        due_month=target_month,
        amount_due=occupancy.monthly_rent,
        amount_paid=Decimal("0"),
        status=RentDueStatus.unpaid,
    )

    db.add(due)
    db.flush()

    return due


def generate_monthly_rent_dues(
    db: Session,
    target_month: date | None = None,
) -> list[RentDue]:
    due_month = first_day_of_month(target_month)

    active_occupancies = (
        db.query(Occupancy)
        .filter(Occupancy.status == OccupancyStatus.active)
        .all()
    )

    dues: list[RentDue] = []

    for occupancy in active_occupancies:
        due = generate_rent_due_for_occupancy(
            db,
            occupancy,
            due_month,
        )
        dues.append(due)

    return dues
