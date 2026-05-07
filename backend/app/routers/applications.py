import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import ApplicationStatus, TenantApplication, User, UserRole
from app.routers.listings import assign_application_room, listing_in_scope
from app.schemas import ApplicationAssignRoom, ApplicationDecision, TenantApplicationRead

router = APIRouter(prefix="/applications", tags=["applications"])


def application_in_scope(db: Session, user: User, application_id: uuid.UUID) -> TenantApplication:
    application = db.get(TenantApplication, application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    listing_in_scope(db, user, application.listing_id)
    return application


@router.put("/{application_id}/approve", response_model=TenantApplicationRead)
def approve_application(application_id: uuid.UUID, payload: ApplicationDecision, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord, UserRole.caretaker))):
    application = application_in_scope(db, user, application_id)
    application.status = ApplicationStatus.approved
    application.landlord_note = payload.landlord_note
    db.commit()
    db.refresh(application)
    return application


@router.put("/{application_id}/reject", response_model=TenantApplicationRead)
def reject_application(application_id: uuid.UUID, payload: ApplicationDecision, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord, UserRole.caretaker))):
    application = application_in_scope(db, user, application_id)
    application.status = ApplicationStatus.rejected
    application.landlord_note = payload.landlord_note
    db.commit()
    db.refresh(application)
    return application


@router.post("/{application_id}/request-info", response_model=TenantApplicationRead)
def request_application_info(application_id: uuid.UUID, payload: ApplicationDecision, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord, UserRole.caretaker))):
    application = application_in_scope(db, user, application_id)
    application.status = ApplicationStatus.info_requested
    application.landlord_note = payload.landlord_note
    db.commit()
    db.refresh(application)
    return application


@router.post("/{application_id}/assign-room")
def assign_room(application_id: uuid.UUID, payload: ApplicationAssignRoom, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord, UserRole.caretaker))):
    return assign_application_room(application_id, payload, db, user)
