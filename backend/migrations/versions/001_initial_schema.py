"""Initial schema — experiments, results, audit_logs

Revision ID: 001
Revises: 
Create Date: 2026-03-13 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "experiments",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("hypothesis", sa.Text, nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("metric_baseline", sa.Float, nullable=False),
        sa.Column("state", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("verdict", sa.String(20), nullable=True),
        sa.Column("verdict_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.CheckConstraint(
            "state IN ('draft', 'running', 'paused', 'completed')",
            name="ck_experiments_state",
        ),
        sa.CheckConstraint(
            "verdict IS NULL OR verdict IN ('ship', 'rollback', 'iterate')",
            name="ck_experiments_verdict",
        ),
    )

    op.create_table(
        "experiment_results",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column(
            "experiment_id",
            sa.String(36),
            sa.ForeignKey("experiments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("control_value", sa.Float, nullable=False),
        sa.Column("variant_value", sa.Float, nullable=False),
        sa.Column("sample_size_control", sa.Integer, nullable=False),
        sa.Column("sample_size_variant", sa.Integer, nullable=False),
        sa.Column("duration_days", sa.Integer, nullable=False),
        sa.Column("recorded_at", sa.DateTime, nullable=False),
        sa.CheckConstraint("sample_size_control > 0", name="ck_results_control_positive"),
        sa.CheckConstraint("sample_size_variant > 0", name="ck_results_variant_positive"),
        sa.CheckConstraint("duration_days > 0", name="ck_results_duration_positive"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column(
            "experiment_id",
            sa.String(36),
            sa.ForeignKey("experiments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("from_state", sa.String(20), nullable=True),
        sa.Column("to_state", sa.String(20), nullable=True),
        sa.Column("metadata", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    # Indexes for common query patterns
    op.create_index("ix_experiments_state", "experiments", ["state"])
    op.create_index("ix_experiments_created_at", "experiments", ["created_at"])
    op.create_index("ix_audit_logs_experiment_id", "audit_logs", ["experiment_id"])
    op.create_index("ix_results_experiment_id", "experiment_results", ["experiment_id"])


def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("experiment_results")
    op.drop_table("experiments")


## Folder structure it should look like
