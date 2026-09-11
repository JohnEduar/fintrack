from decimal import Decimal

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal

class ExpenseByCategoryResponse(BaseModel):
    category_id: int
    category_name: str
    total: Decimal

class BudgetStatusResponse(BaseModel):
    category_id: int
    category_name: str
    budget_amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    percentage_used: Decimal