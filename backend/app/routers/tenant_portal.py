from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Occupancy, RentDue, Tenant, User, UserRole

router = APIRouter(prefix="/tenant-portal", tags=["tenant portal"])


@router.get("/me")
def tenant_portal_me(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != UserRole.tenant:
        return {"detail": "Tenant portal is for tenant accounts"}
    tenant = db.query(Tenant).filter(Tenant.user_id == user.id).first()
    if not tenant:
        return {"tenant": None, "occupancies": [], "rent_dues": []}
    return {
        "tenant": tenant,
        "occupancies": db.query(Occupancy).filter(Occupancy.tenant_id == tenant.id).all(),
        "rent_dues": db.query(RentDue).filter(RentDue.tenant_id == tenant.id).all(),
    }
