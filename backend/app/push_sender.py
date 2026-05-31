import json

from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session

from app.config import settings
from app.models import PushSubscription


def get_vapid_claims() -> dict:
    return {
        "sub": getattr(
            settings,
            "VAPID_SUBJECT",
            "mailto:phomolomatsoso@gmail.com",
        )
    }


def get_vapid_private_key() -> str | None:
    return getattr(settings, "VAPID_PRIVATE_KEY", None)


def send_push_to_subscription(
    subscription: PushSubscription,
    payload: dict,
) -> bool:
    private_key = get_vapid_private_key()

    if not private_key:
        return False

    subscription_info = {
        "endpoint": subscription.endpoint,
        "keys": {
            "p256dh": subscription.p256dh,
            "auth": subscription.auth,
        },
    }

    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=private_key,
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
    severity: str = "watchlist",
    payload: dict | None = None,
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
        sent = send_push_to_subscription(
            subscription,
            {
                "title": title,
                "body": body,
                "severity": severity,
                "payload": payload or {},
            },
        )

        if sent:
            sent_count += 1

    return sent_count
