from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.schemas.report import (
    BudgetStatusResponse,
    ExpenseByCategoryResponse,
    SummaryResponse,
)
from app.security.dependencies import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary", response_model=SummaryResponse)
def get_summary(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date",
        )

    income_query = select(func.sum(Transaction.amount)).where(
        Transaction.user_id == current_user.id,
        Transaction.type == TransactionType.INCOME,
    )

    if start_date is not None:
        income_query = income_query.where(
            Transaction.transaction_date >= start_date
        )

    if end_date is not None:
        income_query = income_query.where(
            Transaction.transaction_date <= end_date
        )

    total_income = db.scalar(income_query)

    total_income = (
        total_income
        if total_income is not None
        else Decimal("0")
    )

    expense_query = select(func.sum(Transaction.amount)).where(
        Transaction.user_id == current_user.id,
        Transaction.type == TransactionType.EXPENSE,
    )

    if start_date is not None:
        expense_query = expense_query.where(
            Transaction.transaction_date >= start_date
        )

    if end_date is not None:
        expense_query = expense_query.where(
            Transaction.transaction_date <= end_date
        )

    total_expense = db.scalar(expense_query)

    total_expense = (
        total_expense
        if total_expense is not None
        else Decimal("0")
    )

    net_balance = total_income - total_expense

    return SummaryResponse(
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
    )


@router.get(
    "/expenses-by-category",
    response_model=list[ExpenseByCategoryResponse],
)
def get_expenses_by_category(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date",
        )

    query = (
        select(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.sum(Transaction.amount).label("total"),
        )
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == current_user.id,
            Transaction.type == TransactionType.EXPENSE,
        )
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Transaction.amount).desc())
    )

    if start_date is not None:
        query = query.where(
            Transaction.transaction_date >= start_date
        )

    if end_date is not None:
        query = query.where(
            Transaction.transaction_date <= end_date
        )

    results = db.execute(query).all()

    return [
        ExpenseByCategoryResponse(
            category_id=row.category_id,
            category_name=row.category_name,
            total=row.total,
        )
        for row in results
    ]


@router.get(
    "/budget-status",
    response_model=list[BudgetStatusResponse],
)
def get_budget_status(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budgets = db.scalars(
        select(Budget).where(
            Budget.user_id == current_user.id,
            Budget.year == year,
            Budget.month == month,
        )
    ).all()

    results = []

    for budget in budgets:
        spent_amount = db.scalar(
            select(func.sum(Transaction.amount)).where(
                Transaction.user_id == current_user.id,
                Transaction.category_id == budget.category_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.transaction_date >= datetime(
                    year,
                    month,
                    1,
                ),
                Transaction.transaction_date < (
                    datetime(
                        year + (1 if month == 12 else 0),
                        1 if month == 12 else month + 1,
                        1,
                    )
                ),
            )
        )

        spent_amount = (
            spent_amount
            if spent_amount is not None
            else Decimal("0")
        )

        remaining_amount = budget.amount - spent_amount

        percentage_used = (
            (spent_amount / budget.amount) * Decimal("100")
        )

        results.append(
            BudgetStatusResponse(
                category_id=budget.category_id,
                category_name=budget.category.name,
                budget_amount=budget.amount,
                spent_amount=spent_amount,
                remaining_amount=remaining_amount,
                percentage_used=percentage_used,
            )
        )

    return results