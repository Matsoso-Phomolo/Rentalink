import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import User, UserRole
from app.ownership import get_tenant_in_scope
from app.risk_logic import (
    calculate_collection_probability,
    generate_landlord_recommendation,
    generate_tenant_risk_summary,
)

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/tenant/{tenant_id}")
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
    return generate_tenant_risk_summary(db, tenant.id)


@router.get("/tenant/{tenant_id}/summary")
def tenant_risk_summary(
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
    return generate_tenant_risk_summary(db, tenant.id)


@router.get("/tenant/{tenant_id}/recommendation")
def tenant_risk_recommendation(
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
    summary = generate_tenant_risk_summary(db, tenant.id)

    return {
        "tenant_id": tenant.id,
        "tenant_name": summary["tenant_name"],
        "risk_level": summary["risk_level"],
        "default_risk": summary["default_risk"],
        "recommendation": summary["recommendation"],
    }


@router.get("/tenant/{tenant_id}/collection-probability")
def tenant_collection_probability(
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
    summary = generate_tenant_risk_summary(db, tenant.id)

    return {
        "tenant_id": tenant.id,
        "tenant_name": summary["tenant_name"],
        "collection_probability": summary["collection_probability"],
        "payment_score": summary["payment_score"],
        "risk_level": summary["risk_level"],
    }
