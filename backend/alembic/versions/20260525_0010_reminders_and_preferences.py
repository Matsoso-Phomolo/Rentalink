"""add reminder logs and notification preferences

Revision ID: 20260525_0010
Revises: 20260524_0009
Create Date: 2026-05-25 00:10:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260525_0010"
down_revision = "20260524_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("in_app_enabled", sa.Boolean(), nullable=False),
        sa.Column("email_enabled", sa.Boolean(), nullable=False),
        sa.Column("whatsapp_enabled", sa.Boolean(), nullable=False),
        sa.Column("sms_enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_notification_preferences_user_id"), "notification_preferences", ["user_id"], unique=True)

    op.create_table(
        "reminder_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("landlord_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("channel", sa.String(length=40), nullable=False),
        sa.Column("reminder_type", sa.String(length=80), nullable=False),
        sa.Column("target_id", sa.String(length=80), nullable=False),
        sa.Column("scheduled_for", sa.Date(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["landlord_id"], ["landlords.id"]),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"]),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reminder_type", "target_id", "channel", "scheduled_for", name="uq_reminder_target_channel_schedule"),
    )
    op.create_index(op.f("ix_reminder_logs_channel"), "reminder_logs", ["channel"], unique=False)
    op.create_index(op.f("ix_reminder_logs_landlord_id"), "reminder_logs", ["landlord_id"], unique=False)
    op.create_index(op.f("ix_reminder_logs_property_id"), "reminder_logs", ["property_id"], unique=False)
    op.create_index(op.f("ix_reminder_logs_reminder_type"), "reminder_logs", ["reminder_type"], unique=False)
    op.create_index(op.f("ix_reminder_logs_room_id"), "reminder_logs", ["room_id"], unique=False)
    op.create_index(op.f("ix_reminder_logs_scheduled_for"), "reminder_logs", ["scheduled_for"], unique=False)
    op.create_index(op.f("ix_reminder_logs_status"), "reminder_logs", ["status"], unique=False)
    op.create_index(op.f("ix_reminder_logs_target_id"), "reminder_logs", ["target_id"], unique=False)
    op.create_index(op.f("ix_reminder_logs_tenant_id"), "reminder_logs", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_reminder_logs_user_id"), "reminder_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reminder_logs_user_id"), table_name="reminder_logs")
    op.drop_index(op.f("ix_reminder_logs_tenant_id"), table_name="reminder_logs")
    op.drop_index(op.f("ix_reminder_logs_target_id"), table_name="reminder_logs")
    op.drop_index(op.f("ix_reminder_logs_status"), table_name="reminder_logs")
    op.drop_index(op.f("ix_reminder_logs_scheduled_for"), table_name="reminder_logs")
    op.drop_index(op.f("ix_reminder_logs_room_id"), table_name="reminder_logs")
    op.drop_index(op.f("ix_reminder_logs_reminder_type"), table_name="reminder_logs")
    op.drop_index(op.f("ix_reminder_logs_property_id"), table_name="reminder_logs")
    op.drop_index(op.f("ix_reminder_logs_landlord_id"), table_name="reminder_logs")
    op.drop_index(op.f("ix_reminder_logs_channel"), table_name="reminder_logs")
    op.drop_table("reminder_logs")
    op.drop_index(op.f("ix_notification_preferences_user_id"), table_name="notification_preferences")
    op.drop_table("notification_preferences")
