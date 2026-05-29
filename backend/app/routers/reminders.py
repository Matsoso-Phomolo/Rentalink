from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models import NotificationPreference, ReminderLog, User, UserRole
from app.ownership import scoped_query

router = APIRouter(prefix="/reminders", tags=["reminders"])


def _serialize_log(log: ReminderLog) -> dict[str, object]:
    return {
        "id": str(log.id),
        "user_id": str(log.user_id),
        "landlord_id": str(log.landlord_id) if log.landlord_id else None,
        "tenant_id": str(log.tenant_id) if log.tenant_id else None,
        "property_id": str(log.property_id) if log.property_id else None,
        "room_id": str(log.room_id) if log.room_id else None,
        "channel": log.channel,
        "reminder_type": log.reminder_type,
        "target_id": log.target_id,
        "scheduled_for": log.scheduled_for,
        "sent_at": log.sent_at,
        "status": log.status,
        "message": log.message,
        "created_at": log.created_at,
    }


@router.get("/mine")
def my_reminder_logs(
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.admin,
            UserRole.landlord,
            UserRole.caretaker,
            UserRole.tenant,
        )
    ),
):
    if user.role == UserRole.tenant:
        query = db.query(ReminderLog).filter(ReminderLog.user_id == user.id)
    else:
        query = scoped_query(db, user, ReminderLog)

    return [
        _serialize_log(log)
        for log in query.order_by(ReminderLog.created_at.desc()).limit(50).all()
    ]


@router.get("/preferences/me")
def get_preferences(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    preference = (
        db.query(NotificationPreference)
        .filter(NotificationPreference.user_id == user.id)
        .first()
    )

    if not preference:
        return {
            "in_app_enabled": True,
            "email_enabled": True,
            "whatsapp_enabled": True,
            "sms_enabled": True,
        }

    return {
        "in_app_enabled": preference.in_app_enabled,
        "email_enabled": preference.email_enabled,
        "whatsapp_enabled": preference.whatsapp_enabled,
        "sms_enabled": preference.sms_enabled,
    }


@router.put("/preferences/me")
def update_preferences(
    payload: dict[str, bool],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    preference = (
        db.query(NotificationPreference)
        .filter(NotificationPreference.user_id == user.id)
        .first()
    )

    if not preference:
        preference = NotificationPreference(user_id=user.id)
        db.add(preference)

    for key in (
        "in_app_enabled",
        "email_enabled",
        "whatsapp_enabled",
        "sms_enabled",
    ):
        if key in payload:
            setattr(preference, key, bool(payload[key]))

    db.commit()
    db.refresh(preference)

    return {
        "in_app_enabled": preference.in_app_enabled,
        "email_enabled": preference.email_enabled,
        "whatsapp_enabled": preference.whatsapp_enabled,
        "sms_enabled": preference.sms_enabled,
    }
