from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import AuditLog, User, UserRole

router = APIRouter(prefix="/audit-logs", tags=["audit logs"])


@router.get("")
def list_audit_logs(db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin))):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all()
