from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import ApplicationStatus, ListingStatus, Occupancy, OccupancyStatus, PaymentSubmission, PaymentSubmissionStatus, Property, RentDue, RentDueStatus, Room, RoomListing, RoomStatus, TenantApplication, User, UserRole
from app.ownership import landlord_scope_filter
from app.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.admin, UserRole.landlord, UserRole.caretaker))):
    props = landlord_scope_filter(db, user, Property)
    rooms = landlord_scope_filter(db, user, Room)
    return DashboardSummary(
        properties=props.count(),
        rooms=rooms.count(),
        vacant_rooms=rooms.filter(Room.status == RoomStatus.vacant).count(),
        occupied_rooms=rooms.filter(Room.status == RoomStatus.occupied).count(),
        active_tenants=landlord_scope_filter(db, user, Occupancy).filter(Occupancy.status == OccupancyStatus.active).count(),
        unpaid_rent_dues=landlord_scope_filter(db, user, RentDue).filter(RentDue.status.in_([RentDueStatus.unpaid, RentDueStatus.partial])).count(),
        pending_payment_submissions=landlord_scope_filter(db, user, PaymentSubmission).filter(PaymentSubmission.status == PaymentSubmissionStatus.pending).count(),
        published_listings=landlord_scope_filter(db, user, RoomListing).filter(RoomListing.status == ListingStatus.published).count(),
        pending_applications=db.query(TenantApplication).join(RoomListing, TenantApplication.listing_id == RoomListing.id).filter(
            RoomListing.id.in_([l.id for l in landlord_scope_filter(db, user, RoomListing).all()]),
            TenantApplication.status.in_([ApplicationStatus.inquiry_pending, ApplicationStatus.form_sent, ApplicationStatus.submitted, ApplicationStatus.pending, ApplicationStatus.under_review, ApplicationStatus.info_requested]),
        ).count(),
    )
