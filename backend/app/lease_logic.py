from datetime import timedelta

from sqlalchemy.orm import Session

from app.models import LeaseAgreement, LeaseStatus, Occupancy, Property, Room, Tenant


def next_lease_number(db: Session) -> str:
    sequence = db.query(LeaseAgreement).count() + 1
    while True:
        number = f"LL-LEASE-{sequence:06d}"
        if not db.query(LeaseAgreement).filter(LeaseAgreement.lease_number == number).first():
            return number
        sequence += 1


def generate_lease_for_occupancy(db: Session, occupancy: Occupancy, terms: str | None = None) -> LeaseAgreement:
    existing = db.query(LeaseAgreement).filter(LeaseAgreement.occupancy_id == occupancy.id).first()
    if existing:
        return existing
    room = db.get(Room, occupancy.room_id)
    tenant = db.get(Tenant, occupancy.tenant_id)
    prop = db.get(Property, room.property_id) if room else None
    default_terms = terms or "Tenant agrees to pay rent on time, keep the room in good condition, follow landlord rules, and report maintenance issues promptly."
    lease = LeaseAgreement(
        landlord_id=occupancy.landlord_id,
        tenant_id=occupancy.tenant_id,
        property_id=prop.id,
        room_id=occupancy.room_id,
        occupancy_id=occupancy.id,
        lease_number=next_lease_number(db),
        start_date=occupancy.move_in_date,
        end_date=tenant.lease_end_date if tenant else occupancy.move_in_date + timedelta(days=365),
        monthly_rent=occupancy.monthly_rent,
        deposit_amount=occupancy.deposit_amount,
        terms=default_terms,
        status=LeaseStatus.draft,
    )
    db.add(lease)
    db.flush()
    lease.pdf_url = f"/leases/{lease.id}/pdf"
    return lease
