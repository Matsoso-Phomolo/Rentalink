import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import User, UserRole
from app.ownership import get_tenant_in_scope
from app.tenant_financial_logic import (
    calculate_tenant_balance,
    calculate_tenant_financial_summary,
    calculate_tenant_overdue_risk,
    calculate_tenant_payment_history,
    calculate_tenant_payment_score,
)

router = APIRouter(prefix="/tenant-financial", tags=["tenant-financial"])


@router.get("/{tenant_id}/summary")
def tenant_financial_summary(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.national_admin,
            UserRole.district_admin,
            UserRole.landlord,
            UserRole.caretaker,
            UserRole.tenant,
        )
    ),
):
    tenant = get_tenant_in_scope(db, user, tenant_id)
    return calculate_tenant_financial_summary(db, tenant.id)


@router.get("/{tenant_id}/balance")
def tenant_balance(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.national_admin,
            UserRole.district_admin,
            UserRole.landlord,
            UserRole.caretaker,
            UserRole.tenant,
        )
    ),
):
    tenant = get_tenant_in_scope(db, user, tenant_id)
    return calculate_tenant_balance(db, tenant.id)


@router.get("/{tenant_id}/risk")
def tenant_risk(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.national_admin,
            UserRole.district_admin,
            UserRole.landlord,
            UserRole.caretaker,
        )
    ),
):
    tenant = get_tenant_in_scope(db, user, tenant_id)
    return calculate_tenant_overdue_risk(db, tenant.id)


@router.get("/{tenant_id}/payment-score")
def tenant_payment_score(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.national_admin,
            UserRole.district_admin,
            UserRole.landlord,
            UserRole.caretaker,
        )
    ),
):
    tenant = get_tenant_in_scope(db, user, tenant_id)
    return calculate_tenant_payment_score(db, tenant.id)


@router.get("/{tenant_id}/history")
def tenant_payment_history(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.national_admin,
            UserRole.district_admin,
            UserRole.landlord,
            UserRole.caretaker,
            UserRole.tenant,
        )
    ),
):
    tenant = get_tenant_in_scope(db, user, tenant_id)
    history = calculate_tenant_payment_history(db, tenant.id)

    return {
        "total_receipts": history["total_receipts"],
        "total_paid": history["total_paid"],
        "receipts": history["receipts"],
    }
