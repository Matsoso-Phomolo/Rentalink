"""add commercial saas operations tables

Revision ID: 20260524_0006
Revises: 20260524_0005
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260524_0006"
down_revision = "20260524_0005"
branch_labels = None
depends_on = None


def has_column(inspector, table: str, column: str) -> bool:
    return column in {item["name"] for item in inspector.get_columns(table)}


def has_index(inspector, table: str, index_name: str) -> bool:
    return index_name in {item["name"] for item in inspector.get_indexes(table)}


def has_fk(inspector, table: str, fk_name: str) -> bool:
    return fk_name in {item["name"] for item in inspector.get_foreign_keys(table)}


def add_index(inspector, table: str, column: str, unique: bool = False) -> None:
    index_name = f"ix_{table}_{column}"
    if not has_index(inspector, table, index_name):
        op.create_index(index_name, table, [column], unique=unique)


def enum_type(bind, name: str, values: tuple[str, ...]):
    if bind.dialect.name == "postgresql":
        enum_obj = postgresql.ENUM(*values, name=name, create_type=False)
        enum_obj.create(bind, checkfirst=True)
        return enum_obj
    return sa.Enum(*values, name=name)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if bind.dialect.name == "postgresql":
        for value in ("ISSUE_LEASE", "SIGN_LEASE", "VERIFY_LISTING", "CREATE_DAMAGE_RECORD"):
            op.execute(f"ALTER TYPE audit_action ADD VALUE IF NOT EXISTS '{value}'")

    listing_verification_status = enum_type(
        bind,
        "listing_verification_status",
        ("unverified", "pending_verification", "verified", "rejected"),
    )
    lease_status = enum_type(bind, "lease_status", ("draft", "issued", "signed", "active", "expired", "terminated"))
    message_thread_status = enum_type(bind, "message_thread_status", ("open", "closed"))
    inspection_type = enum_type(bind, "inspection_type", ("move_in", "move_out"))
    inspection_status = enum_type(bind, "inspection_status", ("draft", "completed"))
    damage_status = enum_type(bind, "damage_status", ("reported", "verified", "charged", "waived", "repaired"))
    subscription_status = enum_type(bind, "subscription_status", ("active", "trialing", "past_due", "cancelled"))

    if "room_listings" in tables:
        additions = [
            ("internet_included", sa.Column("internet_included", sa.Boolean(), nullable=True, server_default=sa.false())),
            ("furnished", sa.Column("furnished", sa.Boolean(), nullable=True, server_default=sa.false())),
            ("parking_available", sa.Column("parking_available", sa.Boolean(), nullable=True, server_default=sa.false())),
            ("pets_allowed", sa.Column("pets_allowed", sa.Boolean(), nullable=True, server_default=sa.false())),
            ("gender_preference", sa.Column("gender_preference", sa.String(length=80), nullable=True)),
            ("verification_status", sa.Column("verification_status", listing_verification_status, nullable=True, server_default="unverified")),
            ("verification_note", sa.Column("verification_note", sa.Text(), nullable=True)),
        ]
        for name, column in additions:
            if not has_column(inspector, "room_listings", name):
                op.add_column("room_listings", column)
        for column in ("internet_included", "furnished", "parking_available", "pets_allowed", "verification_status"):
            add_index(inspector, "room_listings", column)
        if has_column(inspector, "room_listings", "is_verified") and has_column(inspector, "room_listings", "verification_status"):
            op.execute(
                "UPDATE room_listings SET verification_status = 'verified' "
                "WHERE is_verified = true AND verification_status IN ('unverified', 'pending_verification')"
            )

    if "payment_receipts" in tables:
        additions = [
            ("room_id", sa.Column("room_id", sa.UUID(), nullable=True)),
            ("transaction_reference", sa.Column("transaction_reference", sa.String(length=160), nullable=True)),
            ("pdf_url", sa.Column("pdf_url", sa.String(length=500), nullable=True)),
        ]
        for name, column in additions:
            if not has_column(inspector, "payment_receipts", name):
                op.add_column("payment_receipts", column)
        if not has_index(inspector, "payment_receipts", "ix_payment_receipts_room_id"):
            op.create_index("ix_payment_receipts_room_id", "payment_receipts", ["room_id"])
        if not has_index(inspector, "payment_receipts", "ix_payment_receipts_transaction_reference"):
            op.create_index("ix_payment_receipts_transaction_reference", "payment_receipts", ["transaction_reference"])
        if not has_fk(inspector, "payment_receipts", "fk_payment_receipts_room_id_rooms"):
            op.create_foreign_key("fk_payment_receipts_room_id_rooms", "payment_receipts", "rooms", ["room_id"], ["id"])

    if "lease_agreements" not in tables:
        op.create_table(
            "lease_agreements",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("landlord_id", sa.UUID(), nullable=False),
            sa.Column("tenant_id", sa.UUID(), nullable=False),
            sa.Column("property_id", sa.UUID(), nullable=False),
            sa.Column("room_id", sa.UUID(), nullable=False),
            sa.Column("occupancy_id", sa.UUID(), nullable=False),
            sa.Column("lease_number", sa.String(length=80), nullable=False),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("end_date", sa.Date(), nullable=True),
            sa.Column("monthly_rent", sa.Numeric(12, 2), nullable=False),
            sa.Column("deposit_amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("terms", sa.Text(), nullable=True),
            sa.Column("status", lease_status, nullable=False),
            sa.Column("tenant_signed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("landlord_signed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("pdf_url", sa.String(length=500), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["landlord_id"], ["landlords.id"]),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.ForeignKeyConstraint(["property_id"], ["properties.id"]),
            sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
            sa.ForeignKeyConstraint(["occupancy_id"], ["occupancies.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("lease_number"),
        )
        for column in ("landlord_id", "tenant_id", "property_id", "room_id", "occupancy_id", "lease_number", "status"):
            op.create_index(f"ix_lease_agreements_{column}", "lease_agreements", [column], unique=column == "lease_number")

    if "message_threads" not in tables:
        op.create_table(
            "message_threads",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("landlord_id", sa.UUID(), nullable=True),
            sa.Column("subject", sa.String(length=255), nullable=False),
            sa.Column("application_id", sa.UUID(), nullable=True),
            sa.Column("support_ticket_id", sa.UUID(), nullable=True),
            sa.Column("lease_id", sa.UUID(), nullable=True),
            sa.Column("payment_submission_id", sa.UUID(), nullable=True),
            sa.Column("status", message_thread_status, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["application_id"], ["tenant_applications.id"]),
            sa.ForeignKeyConstraint(["landlord_id"], ["landlords.id"]),
            sa.ForeignKeyConstraint(["lease_id"], ["lease_agreements.id"]),
            sa.ForeignKeyConstraint(["payment_submission_id"], ["payment_submissions.id"]),
            sa.ForeignKeyConstraint(["support_ticket_id"], ["support_tickets.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        for column in ("landlord_id", "application_id", "support_ticket_id", "lease_id", "payment_submission_id", "status"):
            op.create_index(f"ix_message_threads_{column}", "message_threads", [column])

    if "messages" not in tables:
        op.create_table(
            "messages",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("thread_id", sa.UUID(), nullable=False),
            sa.Column("sender_user_id", sa.UUID(), nullable=False),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["sender_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["thread_id"], ["message_threads.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_messages_thread_id", "messages", ["thread_id"])
        op.create_index("ix_messages_sender_user_id", "messages", ["sender_user_id"])

    if "room_inspections" not in tables:
        op.create_table(
            "room_inspections",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("landlord_id", sa.UUID(), nullable=False),
            sa.Column("tenant_id", sa.UUID(), nullable=True),
            sa.Column("room_id", sa.UUID(), nullable=False),
            sa.Column("occupancy_id", sa.UUID(), nullable=True),
            sa.Column("inspection_type", inspection_type, nullable=False),
            sa.Column("status", inspection_status, nullable=False),
            sa.Column("room_condition", sa.Text(), nullable=True),
            sa.Column("walls", sa.Text(), nullable=True),
            sa.Column("door_lock", sa.Text(), nullable=True),
            sa.Column("windows", sa.Text(), nullable=True),
            sa.Column("electricity", sa.Text(), nullable=True),
            sa.Column("water", sa.Text(), nullable=True),
            sa.Column("furniture", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["landlord_id"], ["landlords.id"]),
            sa.ForeignKeyConstraint(["occupancy_id"], ["occupancies.id"]),
            sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        for column in ("landlord_id", "tenant_id", "room_id", "occupancy_id", "inspection_type", "status"):
            op.create_index(f"ix_room_inspections_{column}", "room_inspections", [column])

    if "damage_records" not in tables:
        op.create_table(
            "damage_records",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("landlord_id", sa.UUID(), nullable=False),
            sa.Column("tenant_id", sa.UUID(), nullable=True),
            sa.Column("room_id", sa.UUID(), nullable=False),
            sa.Column("inspection_id", sa.UUID(), nullable=True),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("estimated_cost", sa.Numeric(12, 2), nullable=False),
            sa.Column("status", damage_status, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["inspection_id"], ["room_inspections.id"]),
            sa.ForeignKeyConstraint(["landlord_id"], ["landlords.id"]),
            sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        for column in ("landlord_id", "tenant_id", "room_id", "inspection_id", "status"):
            op.create_index(f"ix_damage_records_{column}", "damage_records", [column])

    if "subscription_plans" not in tables:
        op.create_table(
            "subscription_plans",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("monthly_price", sa.Numeric(12, 2), nullable=False),
            sa.Column("max_properties", sa.Integer(), nullable=False),
            sa.Column("max_rooms", sa.Integer(), nullable=False),
            sa.Column("features", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
        )
        op.create_index("ix_subscription_plans_is_active", "subscription_plans", ["is_active"])

    if "landlord_subscriptions" not in tables:
        op.create_table(
            "landlord_subscriptions",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("landlord_id", sa.UUID(), nullable=False),
            sa.Column("plan_id", sa.UUID(), nullable=False),
            sa.Column("status", subscription_status, nullable=False),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("renewal_date", sa.Date(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["landlord_id"], ["landlords.id"]),
            sa.ForeignKeyConstraint(["plan_id"], ["subscription_plans.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        for column in ("landlord_id", "plan_id", "status"):
            op.create_index(f"ix_landlord_subscriptions_{column}", "landlord_subscriptions", [column])


def downgrade() -> None:
    pass
