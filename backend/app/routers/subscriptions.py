import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import LandlordSubscription, SubscriptionPlan, User, UserRole
from app.schemas import LandlordSubscriptionCreate, LandlordSubscriptionRead, SubscriptionPlanCreate, SubscriptionPlanRead

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("/plans", response_model=SubscriptionPlanRead)
def create_plan(payload: SubscriptionPlanCreate, db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin))):
    plan = SubscriptionPlan(**payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/plans", response_model=list[SubscriptionPlanRead])
def list_plans(db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin, UserRole.landlord, UserRole.caretaker))):
    return db.query(SubscriptionPlan).order_by(SubscriptionPlan.monthly_price.asc()).all()


@router.put("/plans/{plan_id}", response_model=SubscriptionPlanRead)
def update_plan(plan_id: uuid.UUID, payload: SubscriptionPlanCreate, db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin))):
    plan = db.get(SubscriptionPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription plan not found")
    for key, value in payload.model_dump().items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/plans/{plan_id}")
def delete_plan(plan_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin))):
    plan = db.get(SubscriptionPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription plan not found")
    plan.is_active = False
    db.commit()
    return {"detail": "Subscription plan disabled"}


@router.post("", response_model=LandlordSubscriptionRead)
def assign_subscription(payload: LandlordSubscriptionCreate, db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin))):
    subscription = LandlordSubscription(**payload.model_dump())
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


@router.get("", response_model=list[LandlordSubscriptionRead])
def list_subscriptions(db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.admin))):
    return db.query(LandlordSubscription).order_by(LandlordSubscription.created_at.desc()).all()
