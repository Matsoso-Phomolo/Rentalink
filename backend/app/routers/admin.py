from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.admin_ai_risk import build_ai_risk_center
from app.database import get_db
from app.dependencies import require_roles
from app.models import User, UserRole
from app.reminders import run_reminders

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/run-reminders")
def run_platform_reminders(db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin))):
    return run_reminders(db)


@router.get("/ai-risk-center")
def ai_risk_center(db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin))):
    return build_ai_risk_center(db)
