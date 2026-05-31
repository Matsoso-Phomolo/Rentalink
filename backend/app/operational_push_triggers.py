from sqlalchemy.orm import Session

from app.intelligence_ws import intelligence_manager
from app.models import RentDue, User, UserRole
from app.push_sender import send_push_to_user


async def broadcast_operational_event(
    event_type: str,
    severity: str,
    title: str,
    description: str,
    payload: dict | None = None,
) -> None:
    await intelligence_manager.broadcast(
        {
            "type": event_type,
            "severity": severity,
            "title": title,
            "description": description,
            "payload": payload or {},
        }
    )


async def trigger_overdue_rent_alert(
    db: Session,
    due: RentDue,
) -> None:
    severity = "watchlist"

    if due.days_overdue >= 30:
        severity = "critical"
    elif due.days_overdue >= 14:
        severity = "risky"
    elif due.days_overdue >= 7:
        severity = "watchlist"

    title = "Rent overdue alert"
    description = (
        f"Rent due {due.payment_reference or due.id} is "
        f"{due.days_overdue} day(s) overdue."
    )

    payload = {
        "rent_due_id": str(due.id),
        "tenant_id": str(due.tenant_id),
        "landlord_id": str(due.landlord_id),
        "days_overdue": due.days_overdue,
        "payment_reference": due.payment_reference,
        "amount_due": str(due.amount_due),
        "amount_paid": str(due.amount_paid),
    }

    await broadcast_operational_event(
        event_type="overdue_rent_alert",
        severity=severity,
        title=title,
        description=description,
        payload=payload,
    )

    users = (
        db.query(User)
        .filter(
            User.role.in_(
                [
                    UserRole.national_admin,
                    UserRole.district_admin,
                    UserRole.landlord,
                ]
            ),
            User.is_active.is_(True),
        )
        .all()
    )

    for user in users:
        send_push_to_user(
            db=db,
            user_id=user.id,
            title=title,
            body=description,
            severity=severity,
            payload=payload,
        )
