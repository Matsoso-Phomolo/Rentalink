from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import PushSubscription, User

router = APIRouter(prefix="/push-subscriptions", tags=["push-subscriptions"])


@router.post("")
async def save_push_subscription(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    endpoint = payload.get("endpoint")
    keys = payload.get("keys") or {}

    if not endpoint:
        return {"detail": "Missing endpoint"}

    subscription = (
        db.query(PushSubscription)
        .filter(PushSubscription.endpoint == endpoint)
        .first()
    )

    if not subscription:
        subscription = PushSubscription(
            user_id=user.id,
            endpoint=endpoint,
            p256dh=keys.get("p256dh", ""),
            auth=keys.get("auth", ""),
            user_agent=request.headers.get("user-agent"),
            is_active=True,
        )
        db.add(subscription)
    else:
        subscription.user_id = user.id
        subscription.p256dh = keys.get("p256dh", subscription.p256dh)
        subscription.auth = keys.get("auth", subscription.auth)
        subscription.user_agent = request.headers.get("user-agent")
        subscription.is_active = True

    db.commit()

    return {"detail": "Push subscription saved"}
