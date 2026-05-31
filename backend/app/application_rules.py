from fastapi import HTTPException, status
from typing import Protocol

from app.models import AllowedTenantType, RoomListing, TenantType


class ApplicationTenantDetails(Protocol):
    tenant_type: TenantType
    student_number: str | None
    institution: str | None
    occupation: str | None


def validate_application_against_listing(
    listing: RoomListing,
    payload: ApplicationTenantDetails,
) -> None:
    if (
        listing.allowed_tenant_type == AllowedTenantType.student
        and payload.tenant_type != TenantType.student
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This room is available for student tenants only.",
        )

    if (
        listing.allowed_tenant_type == AllowedTenantType.non_student
        and payload.tenant_type != TenantType.non_student
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This room is available for non-student tenants only.",
        )

    if payload.tenant_type == TenantType.student:
        if not payload.institution or not payload.student_number:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Student applications require institution and student number.",
            )

    if payload.tenant_type == TenantType.non_student and not payload.occupation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Non-student applications require occupation.",
        )


def validate_application_record_against_listing(
    listing: RoomListing,
    tenant_type: TenantType,
    institution: str | None,
    student_number: str | None,
    occupation: str | None,
) -> None:
    class Payload:
        tenant_type: TenantType
        institution: str | None
        student_number: str | None
        occupation: str | None

    payload = Payload()
    payload.tenant_type = tenant_type
    payload.institution = institution
    payload.student_number = student_number
    payload.occupation = occupation

    validate_application_against_listing(listing, payload)
