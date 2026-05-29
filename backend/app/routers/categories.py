import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_actor_landlord_id, require_roles
from app.models import PropertyCategory, User, UserRole
from app.ownership import assert_landlord_access, scoped_query
from app.schemas import PropertyCategoryCreate, PropertyCategoryRead

router = APIRouter(prefix="/categories", tags=["property categories"])


@router.post("", response_model=PropertyCategoryRead)
def create_category(
    payload: PropertyCategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.landlord,
            UserRole.caretaker,
        )
    ),
):
    landlord_id = get_actor_landlord_id(db, user)

    if not landlord_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No landlord scope available",
        )

    assert_landlord_access(db, user, landlord_id)

    category = PropertyCategory(
        landlord_id=landlord_id,
        **payload.model_dump(),
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get("", response_model=list[PropertyCategoryRead])
def list_categories(
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.admin,
            UserRole.district_admin,
            UserRole.landlord,
            UserRole.caretaker,
        )
    ),
):
    return (
        scoped_query(db, user, PropertyCategory)
        .order_by(PropertyCategory.name.asc())
        .all()
    )


@router.put("/{category_id}", response_model=PropertyCategoryRead)
def update_category(
    category_id: uuid.UUID,
    payload: PropertyCategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.landlord,
            UserRole.caretaker,
        )
    ),
):
    category = (
        scoped_query(db, user, PropertyCategory)
        .filter(PropertyCategory.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    category.name = payload.name
    category.description = payload.description

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(
            UserRole.landlord,
            UserRole.caretaker,
        )
    ),
):
    category = (
        scoped_query(db, user, PropertyCategory)
        .filter(PropertyCategory.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    db.delete(category)
    db.commit()

    return {"detail": "Category deleted"}
