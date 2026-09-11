from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.budget import Budget
from app.models.category import Category, CategoryType
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"],
)

# Create a new budget
@router.post(
    "/",
    response_model=BudgetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate that the category exists and is active
    category = db.scalar(
        select(Category).where(
            Category.id == budget_data.category_id,
            Category.is_active.is_(True),
        )
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    if category.type != CategoryType.EXPENSE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budgets can only be created for expense categories",
        )

    existing_budget = db.scalar(
        select(Budget).where(
            Budget.user_id == current_user.id,
            Budget.category_id == budget_data.category_id,
            Budget.year == budget_data.year,
            Budget.month == budget_data.month,
        )
    )

    if existing_budget is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A budget already exists for this category and period",
        )

    budget = Budget(
        user_id=current_user.id,
        category_id=budget_data.category_id,
        amount=budget_data.amount,
        year=budget_data.year,
        month=budget_data.month,
    )

    db.add(budget)
    db.commit()
    db.refresh(budget)

    return budget

# Get budgets with optional filters
@router.get(
    "/",
    response_model=list[BudgetResponse],
)
def get_budgets(
    year: int | None = Query(default=None),
    month: int | None = Query(default=None, ge=1, le=12),
    category_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Budget).where(
        Budget.user_id == current_user.id
    )

    if year is not None:
        query = query.where(
            Budget.year == year
        )

    if month is not None:
        query = query.where(
            Budget.month == month
        )

    if category_id is not None:
        query = query.where(
            Budget.category_id == category_id
        )

    budgets = db.scalars(query).all()

    return budgets

# Get a specific budget by ID
@router.get(
    "/{budget_id}",
    response_model=BudgetResponse,
)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = db.scalar(
        select(Budget).where(
            Budget.id == budget_id,
            Budget.user_id == current_user.id,
        )
    )

    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )

    return budget

# Update a specific budget by ID
@router.patch(
    "/{budget_id}",
    response_model=BudgetResponse,
)
def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = db.scalar(
        select(Budget).where(
            Budget.id == budget_id,
            Budget.user_id == current_user.id,
        )
    )

    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )

    new_category_id = (
    budget_data.category_id
    if "category_id" in budget_data.model_fields_set
    else budget.category_id
    )

    new_amount = (
        budget_data.amount
        if budget_data.amount is not None
        else budget.amount
    )

    new_year = (
        budget_data.year
        if budget_data.year is not None
        else budget.year
    )

    new_month = (
        budget_data.month
        if budget_data.month is not None
        else budget.month
    )

    if new_category_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget must have a category",
        )

    category = db.scalar(
        select(Category).where(
            Category.id == new_category_id,
            Category.is_active.is_(True),
        )
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    if category.type != CategoryType.EXPENSE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budgets can only be created for expense categories",
        )

    existing_budget = db.scalar(
        select(Budget).where(
            Budget.user_id == current_user.id,
            Budget.category_id == new_category_id,
            Budget.year == new_year,
            Budget.month == new_month,
            Budget.id != budget.id,
        )
    )

    if existing_budget is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A budget already exists for this category and period",
        )

    budget.category_id = new_category_id
    budget.amount = new_amount
    budget.year = new_year
    budget.month = new_month

    db.commit()
    db.refresh(budget)

    return budget

# Delete a specific budget by ID
@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = db.scalar(
        select(Budget).where(
            Budget.id == budget_id,
            Budget.user_id == current_user.id,
        )
    )

    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )

    db.delete(budget)
    db.commit()