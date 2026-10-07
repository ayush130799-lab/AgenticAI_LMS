"""bookmark uniqueness, content indexes, admin audit log

Revision ID: 0003_integrity_and_audit
Revises: 0002_module_assessments
Create Date: 2026-09-29

* bookmarks: collapse any duplicate (user_id, lesson_id) rows, then add a UNIQUE constraint so the
  toggle endpoint cannot be corrupted by concurrent requests.
* notes / highlights / questions: indexes for the lookups the API actually performs.
* admin_audit_log: one row per state-changing /api/admin request.

Idempotent for the same reason as 0002: 0001 builds tables from the current ORM models, so a database
created fresh already has these objects while an older one needs them added.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0003_integrity_and_audit"
down_revision: Union[str, None] = "0002_module_assessments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DELETE FROM bookmarks a USING bookmarks b "
        "WHERE a.user_id = b.user_id AND a.lesson_id = b.lesson_id AND a.ctid < b.ctid"
    )
    op.execute("ALTER TABLE bookmarks DROP CONSTRAINT IF EXISTS uq_bookmark_user_lesson")
    op.execute("ALTER TABLE bookmarks ADD CONSTRAINT uq_bookmark_user_lesson UNIQUE (user_id, lesson_id)")

    op.execute("CREATE INDEX IF NOT EXISTS ix_notes_user_lesson ON notes (user_id, lesson_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_highlights_user_lesson ON highlights (user_id, lesson_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_questions_assessment_id ON questions (assessment_id)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_audit_log (
            id UUID PRIMARY KEY,
            user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            actor_email VARCHAR(255) NOT NULL,
            method VARCHAR(10) NOT NULL,
            path VARCHAR(500) NOT NULL,
            entity VARCHAR(50) NOT NULL,
            entity_id VARCHAR(64),
            status_code INTEGER NOT NULL,
            client_ip VARCHAR(64),
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_admin_audit_log_created_at ON admin_audit_log (created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_admin_audit_log_user_id ON admin_audit_log (user_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS admin_audit_log")
    op.execute("DROP INDEX IF EXISTS ix_questions_assessment_id")
    op.execute("DROP INDEX IF EXISTS ix_highlights_user_lesson")
    op.execute("DROP INDEX IF EXISTS ix_notes_user_lesson")
    op.execute("ALTER TABLE bookmarks DROP CONSTRAINT IF EXISTS uq_bookmark_user_lesson")
