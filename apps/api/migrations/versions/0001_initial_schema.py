"""Create the initial merchant dispute schema."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    case_status = postgresql.ENUM(
        "RECEIVED",
        "COLLECTING",
        "READY_FOR_REVIEW",
        "SUBMITTED",
        "WON",
        "LOST",
        "FAILED",
        "EXPIRED",
        name="casestatus",
        create_type=False,
    )
    webhook_status = postgresql.ENUM(
        "RECEIVED", "QUEUED", "PROCESSED", "FAILED", name="webhookeventstatus", create_type=False
    )
    evidence_source = postgresql.ENUM(
        "PAYPAL",
        "SHOPIFY",
        "SHIPPO",
        "ZENDESK",
        "VISION",
        "MERCHANT",
        name="evidencesource",
        create_type=False,
    )
    case_status.create(op.get_bind(), checkfirst=True)
    webhook_status.create(op.get_bind(), checkfirst=True)
    evidence_source.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "merchants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "merchant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_id", sa.String(length=128), nullable=False),
        sa.Column("event_type", sa.String(length=200), nullable=False),
        sa.Column("status", webhook_status, nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "received_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("merchant_id", "event_id", name="uq_webhook_merchant_event"),
    )
    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "merchant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("paypal_dispute_id", sa.String(length=128), nullable=False),
        sa.Column("status", case_status, nullable=False),
        sa.Column("response_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("merchant_id", "paypal_dispute_id", name="uq_case_merchant_dispute"),
    )
    op.create_index("ix_cases_merchant_status", "cases", ["merchant_id", "status"])
    op.create_index("ix_cases_response_deadline", "cases", ["response_deadline"])
    op.create_table(
        "evidence_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", evidence_source, nullable=False),
        sa.Column("kind", sa.String(length=100), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True)),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_evidence_case_occurred", "evidence_items", ["case_id", "occurred_at"])


def downgrade() -> None:
    op.drop_index("ix_evidence_case_occurred", table_name="evidence_items")
    op.drop_table("evidence_items")
    op.drop_index("ix_cases_response_deadline", table_name="cases")
    op.drop_index("ix_cases_merchant_status", table_name="cases")
    op.drop_table("cases")
    op.drop_table("webhook_events")
    op.drop_table("merchants")
    op.execute("DROP TYPE IF EXISTS evidencesource")
    op.execute("DROP TYPE IF EXISTS webhookeventstatus")
    op.execute("DROP TYPE IF EXISTS casestatus")
