from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.transaction import TransactionType

class TransactionCreate(BaseModel):
    category_id: int | None = None
    source_account_id: int | None = None
    destination_account_id: int | None = None
    type: TransactionType
    amount: Decimal = Field(..., gt=0, description="The amount of the transaction. Must be greater than 0.")
    description: str | None = None
    transaction_date: datetime

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    category_id: int | None
    source_account_id: int | None
    destination_account_id: int | None
    type: TransactionType
    amount: Decimal = Field(..., gt=0, description="The amount of the transaction. Must be greater than 0.")
    description: str | None
    transaction_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class TransactionUpdate(BaseModel):
    category_id: int | None = None
    source_account_id: int | None = None
    destination_account_id: int | None = None
    type: TransactionType | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    description: str | None = None
    transaction_date: datetime | None = None