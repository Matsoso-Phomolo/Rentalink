from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import Landlord, User, UserRole
from app.schemas import LandlordCreate, LandlordRead

router = APIRouter(prefix="/landlords", tags=["landlords"])


@router.post("", response_model=LandlordRead)
def create_landlord(payload: LandlordCreate, db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin))):
    landlord = Landlord(**payload.model_dump())
    db.add(landlord)
    db.commit()
    db.refresh(landlord)
    return landlord


@router.get("", response_model=list[LandlordRead])
def list_landlords(db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin))):
    return db.query(Landlord).order_by(Landlord.created_at.desc()).all()
