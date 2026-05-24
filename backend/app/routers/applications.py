import uuid
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import require_roles
from app.models import ApplicationStatus, TenantApplication, User, UserRole
from app.routers.listings import assign_application_room, listing_in_scope
from app.ownership import landlord_scope_filter
from app.schemas import ApplicationAssignRoom, ApplicationDecision, ApplicationFormLink, TenantApplicationRead

router = APIRouter(prefix="/applications", tags=["applications"])


def application_in_scope(db: Session, user: User, application_id: uuid.UUID) -> TenantApplication:
    application = db.get(TenantApplication, application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    listing_in_scope(db, user, application.listing_id)
    return application


@router.get("", response_model=list[TenantApplicationRead])
def list_applications(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord, UserRole.caretaker))):
    query = landlord_scope_filter(db, user, TenantApplication)
    return query.order_by(TenantApplication.created_at.desc()).all()


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


@router.post("/{application_id}/send-form-link", response_model=ApplicationFormLink)
def send_application_form_link(application_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord, UserRole.caretaker))):
    application = application_in_scope(db, user, application_id)
    token = secrets.token_urlsafe(32)
    while db.query(TenantApplication).filter(TenantApplication.application_token == token).first():
        token = secrets.token_urlsafe(32)
    application.application_token = token
    application.form_sent_at = datetime.now(timezone.utc)
    application.token_expires_at = application.form_sent_at + timedelta(days=settings.application_token_expire_days)
    application.status = ApplicationStatus.form_sent
    db.commit()
    db.refresh(application)
    base_url = settings.public_base_url.rstrip("/")
    return ApplicationFormLink(application_id=application.id, application_url=f"{base_url}/#/apply/{token}", token_expires_at=application.token_expires_at)


@router.post("/{application_id}/assign-room")
def assign_room(application_id: uuid.UUID, payload: ApplicationAssignRoom, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord, UserRole.caretaker))):
    return assign_application_room(application_id, payload, db, user)
