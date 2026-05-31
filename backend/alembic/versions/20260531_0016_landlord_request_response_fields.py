"""add landlord request response contact fields

Revision ID: 20260531_0016
Revises: 20260529_0015
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260531_0016"
down_revision = "20260529_0015"
branch_labels = None
depends_on = None


def has_column(inspector, table: str, column: str) -> bool:
    return column in {item["name"] for item in inspector.get_columns(table)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "landlord_requests" not in tables:
        return

    if bind.dialect.name == "postgresql":
        response_method_type = postgresql.ENUM(
            "phone_call",
            "whatsapp",
            "email",
            "sms",
            name="preferred_response_method",
            create_type=False,
        )
        response_method_type.create(bind, checkfirst=True)
    else:
        response_method_type = sa.Enum(
            "phone_call",
            "whatsapp",
            "email",
            "sms",
            name="preferred_response_method",
        )

    if not has_column(inspector, "landlord_requests", "preferred_response_method"):
        op.add_column(
            "landlord_requests",
            sa.Column(
                "preferred_response_method",
                response_method_type,
                nullable=False,
                server_default="email",
            ),
        )

    if not has_column(inspector, "landlord_requests", "response_contact_value"):
        op.add_column(
            "landlord_requests",
            sa.Column("response_contact_value", sa.String(length=255), nullable=True),
        )

    op.execute(
        """
        UPDATE landlord_requests
        SET response_contact_value = COALESCE(response_contact_value, email)
        WHERE response_contact_value IS NULL
        """
    )


def downgrade() -> None:
    pass
