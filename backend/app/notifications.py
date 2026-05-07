import uuid

from sqlalchemy.orm import Session

from app.models import Notification


def create_notification(db: Session, user_id: uuid.UUID, title: str, body: str, category: str) -> Notification:
    notification = Notification(user_id=user_id, title=title, body=body, category=category)
    db.add(notification)
    return notification
