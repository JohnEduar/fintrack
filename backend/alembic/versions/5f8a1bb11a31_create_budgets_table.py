"""create budgets table

Revision ID: 5f8a1bb11a31
Revises: d2d9f42a40af
Create Date: 2026-09-04 19:19:29.194817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f8a1bb11a31'
down_revision: Union[str, Sequence[str], None] = 'd2d9f42a40af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "amount > 0",
            name="check_budget_amount_positive",
        ),
        sa.CheckConstraint(
            "month BETWEEN 1 AND 12",
            name="check_budget_month_valid",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "category_id",
            "year",
            "month",
            name="uq_budget_user_category_period",
        ),
    )


def downgrade() -> None:
    op.drop_table("budgets")
