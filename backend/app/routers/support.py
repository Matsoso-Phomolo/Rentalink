import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models import SupportTicket, SupportTicketMessage, User, UserRole
from app.ownership import scoped_query
from app.schemas import SupportTicketCreate, SupportTicketRead

router = APIRouter(prefix="/support", tags=["support"])


@router.get("", response_model=list[SupportTicketRead])
def list_support_tickets(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        scoped_query(db, user, SupportTicket)
        .order_by(SupportTicket.created_at.desc())
        .all()
    )


@router.post("", response_model=SupportTicketRead)
def create_support_ticket(
    payload: SupportTicketCreate,
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
    ticket = SupportTicket(
        **payload.model_dump(),
        sender_user_id=user.id,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


@router.get("/{ticket_id}", response_model=SupportTicketRead)
def get_support_ticket(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ticket = (
        scoped_query(db, user, SupportTicket)
        .filter(SupportTicket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support ticket not found",
        )

    return ticket
