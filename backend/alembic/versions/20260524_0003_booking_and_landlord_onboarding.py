"""add booking request and landlord onboarding fields

Revision ID: 20260524_0003
Revises: 20260507_0002
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260524_0003"
down_revision = "20260507_0002"
branch_labels = None
depends_on = None


def has_column(inspector, table: str, column: str) -> bool:
    return column in {item["name"] for item in inspector.get_columns(table)}


def has_index(inspector, table: str, index_name: str) -> bool:
    return index_name in {item["name"] for item in inspector.get_indexes(table)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if bind.dialect.name == "postgresql":
        for value in ("inquiry_pending", "form_sent", "submitted", "expired"):
            op.execute(f"ALTER TYPE application_status ADD VALUE IF NOT EXISTS '{value}'")

    if "landlords" in tables:
        if not has_column(inspector, "landlords", "system_landlord_number"):
            op.add_column("landlords", sa.Column("system_landlord_number", sa.String(length=40), nullable=True))
        if not has_index(inspector, "landlords", "ix_landlords_system_landlord_number"):
            op.create_index("ix_landlords_system_landlord_number", "landlords", ["system_landlord_number"], unique=True)
        if not has_column(inspector, "landlords", "is_active"):
            op.add_column("landlords", sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()))
        if not has_index(inspector, "landlords", "ix_landlords_is_active"):
            op.create_index("ix_landlords_is_active", "landlords", ["is_active"])

    if "landlord_requests" not in tables:
        request_status = postgresql.ENUM("pending", "approved", "rejected", name="landlord_request_status", create_type=False)
        request_status.create(bind, checkfirst=True)
        op.create_table(
            "landlord_requests",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("business_name", sa.String(length=255), nullable=False),
            sa.Column("full_name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("phone", sa.String(length=40), nullable=True),
            sa.Column("address", sa.Text(), nullable=True),
            sa.Column("message", sa.Text(), nullable=True),
            sa.Column("status", request_status, nullable=False),
            sa.Column("admin_note", sa.Text(), nullable=True),
            sa.Column("landlord_id", sa.UUID(), nullable=True),
            sa.Column("approved_by_user_id", sa.UUID(), nullable=True),
            sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["landlord_id"], ["landlords.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_landlord_requests_email", "landlord_requests", ["email"])
        op.create_index("ix_landlord_requests_landlord_id", "landlord_requests", ["landlord_id"])
        op.create_index("ix_landlord_requests_status", "landlord_requests", ["status"])

    if "tenant_applications" in tables:
        additions = [
            ("room_id", sa.Column("room_id", sa.UUID(), nullable=True)),
            ("property_id", sa.Column("property_id", sa.UUID(), nullable=True)),
            ("landlord_id", sa.Column("landlord_id", sa.UUID(), nullable=True)),
            ("gender", sa.Column("gender", sa.String(length=80), nullable=True)),
            ("alternative_phone", sa.Column("alternative_phone", sa.String(length=40), nullable=True)),
            ("national_id", sa.Column("national_id", sa.String(length=120), nullable=True)),
            ("passport_number", sa.Column("passport_number", sa.String(length=120), nullable=True)),
            ("institution", sa.Column("institution", sa.String(length=255), nullable=True)),
            ("emergency_contact_name", sa.Column("emergency_contact_name", sa.String(length=255), nullable=True)),
            ("emergency_contact_phone", sa.Column("emergency_contact_phone", sa.String(length=40), nullable=True)),
            ("application_token", sa.Column("application_token", sa.String(length=160), nullable=True)),
            ("token_expires_at", sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True)),
            ("form_sent_at", sa.Column("form_sent_at", sa.DateTime(timezone=True), nullable=True)),
            ("submitted_at", sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True)),
        ]
        for name, column in additions:
            if not has_column(inspector, "tenant_applications", name):
                op.add_column("tenant_applications", column)
        for column in ("room_id", "property_id", "landlord_id", "application_token"):
            index_name = f"ix_tenant_applications_{column}"
            if has_index(inspector, "tenant_applications", index_name):
                continue
            if column == "application_token":
                op.create_index(index_name, "tenant_applications", [column], unique=True)
            else:
                op.create_index(index_name, "tenant_applications", [column])
        op.execute(
            """
            UPDATE tenant_applications AS ta
            SET room_id = COALESCE(ta.room_id, rl.room_id),
                property_id = COALESCE(ta.property_id, rl.property_id),
                landlord_id = COALESCE(ta.landlord_id, rl.landlord_id)
            FROM room_listings AS rl
            WHERE ta.listing_id = rl.id
            """
        )


def downgrade() -> None:
    pass
