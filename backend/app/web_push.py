import json

from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session

from app.config import settings
from app.models import PushSubscription


def get_vapid_private_key() -> str:
    key = getattr(settings, "vapid_private_key", None)

    if not key:
        raise RuntimeError("Missing VAPID_PRIVATE_KEY environment variable.")

    return key


def get_vapid_claims() -> dict:
    contact = getattr(settings, "vapid_contact_email", None)

    return {
        "sub": f"mailto:{contact or 'admin@rentalink.app'}",
    }


def send_web_push(
    subscription: PushSubscription,
    title: str,
    body: str,
    url: str = "/#/intelligence/alerts",
    severity: str = "watchlist",
) -> bool:
    payload = {
        "title": title,
        "body": body,
        "url": url,
        "severity": severity,
        "icon": "/icons/icon-192.png",
        "badge": "/icons/icon-192.png",
    }

    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth,
                },
            },
            data=json.dumps(payload),
            vapid_private_key=get_vapid_private_key(),
            vapid_claims=get_vapid_claims(),
        )

        return True

    except WebPushException:
        return False


def send_push_to_user(
    db: Session,
    user_id,
    title: str,
    body: str,
    url: str = "/#/intelligence/alerts",
    severity: str = "watchlist",
) -> int:
    subscriptions = (
        db.query(PushSubscription)
        .filter(
            PushSubscription.user_id == user_id,
            PushSubscription.is_active.is_(True),
        )
        .all()
    )

    sent_count = 0

    for subscription in subscriptions:
        sent = send_web_push(
            subscription=subscription,
            title=title,
            body=body,
            url=url,
            severity=severity,
        )

        if sent:
            sent_count += 1
        else:
            subscription.is_active = False

    db.commit()

    return sent_count
