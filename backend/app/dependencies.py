import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth import decode_token
from app.database import get_db
from app.models import Caretaker, Landlord, Tenant, User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    user = db.get(User, uuid.UUID(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return user


def require_roles(*roles: UserRole) -> Callable:
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return checker


def get_actor_landlord_id(db: Session, user: User) -> uuid.UUID | None:
    if user.role == UserRole.admin:
        return None
    if user.role == UserRole.landlord:
        profile = db.query(Landlord).filter(Landlord.user_id == user.id).first()
        return profile.id if profile else None
    if user.role == UserRole.caretaker:
        profile = db.query(Caretaker).filter(Caretaker.user_id == user.id).first()
        return profile.landlord_id if profile else None
    if user.role == UserRole.tenant:
        profile = db.query(Tenant).filter(Tenant.user_id == user.id).first()
        return profile.landlord_id if profile else None
    return None


def current_landlord_id(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> uuid.UUID:
    landlord_id = get_actor_landlord_id(db, current_user)
    if not landlord_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No landlord context available")
    return landlord_id
