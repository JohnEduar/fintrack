from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category


class Budget(Base):
    __tablename__ = "budgets"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "category_id",
            "year",
            "month",
            name="uq_budget_user_category_period",
        ),
        CheckConstraint(
            "amount > 0",
            name="check_budget_amount_positive",
        ),
        CheckConstraint(
            "month BETWEEN 1 AND 12",
            name="check_budget_month_valid",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
    )

    year: Mapped[int] = mapped_column(
        nullable=False,
    )

    month: Mapped[int] = mapped_column(
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship()

    category: Mapped["Category"] = relationship()