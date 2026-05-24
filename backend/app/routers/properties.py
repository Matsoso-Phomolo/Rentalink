import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_actor_landlord_id, get_current_user, require_roles
from app.models import Property, Room, User, UserRole
from app.ownership import assert_landlord_access, landlord_scope_filter
from app.schemas import PropertyCreate, PropertyRead, PropertyUpdate

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
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    assert_landlord_access(db, user, prop.landlord_id)
    return prop


@router.put("/{property_id}", response_model=PropertyRead)
def update_property(property_id: uuid.UUID, payload: PropertyUpdate, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord))):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    assert_landlord_access(db, user, prop.landlord_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(prop, key, value)
    db.commit()
    db.refresh(prop)
    return prop


@router.delete("/{property_id}")
def delete_property(property_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord))):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    assert_landlord_access(db, user, prop.landlord_id)
    has_rooms = db.query(Room).filter(Room.property_id == prop.id).first()
    if has_rooms:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Remove or transfer rooms before deleting this property.")
    db.delete(prop)
    db.commit()
    return {"detail": "Property deleted"}
