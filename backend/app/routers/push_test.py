from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.web_push import send_push_to_user

router = APIRouter(prefix="/push-test", tags=["push-test"])


@router.post("/me")
def send_test_push_to_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sent_count = send_push_to_user(
        db=db,
        user_id=user.id,
        title="Rentalink test alert",
        body="Your Rentalink push notifications are working.",
        url="/#/intelligence/alerts",
        severity="stable",
    )

    return {
        "detail": "Test push attempted",
        "sent_count": sent_count,
    }
