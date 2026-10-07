"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-23

This bootstrap migration creates the pgvector extension and then builds every
table straight from the SQLAlchemy ORM metadata (`app.models.Base`), rather
than hand-authored `op.create_table(...)` calls. With ~25 interrelated tables
this keeps the migration guaranteed to match the models exactly. Any schema
change going forward should use `alembic revision --autogenerate` against a
running database, which will produce normal incremental migrations on top of
this one.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Import here (not at module load time) so alembic's --autogenerate
    # tooling can still import this file even before app deps are installed.
    from app.models import Base

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    from app.models import Base

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
    op.execute("DROP EXTENSION IF EXISTS vector")
