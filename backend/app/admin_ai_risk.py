from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    Complaint,
    ComplaintStatus,
    Landlord,
    LandlordRequest,
    LandlordRequestStatus,
    ListingPhoto,
    ListingVerificationStatus,
    PaymentSubmission,
    PaymentSubmissionStatus,
    PaymentTransaction,
    PaymentTransactionStatus,
    ReminderLog,
    RoomListing,
    SubscriptionStatus,
    SupportTicket,
    TicketStatus,
    LandlordSubscription,
)

URGENT_KEYWORDS = ("violence", "theft", "harassment", "damage", "electricity", "water", "lock", "security")


def _risk_level(score: int) -> str:
    if score >= 80:
        return "urgent"
    if score >= 55:
        return "high"
    if score >= 30:
        return "medium"
    return "low"


def build_ai_risk_center(db: Session) -> dict[str, object]:
    landlord_cards = []
    for landlord in db.query(Landlord).order_by(Landlord.created_at.desc()).limit(25).all():
        rejected_requests = db.query(LandlordRequest).filter(
            LandlordRequest.email == landlord.email,
            LandlordRequest.status == LandlordRequestStatus.rejected,
        ).count()
        rejected_listings = db.query(RoomListing).filter(
            RoomListing.landlord_id == landlord.id,
            RoomListing.verification_status == ListingVerificationStatus.rejected,
        ).count()
        incomplete_contact = 0 if landlord.contact_phone and landlord.email and landlord.address else 15
        inactive_penalty = 25 if not landlord.is_active else 0
        score = min(100, incomplete_contact + inactive_penalty + rejected_requests * 20 + rejected_listings * 10)
        landlord_cards.append({
            "landlord_id": str(landlord.id),
            "name": landlord.business_name,
            "system_landlord_number": landlord.system_landlord_number,
            "score": score,
            "level": _risk_level(score),
            "signals": {
                "rejected_requests": rejected_requests,
                "rejected_listings": rejected_listings,
                "incomplete_contact": bool(incomplete_contact),
                "inactive": not landlord.is_active,
            },
        })

    listing_cards = []
    for listing in db.query(RoomListing).order_by(RoomListing.created_at.desc()).limit(30).all():
        photo_count = db.query(ListingPhoto).filter(ListingPhoto.listing_id == listing.id).count()
        rent = float(listing.rent_price or 0)
        score = 0
        signals: list[str] = []
        if listing.verification_status != ListingVerificationStatus.verified:
            score += 30
            signals.append("listing not verified")
        if rent and (rent < 200 or rent > 3000):
            score += 25
            signals.append("rent outside expected Roma/NUL range")
        if photo_count == 0:
            score += 20
            signals.append("missing room photos")
        if not listing.contact_phone:
            score += 10
            signals.append("missing contact phone")
        listing_cards.append({
            "listing_id": str(listing.id),
            "title": listing.title,
            "score": min(100, score),
            "level": _risk_level(min(100, score)),
            "signals": signals,
        })

    complaint_cards = []
    for complaint in db.query(Complaint).filter(Complaint.status != ComplaintStatus.resolved).order_by(Complaint.created_at.desc()).limit(20).all():
        text = f"{complaint.title} {complaint.description}".lower()
        hits = [word for word in URGENT_KEYWORDS if word in text]
        score = min(100, 20 + len(hits) * 20)
        complaint_cards.append({
            "complaint_id": str(complaint.id),
            "title": complaint.title,
            "level": _risk_level(score),
            "score": score,
            "urgent_keywords": hits,
        })

    suspicious_payments = []
    duplicate_refs = db.query(
        PaymentSubmission.transaction_reference,
        PaymentSubmission.landlord_id,
        func.count(PaymentSubmission.id).label("count"),
    ).group_by(PaymentSubmission.transaction_reference, PaymentSubmission.landlord_id).having(func.count(PaymentSubmission.id) > 1).all()
    for reference, landlord_id, count in duplicate_refs:
        suspicious_payments.append({
            "type": "duplicate_reference",
            "landlord_id": str(landlord_id),
            "reference": reference,
            "count": count,
            "level": "high",
        })
    failed_transactions = db.query(PaymentTransaction).filter(PaymentTransaction.status.in_([PaymentTransactionStatus.failed, PaymentTransactionStatus.timeout])).order_by(PaymentTransaction.created_at.desc()).limit(10).all()
    for transaction in failed_transactions:
        suspicious_payments.append({
            "type": "failed_mobile_money",
            "landlord_id": str(transaction.landlord_id),
            "reference": transaction.provider_reference or transaction.checkout_request_id,
            "count": 1,
            "level": "medium",
        })

    daily_summary = {
        "new_landlord_requests": db.query(LandlordRequest).filter(LandlordRequest.status == LandlordRequestStatus.pending).count(),
        "pending_listing_verification": db.query(RoomListing).filter(RoomListing.verification_status == ListingVerificationStatus.pending_verification).count(),
        "overdue_subscriptions": db.query(LandlordSubscription).filter(LandlordSubscription.status == SubscriptionStatus.past_due).count(),
        "unresolved_complaints": db.query(Complaint).filter(Complaint.status != ComplaintStatus.resolved).count(),
        "open_maintenance_tickets": db.query(SupportTicket).filter(SupportTicket.status.in_([TicketStatus.open, TicketStatus.assigned, TicketStatus.in_progress])).count(),
        "recent_failed_payments": db.query(PaymentTransaction).filter(PaymentTransaction.status.in_([PaymentTransactionStatus.failed, PaymentTransactionStatus.timeout])).count(),
        "reminders_scaffolded": db.query(ReminderLog).filter(ReminderLog.status == "scaffolded").count(),
        "rejected_payment_proofs": db.query(PaymentSubmission).filter(PaymentSubmission.status == PaymentSubmissionStatus.rejected).count(),
    }

    return {
        "decision_support_only": True,
        "landlord_risk_cards": landlord_cards,
        "listing_fraud_cards": listing_cards,
        "complaint_severity_cards": complaint_cards,
        "suspicious_payment_alerts": suspicious_payments,
        "daily_admin_summary": daily_summary,
    }
