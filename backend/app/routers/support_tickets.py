import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import AliasChoices, BaseModel, Field

from app.audit import log_action
from app.database import get_db
from app.dependencies import get_current_user
from app.models import AuditAction, SupportTicket, User
from app.ownership import get_tenant_in_scope, landlord_scope_filter

router = APIRouter(prefix="/support-tickets", tags=["support tickets"])


class SupportTicketCreate(BaseModel):
    tenant_id: uuid.UUID
    title: str = Field(validation_alias=AliasChoices("title", "subject"))
    category: str
    priority: str | None = None
    description: str


@router.post("")
def create_ticket(payload: SupportTicketCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tenant = get_tenant_in_scope(db, user, payload.tenant_id)
    ticket = SupportTicket(landlord_id=tenant.landlord_id, **payload.model_dump())
    db.add(ticket)
    log_action(db, AuditAction.create_support_ticket, user, tenant.landlord_id, "SupportTicket")
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("")
def list_tickets(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return landlord_scope_filter(db, user, SupportTicket).order_by(SupportTicket.created_at.desc()).all()
