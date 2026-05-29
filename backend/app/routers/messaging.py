import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Message, MessageThread, Tenant, User, UserRole
from app.ownership import get_tenant_in_scope, scoped_query
from app.schemas import (
    MessageCreate,
    MessageRead,
    MessageThreadCreate,
    MessageThreadRead,
)

router = APIRouter(prefix="/messages", tags=["messages"])


def actor_landlord_id(
    db: Session,
    user: User,
) -> uuid.UUID | None:
    if user.role == UserRole.landlord and user.landlord_profile:
        return user.landlord_profile.id

    if user.role == UserRole.caretaker and user.caretaker_profile:
        return user.caretaker_profile.landlord_id

    if user.role == UserRole.tenant:
        tenant = db.query(Tenant).filter(Tenant.user_id == user.id).first()
        return tenant.landlord_id if tenant else None

    return None


def thread_in_scope(
    db: Session,
    user: User,
    thread_id: uuid.UUID,
) -> MessageThread:
    thread = db.get(MessageThread, thread_id)

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message thread not found",
        )

    if user.role == UserRole.tenant:
        tenant = db.query(Tenant).filter(Tenant.user_id == user.id).first()

        if not tenant or thread.landlord_id != tenant.landlord_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Message thread is outside your account",
            )

        return thread

    scoped_thread = (
        scoped_query(db, user, MessageThread)
        .filter(MessageThread.id == thread.id)
        .first()
    )

    if not scoped_thread:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Message thread is outside your scope",
        )

    return thread


@router.post("/threads", response_model=MessageThreadRead)
def create_thread(
    payload: MessageThreadCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    landlord_id = actor_landlord_id(db, user)

    thread = MessageThread(
        landlord_id=landlord_id,
        **payload.model_dump(),
    )

    db.add(thread)
    db.commit()
    db.refresh(thread)

    return thread


@router.get("/threads", response_model=list[MessageThreadRead])
def list_threads(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role == UserRole.tenant:
        tenant = db.query(Tenant).filter(Tenant.user_id == user.id).first()

        if not tenant:
            return []

        return (
            db.query(MessageThread)
            .filter(MessageThread.landlord_id == tenant.landlord_id)
            .order_by(MessageThread.created_at.desc())
            .all()
        )

    return (
        scoped_query(db, user, MessageThread)
        .order_by(MessageThread.created_at.desc())
        .all()
    )


@router.post("/threads/{thread_id}", response_model=MessageRead)
def send_message(
    thread_id: uuid.UUID,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    thread = thread_in_scope(db, user, thread_id)

    message = Message(
        thread_id=thread.id,
        sender_user_id=user.id,
        body=payload.body,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.get("/threads/{thread_id}", response_model=list[MessageRead])
def list_messages(
    thread_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    thread = thread_in_scope(db, user, thread_id)

    return (
        db.query(Message)
        .filter(Message.thread_id == thread.id)
        .order_by(Message.created_at.asc())
        .all()
    )
