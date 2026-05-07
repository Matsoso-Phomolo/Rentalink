from datetime import date

from sqlalchemy.orm import Session

from app.models import Occupancy, RentDue, RentDueStatus


def first_day(value: date) -> date:
    return date(value.year, value.month, 1)


def generate_initial_rent_due(db: Session, occupancy: Occupancy) -> RentDue:
    due = RentDue(
        landlord_id=occupancy.landlord_id,
        tenant_id=occupancy.tenant_id,
        occupancy_id=occupancy.id,
        due_month=first_day(occupancy.billing_start_month),
        amount_due=occupancy.monthly_rent,
        amount_paid=0,
        status=RentDueStatus.unpaid,
    )
    db.add(due)
    return due


def refresh_due_status(due: RentDue) -> None:
    if due.amount_paid <= 0:
        due.status = RentDueStatus.unpaid
    elif due.amount_paid < due.amount_due:
        due.status = RentDueStatus.partial
    else:
        due.status = RentDueStatus.paid
