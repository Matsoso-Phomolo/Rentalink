import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_actor_landlord_id
from app.models import Property, Room, Tenant, User, UserRole


def landlord_scope_filter(db: Session, user: User, model):
    if user.role == UserRole.admin:
        return db.query(model)
    landlord_id = get_actor_landlord_id(db, user)
    if not landlord_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No landlord scope")
    return db.query(model).filter(model.landlord_id == landlord_id)


def assert_landlord_access(db: Session, user: User, landlord_id: uuid.UUID) -> None:
    if user.role == UserRole.admin:
        return
    actor_landlord_id = get_actor_landlord_id(db, user)
    if actor_landlord_id != landlord_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resource is outside your landlord scope")


def get_property_in_scope(db: Session, user: User, property_id: uuid.UUID) -> Property:
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    assert_landlord_access(db, user, prop.landlord_id)
    return prop


def get_room_in_scope(db: Session, user: User, room_id: uuid.UUID) -> Room:
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    assert_landlord_access(db, user, room.landlord_id)
    return room


def get_tenant_in_scope(db: Session, user: User, tenant_id: uuid.UUID) -> Tenant:
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    if user.role == UserRole.tenant and tenant.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant can only access own data")
    assert_landlord_access(db, user, tenant.landlord_id)
    return tenant
