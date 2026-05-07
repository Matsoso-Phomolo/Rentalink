from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("")
def list_payments_placeholder():
    return {"detail": "Direct payment records arrive in the next phase; use /payment-submissions for Phase 1."}
