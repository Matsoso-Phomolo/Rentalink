from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import Caretaker, User, UserRole
from app.schemas import CaretakerCreate

router = APIRouter(prefix="/caretakers", tags=["caretakers"])


@router.post("")
def create_caretaker(payload: CaretakerCreate, db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin, UserRole.landlord))):
    caretaker = Caretaker(**payload.model_dump())
    db.add(caretaker)
    db.commit()
    db.refresh(caretaker)
    return caretaker
