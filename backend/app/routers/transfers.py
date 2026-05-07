import uuid
from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.audit import log_action
from app.database import get_db
from app.dependencies import require_roles
from app.models import AuditAction, Occupancy, OccupancyStatus, Room, RoomListing, RoomStatus, ListingStatus, User, UserRole
from app.ownership import get_room_in_scope, get_tenant_in_scope
from app.rent_logic import generate_initial_rent_due

router = APIRouter(prefix="/transfers", tags=["transfers"])


class TransferCreate(BaseModel):
    tenant_id: uuid.UUID
    old_occupancy_id: uuid.UUID
    new_room_id: uuid.UUID
    transfer_date: date
    monthly_rent: float
    deposit_amount: float = 0
    billing_start_month: date


@router.post("")
def transfer_room(payload: TransferCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord, UserRole.caretaker))):
    tenant = get_tenant_in_scope(db, user, payload.tenant_id)
    new_room = get_room_in_scope(db, user, payload.new_room_id)
    old = db.get(Occupancy, payload.old_occupancy_id)
    old.status = OccupancyStatus.transferred
    old.move_out_date = payload.transfer_date
    previous_room = db.get(Room, old.room_id)
    previous_room.status = RoomStatus.vacant
    new_room.status = RoomStatus.occupied
    db.query(RoomListing).filter(RoomListing.room_id == new_room.id, RoomListing.status == ListingStatus.published).update(
        {"status": ListingStatus.rented, "is_public": False}
    )
    occupancy = Occupancy(
        landlord_id=tenant.landlord_id,
        tenant_id=tenant.id,
        room_id=new_room.id,
        move_in_date=payload.transfer_date,
        monthly_rent=payload.monthly_rent,
        deposit_amount=payload.deposit_amount,
        billing_start_month=payload.billing_start_month,
    )
    db.add(occupancy)
    db.flush()
    generate_initial_rent_due(db, occupancy)
    log_action(db, AuditAction.room_transfer, user, tenant.landlord_id, "Occupancy", occupancy.id)
    db.commit()
    return occupancy
