"""add demo seed support fields

Revision ID: 20260507_0002
Revises: 20260507_0001
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa

revision = "20260507_0002"
down_revision = "20260507_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {table: {column["name"] for column in inspector.get_columns(table)} for table in inspector.get_table_names()}
    if "email" not in columns.get("landlords", set()):
        op.add_column("landlords", sa.Column("email", sa.String(length=255), nullable=True))
    if "address" not in columns.get("landlords", set()):
        op.add_column("landlords", sa.Column("address", sa.Text(), nullable=True))
    if "description" not in columns.get("properties", set()):
        op.add_column("properties", sa.Column("description", sa.Text(), nullable=True))
    if "country" not in columns.get("properties", set()):
        op.add_column("properties", sa.Column("country", sa.String(length=120), nullable=True))
    if "institution" not in columns.get("tenants", set()):
        op.add_column("tenants", sa.Column("institution", sa.String(length=255), nullable=True))
    if "priority" not in columns.get("support_tickets", set()):
        op.add_column("support_tickets", sa.Column("priority", sa.String(length=40), nullable=True))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {table: {column["name"] for column in inspector.get_columns(table)} for table in inspector.get_table_names()}
    if "priority" in columns.get("support_tickets", set()):
        op.drop_column("support_tickets", "priority")
    if "institution" in columns.get("tenants", set()):
        op.drop_column("tenants", "institution")
    if "country" in columns.get("properties", set()):
        op.drop_column("properties", "country")
    if "description" in columns.get("properties", set()):
        op.drop_column("properties", "description")
    if "address" in columns.get("landlords", set()):
        op.drop_column("landlords", "address")
    if "email" in columns.get("landlords", set()):
        op.drop_column("landlords", "email")
