import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ListingStatus, RoomListing, TenantApplication, ViewingRequest
from app.schemas import ListingRead, TenantApplicationCreate, TenantApplicationRead, ViewingRequestCreate, ViewingRequestRead

router = APIRouter(prefix="/public/listings", tags=["public listings"])


def get_public_listing(db: Session, listing_id: uuid.UUID) -> RoomListing:
    listing = db.query(RoomListing).filter(
        RoomListing.id == listing_id,
        RoomListing.status == ListingStatus.published,
        RoomListing.is_public.is_(True),
    ).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Public listing not found")
    return listing


@router.get("", response_model=list[ListingRead])
def public_listings(location_area: str | None = None, room_type: str | None = None, max_rent: float | None = None, db: Session = Depends(get_db)):
    query = db.query(RoomListing).filter(RoomListing.status == ListingStatus.published, RoomListing.is_public.is_(True))
    if location_area:
        query = query.filter(RoomListing.location_area.ilike(f"%{location_area}%"))
    if room_type:
        query = query.filter(RoomListing.room_type == room_type)
    if max_rent:
        query = query.filter(RoomListing.rent_price <= max_rent)
    return query.order_by(RoomListing.created_at.desc()).all()


@router.get("/{listing_id}", response_model=ListingRead)
def public_listing_detail(listing_id: uuid.UUID, db: Session = Depends(get_db)):
    return get_public_listing(db, listing_id)


@router.post("/{listing_id}/viewing-requests", response_model=ViewingRequestRead)
def create_viewing_request(listing_id: uuid.UUID, payload: ViewingRequestCreate, db: Session = Depends(get_db)):
    listing = get_public_listing(db, listing_id)
    request = ViewingRequest(listing_id=listing.id, **payload.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.post("/{listing_id}/applications", response_model=TenantApplicationRead)
def create_application(listing_id: uuid.UUID, payload: TenantApplicationCreate, db: Session = Depends(get_db)):
    listing = get_public_listing(db, listing_id)
    application = TenantApplication(listing_id=listing.id, **payload.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application
