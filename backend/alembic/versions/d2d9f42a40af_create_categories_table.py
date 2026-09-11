"""create categories table

Revision ID: d2d9f42a40af
Revises: a054c0e39f57
Create Date: 2026-09-04 15:47:48.706495

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision: str = 'd2d9f42a40af'
down_revision: Union[str, Sequence[str], None] = 'a054c0e39f57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    now = datetime.now(timezone.utc)
    op.bulk_insert(
        sa.table(
            "categories",
            sa.column("name", sa.String()),
            sa.column("type", sa.String()),
            sa.column("is_active", sa.Boolean()),
            sa.column("created_at", sa.DateTime()),
            sa.column("updated_at", sa.DateTime()),
        ),
        [
            {"name": "Salario", "type": "INCOME", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Otros ingresos", "type": "INCOME", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Inversiones", "type": "INCOME", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Alimentación", "type": "EXPENSE", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Transporte", "type": "EXPENSE", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Vivienda", "type": "EXPENSE", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Servicios", "type": "EXPENSE", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Salud", "type": "EXPENSE", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Educación", "type": "EXPENSE", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Entretenimiento", "type": "EXPENSE", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Compras", "type": "EXPENSE", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Suscripciones", "type": "EXPENSE", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Deudas", "type": "EXPENSE", "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Otros gastos", "type": "EXPENSE", "is_active": True, "created_at": now, "updated_at": now},
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM categories")
