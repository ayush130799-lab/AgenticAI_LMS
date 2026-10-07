"""module assessments and progression gating

Revision ID: 0002_module_assessments
Revises: 0001_initial
Create Date: 2026-09-25

Purely additive: new nullable/defaulted columns on assessments, questions and
assessment_attempts, a widened question_type CHECK (adds 'quiz'), and the new
assessment_answers table. No existing data is modified or removed.

Every statement is idempotent because 0001 builds tables from the *current*
ORM models, so a database created fresh already has these objects, while a
database created before this feature needs them added.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002_module_assessments"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE assessments ADD COLUMN IF NOT EXISTS level VARCHAR(20)")
    op.execute("ALTER TABLE assessments ADD COLUMN IF NOT EXISTS required_coding_questions INTEGER NOT NULL DEFAULT 1")
    op.execute("ALTER TABLE assessments ADD COLUMN IF NOT EXISTS is_published BOOLEAN NOT NULL DEFAULT false")
    op.execute("ALTER TABLE assessments DROP CONSTRAINT IF EXISTS ck_assessment_level")
    op.execute(
        "ALTER TABLE assessments ADD CONSTRAINT ck_assessment_level "
        "CHECK (level is null or level in ('beginner','intermediate','advanced'))"
    )

    op.execute("ALTER TABLE questions ADD COLUMN IF NOT EXISTS quiz_format VARCHAR(20)")
    op.execute("ALTER TABLE questions ADD COLUMN IF NOT EXISTS coding_config JSONB")
    op.execute("ALTER TABLE questions DROP CONSTRAINT IF EXISTS ck_question_type")
    op.execute(
        "ALTER TABLE questions ADD CONSTRAINT ck_question_type "
        "CHECK (question_type in ('mcq','multi_select','short_answer','coding','scenario','quiz'))"
    )

    for column, ddl in (
        ("attempt_number", "INTEGER"),
        ("percentage", "DOUBLE PRECISION"),
        ("passed", "BOOLEAN"),
        ("mcq_score", "DOUBLE PRECISION"),
        ("quiz_score", "DOUBLE PRECISION"),
        ("coding_score", "DOUBLE PRECISION"),
        ("coding_results", "JSONB"),
        ("result_detail", "JSONB"),
    ):
        op.execute(f"ALTER TABLE assessment_attempts ADD COLUMN IF NOT EXISTS {column} {ddl}")
    op.execute("ALTER TABLE assessment_attempts DROP CONSTRAINT IF EXISTS uq_attempt_number")
    op.execute(
        "ALTER TABLE assessment_attempts ADD CONSTRAINT uq_attempt_number "
        "UNIQUE (user_id, assessment_id, attempt_number)"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS assessment_answers (
            id UUID PRIMARY KEY,
            attempt_id UUID NOT NULL REFERENCES assessment_attempts(id) ON DELETE CASCADE,
            question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
            answer JSONB,
            is_correct BOOLEAN NOT NULL DEFAULT false,
            points_awarded DOUBLE PRECISION NOT NULL DEFAULT 0,
            coding_result JSONB,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now(),
            CONSTRAINT uq_answer_attempt_question UNIQUE (attempt_id, question_id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_assessment_answers_attempt_id ON assessment_answers (attempt_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS assessment_answers")
    for column in ("result_detail", "coding_results", "coding_score", "quiz_score", "mcq_score", "passed", "percentage", "attempt_number"):
        op.execute(f"ALTER TABLE assessment_attempts DROP COLUMN IF EXISTS {column}")
    op.execute("ALTER TABLE questions DROP COLUMN IF EXISTS coding_config")
    op.execute("ALTER TABLE questions DROP COLUMN IF EXISTS quiz_format")
    op.execute("ALTER TABLE assessments DROP COLUMN IF EXISTS is_published")
    op.execute("ALTER TABLE assessments DROP COLUMN IF EXISTS required_coding_questions")
    op.execute("ALTER TABLE assessments DROP COLUMN IF EXISTS level")
