import json
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditAction, AuditLog, User


def log_action(
    db: Session,
    action: AuditAction,
    actor: User | None = None,
    landlord_id: uuid.UUID | None = None,
    entity_type: str | None = None,
    entity_id: uuid.UUID | str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    db.add(
        AuditLog(
            action=action,
            actor_user_id=actor.id if actor else None,
            landlord_id=landlord_id,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else None,
            metadata_json=json.dumps(metadata or {}),
        )
    )
