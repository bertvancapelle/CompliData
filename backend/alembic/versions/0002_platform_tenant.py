"""Platform-register: tenant-tabel (ADR-012).

Revision ID: 0002_platform_tenant
Revises: 0001_bwb_initial
Create Date: 2026-06-06

Platform-tabel (GEEN RLS, niet tenant-scoped). Alleen lk_platform mag CRUD;
lk_app wordt expliciet ontzegd (domein-scheiding). Gechaind aan de bestaande
module-head zodat er één Alembic-head blijft.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_platform_tenant"
down_revision: Union[str, Sequence[str], None] = "0001_bwb_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column("naam", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'actief'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("naam", name="uq_tenant_naam"),
        sa.UniqueConstraint("slug", name="uq_tenant_slug"),
    )

    # Platform-domein: uitsluitend lk_platform mag het register beheren.
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON tenant TO lk_platform")
    # lk_app krijgt via ALTER DEFAULT PRIVILEGES standaard rechten op nieuwe
    # tabellen; die hier expliciet intrekken — het platform-register valt buiten
    # het tenant-domein (least privilege, ADR-012).
    op.execute("REVOKE ALL ON tenant FROM lk_app")


def downgrade() -> None:
    op.drop_table("tenant")
