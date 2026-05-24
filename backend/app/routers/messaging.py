import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Message, MessageThread, Tenant, User, UserRole
from app.ownership import assert_landlord_access, landlord_scope_filter
from app.schemas import MessageCreate, MessageRead, MessageThreadCreate, MessageThreadRead

router = APIRouter(prefix="/messages", tags=["messages"])


def actor_landlord_id(db: Session, user: User) -> uuid.UUID | None:
    if user.role == UserRole.landlord and user.landlord_profile:
        return user.landlord_profile.id
    if user.role == UserRole.caretaker and user.caretaker_profile:
        return user.caretaker_profile.landlord_id
    if user.role == UserRole.tenant:
        tenant = db.query(Tenant).filter(Tenant.user_id == user.id).first()
        return tenant.landlord_id if tenant else None
    return None


@router.post("/threads", response_model=MessageThreadRead)
def create_thread(payload: MessageThreadCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    thread = MessageThread(landlord_id=actor_landlord_id(db, user), **payload.model_dump())
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread


@router.get("/threads", response_model=list[MessageThreadRead])
def list_threads(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == UserRole.tenant:
        landlord_id = actor_landlord_id(db, user)
        return db.query(MessageThread).filter(MessageThread.landlord_id == landlord_id).order_by(MessageThread.created_at.desc()).all()
    return landlord_scope_filter(db, user, MessageThread).order_by(MessageThread.created_at.desc()).all()


@router.post("/threads/{thread_id}", response_model=MessageRead)
def send_message(thread_id: uuid.UUID, payload: MessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    thread = db.get(MessageThread, thread_id)
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message thread not found")
    if thread.landlord_id and user.role != UserRole.tenant:
        assert_landlord_access(db, user, thread.landlord_id)
    message = Message(thread_id=thread.id, sender_user_id=user.id, body=payload.body)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/threads/{thread_id}", response_model=list[MessageRead])
def list_messages(thread_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    thread = db.get(MessageThread, thread_id)
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message thread not found")
    if thread.landlord_id and user.role != UserRole.tenant:
        assert_landlord_access(db, user, thread.landlord_id)
    return db.query(Message).filter(Message.thread_id == thread.id).order_by(Message.created_at.asc()).all()
