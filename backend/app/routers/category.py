from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryResponse
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get("/", response_model=list[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    categories = db.scalars(
        select(Category).where(
            Category.is_active.is_(True)
        )
    ).all()

    return categories