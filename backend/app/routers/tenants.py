import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.audit import log_action
from app.database import get_db
from app.dependencies import get_actor_landlord_id, get_current_user, require_roles
from app.models import AuditAction, OnboardingChecklist, Tenant, User, UserRole
from app.ownership import assert_landlord_access, get_tenant_in_scope, landlord_scope_filter
from app.schemas import TenantCreate, TenantRead, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=TenantRead)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord, UserRole.caretaker))):
    landlord_id = get_actor_landlord_id(db, user)
    assert_landlord_access(db, user, landlord_id)
    tenant = Tenant(**payload.model_dump(), landlord_id=landlord_id)
    db.add(tenant)
    db.flush()
    db.add(OnboardingChecklist(tenant_id=tenant.id))
    log_action(db, AuditAction.create_tenant, user, landlord_id, "Tenant", tenant.id)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("", response_model=list[TenantRead])
def list_tenants(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == UserRole.tenant:
        return db.query(Tenant).filter(Tenant.user_id == user.id).all()
    return landlord_scope_filter(db, user, Tenant).order_by(Tenant.created_at.desc()).all()


@router.put("/{tenant_id}", response_model=TenantRead)
def update_tenant(tenant_id: uuid.UUID, payload: TenantUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tenant = get_tenant_in_scope(db, user, tenant_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(tenant, key, value)
    log_action(db, AuditAction.update_tenant, user, tenant.landlord_id, "Tenant", tenant.id)
    db.commit()
    db.refresh(tenant)
    return tenant
