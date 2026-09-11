from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    category_id: int
    amount: Decimal = Field(..., gt=0)
    year: int
    month: int = Field(..., ge=1, le=12)


class BudgetUpdate(BaseModel):
    category_id: int | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    year: int | None = None
    month: int | None = Field(default=None, ge=1, le=12)


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount: Decimal
    year: int
    month: int

    model_config = {
        "from_attributes": True
    }