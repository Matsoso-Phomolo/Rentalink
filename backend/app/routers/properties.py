import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_actor_landlord_id, get_current_user, require_roles
from app.models import Property, User, UserRole
from app.ownership import assert_landlord_access, landlord_scope_filter
from app.schemas import PropertyCreate, PropertyRead

router = APIRouter(prefix="/properties", tags=["properties"])


@router.post("", response_model=PropertyRead)
def create_property(payload: PropertyCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord))):
    landlord_id = payload.landlord_id or get_actor_landlord_id(db, user)
    assert_landlord_access(db, user, landlord_id)
    prop = Property(**payload.model_dump(exclude={"landlord_id"}), landlord_id=landlord_id)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.get("", response_model=list[PropertyRead])
def list_properties(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return landlord_scope_filter(db, user, Property).order_by(Property.created_at.desc()).all()


@router.get("/{property_id}", response_model=PropertyRead)
def get_property(property_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    prop = db.get(Property, property_id)
    assert_landlord_access(db, user, prop.landlord_id)
    return prop
