from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import (
    Landlord,
    LandlordSubscription,
    Notification,
    NotificationPreference,
    Occupancy,
    ReminderLog,
    RentDue,
    RentDueStatus,
    Room,
    SubscriptionPlan,
    SubscriptionStatus,
    Tenant,
    User,
)


@dataclass
class ReminderRunResult:
    tenant_rent_reminders_generated: int = 0
    subscription_reminders_generated: int = 0
    skipped_duplicates: int = 0
    failures: list[str] | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "tenant_rent_reminders_generated": self.tenant_rent_reminders_generated,
            "subscription_reminders_generated": self.subscription_reminders_generated,
            "skipped_duplicates": self.skipped_duplicates,
            "failures": self.failures or [],
        }


def _money(value: Decimal | float | int | None) -> str:
    return f"{float(value or 0):,.2f}".rstrip("0").rstrip(".")


def _channels_for(db: Session, user: User, phone: str | None, email: str | None) -> list[str]:
    preference = db.query(NotificationPreference).filter(NotificationPreference.user_id == user.id).first()
    if not preference:
        channels = ["in_app"]
        if email:
            channels.append("email")
        if phone:
            channels.extend(["whatsapp", "sms"])
        return channels

    channels: list[str] = []
    if preference.in_app_enabled:
        channels.append("in_app")
    if preference.email_enabled and email:
        channels.append("email")
    if preference.whatsapp_enabled and phone:
        channels.append("whatsapp")
    if preference.sms_enabled and phone:
        channels.append("sms")
    return channels or ["in_app"]


def _create_reminder(
    db: Session,
    *,
    user_id: UUID,
    landlord_id: UUID | None,
    tenant_id: UUID | None,
    property_id: UUID | None,
    room_id: UUID | None,
    channel: str,
    reminder_type: str,
    target_id: UUID,
    scheduled_for: date,
    message: str,
) -> str:
    existing = db.query(ReminderLog).filter(
        ReminderLog.reminder_type == reminder_type,
        ReminderLog.target_id == str(target_id),
        ReminderLog.channel == channel,
        ReminderLog.scheduled_for == scheduled_for,
    ).first()
    if existing:
        return "skipped"

    now = datetime.now(timezone.utc)
    status = "sent" if channel == "in_app" else "scaffolded"
    db.add(ReminderLog(
        user_id=user_id,
        landlord_id=landlord_id,
        tenant_id=tenant_id,
        property_id=property_id,
        room_id=room_id,
        channel=channel,
        reminder_type=reminder_type,
        target_id=str(target_id),
        scheduled_for=scheduled_for,
        sent_at=now,
        status=status,
        message=message,
    ))
    if channel == "in_app":
        title = "Rent reminder" if reminder_type.startswith("rent") else "Subscription reminder"
        db.add(Notification(user_id=user_id, title=title, body=message, category=reminder_type))
    return "created"


def _rent_reminder_kind(due: RentDue, today: date) -> str | None:
    if not due.due_date:
        return None
    days_until_due = (due.due_date - today).days
    if days_until_due in {7, 3, 1, 0}:
        return "rent_due"
    if days_until_due < 0 and abs(days_until_due) % 3 == 0:
        return "rent_overdue"
    return None


def _subscription_reminder_kind(subscription: LandlordSubscription, today: date) -> str | None:
    if not subscription.renewal_date:
        return None
    days_until_renewal = (subscription.renewal_date - today).days
    if days_until_renewal in {7, 3, 0}:
        return "subscription_due"
    if days_until_renewal < 0 and abs(days_until_renewal) % 5 == 0:
        return "subscription_overdue"
    return None


def run_reminders(db: Session, today: date | None = None) -> dict[str, object]:
    today = today or date.today()
    result = ReminderRunResult(failures=[])

    rent_dues = db.query(RentDue).filter(RentDue.status.in_([RentDueStatus.unpaid, RentDueStatus.partial, RentDueStatus.overdue])).all()
    for due in rent_dues:
        try:
            reminder_type = _rent_reminder_kind(due, today)
            if not reminder_type:
                continue
            tenant = db.get(Tenant, due.tenant_id)
            occupancy = db.get(Occupancy, due.occupancy_id)
            user = db.get(User, tenant.user_id) if tenant and tenant.user_id else None
            room = db.get(Room, occupancy.room_id) if occupancy else None
            property_item = room.property if room else None
            if not tenant or not user or not room or not property_item:
                continue
            balance = max(Decimal("0"), Decimal(str(due.amount_due or 0)) - Decimal(str(due.amount_paid or 0)))
            if reminder_type == "rent_overdue":
                message = f"Your Rentalink rent payment for Room {room.room_number} at {property_item.name} is overdue. Outstanding balance: M{_money(balance)}. Please make payment as soon as possible."
            else:
                message = f"Reminder: Your Rentalink rent payment for Room {room.room_number} at {property_item.name} is due on {due.due_date}. Outstanding amount: M{_money(balance)}."
            for channel in _channels_for(db, user, tenant.phone, tenant.email or user.email):
                outcome = _create_reminder(
                    db,
                    user_id=user.id,
                    landlord_id=due.landlord_id,
                    tenant_id=due.tenant_id,
                    property_id=property_item.id,
                    room_id=room.id,
                    channel=channel,
                    reminder_type=reminder_type,
                    target_id=due.id,
                    scheduled_for=today,
                    message=message,
                )
                if outcome == "created":
                    result.tenant_rent_reminders_generated += 1
                else:
                    result.skipped_duplicates += 1
        except Exception as exc:  # pragma: no cover - defensive scheduler boundary
            result.failures.append(f"rent_due:{due.id}:{exc}")

    subscriptions = db.query(LandlordSubscription).filter(LandlordSubscription.status == SubscriptionStatus.active).all()
    for subscription in subscriptions:
        try:
            reminder_type = _subscription_reminder_kind(subscription, today)
            if not reminder_type:
                continue
            landlord = db.get(Landlord, subscription.landlord_id)
            user = db.get(User, landlord.user_id) if landlord else None
            plan = db.get(SubscriptionPlan, subscription.plan_id)
            if not landlord or not user or not plan:
                continue
            if reminder_type == "subscription_overdue":
                message = f"Your Rentalink {plan.name} subscription expired on {subscription.renewal_date}. Please renew to continue accessing landlord operations."
            else:
                message = f"Your Rentalink {plan.name} subscription expires on {subscription.renewal_date}. Please renew to continue accessing landlord operations."
            for channel in _channels_for(db, user, landlord.contact_phone or user.phone, landlord.email or user.email):
                outcome = _create_reminder(
                    db,
                    user_id=user.id,
                    landlord_id=landlord.id,
                    tenant_id=None,
                    property_id=None,
                    room_id=None,
                    channel=channel,
                    reminder_type=reminder_type,
                    target_id=subscription.id,
                    scheduled_for=today,
                    message=message,
                )
                if outcome == "created":
                    result.subscription_reminders_generated += 1
                else:
                    result.skipped_duplicates += 1
        except Exception as exc:  # pragma: no cover - defensive scheduler boundary
            result.failures.append(f"subscription:{subscription.id}:{exc}")

    db.commit()
    return result.as_dict()
