"""add district areas and district admin assignments

Revision ID: 20260528_0013
Revises: 20260527_0012
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260528_0013"
down_revision = "20260527_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "district_areas",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "district_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("districts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=120),
            nullable=False,
        ),
        sa.Column(
            "slug",
            sa.String(length=120),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_unique_constraint(
        "uq_district_areas_slug",
        "district_areas",
        ["slug"],
    )

    op.create_index(
        "ix_district_areas_district_id",
        "district_areas",
        ["district_id"],
    )

    op.create_index(
        "ix_district_areas_is_active",
        "district_areas",
        ["is_active"],
    )

    op.create_table(
        "district_admin_assignments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "district_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("districts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_unique_constraint(
        "uq_district_admin_assignment",
        "district_admin_assignments",
        ["user_id", "district_id"],
    )

    op.create_index(
        "ix_district_admin_assignments_user_id",
        "district_admin_assignments",
        ["user_id"],
    )

    op.create_index(
        "ix_district_admin_assignments_district_id",
        "district_admin_assignments",
        ["district_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_district_admin_assignments_district_id",
        table_name="district_admin_assignments",
    )

    op.drop_index(
        "ix_district_admin_assignments_user_id",
        table_name="district_admin_assignments",
    )

    op.drop_constraint(
        "uq_district_admin_assignment",
        "district_admin_assignments",
        type_="unique",
    )

    op.drop_table("district_admin_assignments")

    op.drop_index(
        "ix_district_areas_is_active",
        table_name="district_areas",
    )

    op.drop_index(
        "ix_district_areas_district_id",
        table_name="district_areas",
    )

    op.drop_constraint(
        "uq_district_areas_slug",
        "district_areas",
        type_="unique",
    )

    op.drop_table("district_areas")
