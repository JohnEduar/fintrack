from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.account import AccountType


class AccountCreate(BaseModel):
    name: str
    type: AccountType


class AccountUpdate(BaseModel):
    name: str | None = None
    type: AccountType | None = None


class AccountResponse(BaseModel):
    id: int
    name: str
    type: AccountType
    balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }