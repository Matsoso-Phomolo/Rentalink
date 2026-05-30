import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import (
    get_district_admin_district_ids,
    require_roles,
)
from app.district_risk_logic import (
    calculate_district_collection_health,
    calculate_district_overdue_exposure,
    calculate_district_risk_distribution,
    calculate_high_risk_landlords,
    generate_district_risk_summary,
)
from app.models import User, UserRole

router = APIRouter(prefix="/district-risk", tags=["district-risk"])


def ensure_district_access(
    db: Session,
    user: User,
    district_id: uuid.UUID,
) -> None:
    if user.role == UserRole.national_admin:
        return

    allowed_district_ids = get_district_admin_district_ids(db, user)

    if district_id not in allowed_district_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this district.",
        )


@router.get("/{district_id}/summary")
def district_risk_summary(
    district_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.national_admin,
            UserRole.district_admin,
        )
    ),
):
    ensure_district_access(db, user, district_id)
    return generate_district_risk_summary(db, district_id)


@router.get("/{district_id}/distribution")
def district_risk_distribution(
    district_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.national_admin,
            UserRole.district_admin,
        )
    ),
):
    ensure_district_access(db, user, district_id)
    return calculate_district_risk_distribution(db, district_id)


@router.get("/{district_id}/high-risk-landlords")
def district_high_risk_landlords(
    district_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.national_admin,
            UserRole.district_admin,
        )
    ),
):
    ensure_district_access(db, user, district_id)
    return calculate_high_risk_landlords(db, district_id)


@router.get("/{district_id}/collection-health")
def district_collection_health(
    district_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.national_admin,
            UserRole.district_admin,
        )
    ),
):
    ensure_district_access(db, user, district_id)
    return calculate_district_collection_health(db, district_id)


@router.get("/{district_id}/overdue-exposure")
def district_overdue_exposure(
    district_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.national_admin,
            UserRole.district_admin,
        )
    ),
):
    ensure_district_access(db, user, district_id)
    return calculate_district_overdue_exposure(db, district_id)
