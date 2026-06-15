"""ADR-023 Fase E (E2) — Work Package: hiërarchisch migratiewerk-element (additief).

Revision ID: 0020_adr023_workpackage
Revises: 0019_relrol_naar_relkenmerk
Create Date: 2026-06-15

Voegt de subtype-tabel `work_package` toe (element-subtype: shared-PK composiet-FK →
element, FORCE RLS). Hiërarchie via een composiet self-FK `(tenant_id, bovenliggend_id)`
→ `work_package(tenant_id, id)` met **ON DELETE RESTRICT** (een werkpakket met directe
subpakketten kan niet verwijderd worden — de subboom wordt niet stilzwijgend weggevaagd).
Een DB-CHECK weert de directe self-parent; transitieve cycluspreventie zit in de service.

`element_type_enum` bevat 'work_package' al sinds 0011 → geen enum-wijziging. Geen
datamigratie (er is geen bestaande work_package-data).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0020_adr023_workpackage"
down_revision: Union[str, Sequence[str], None] = "0019_relrol_naar_relkenmerk"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "work_package",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("naam", sa.String(255), nullable=False),
        sa.Column("toelichting", sa.Text(), nullable=True),
        sa.Column("bovenliggend_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        # Composiet-FK-target voor de self-FK (tenant-consistent).
        sa.UniqueConstraint("tenant_id", "id", name="uq_work_package_tenant_id"),
        sa.CheckConstraint(
            "bovenliggend_id IS NULL OR bovenliggend_id <> id",
            name="ck_work_package_geen_self_parent",
        ),
    )
    op.create_index("ix_work_package_tenant", "work_package", ["tenant_id"])
    op.create_index("ix_work_package_tenant_bovenliggend", "work_package",
                    ["tenant_id", "bovenliggend_id"])
    # Shared-PK: composiet-FK (tenant_id, id) → element (cross-tenant uitgesloten, cascade).
    op.create_foreign_key(
        "fk_work_package_element", "work_package", "element",
        ["tenant_id", "id"], ["tenant_id", "id"], ondelete="CASCADE",
    )
    # Hiërarchie: composiet self-FG met RESTRICT (subboom niet stilzwijgend wegvagen).
    op.create_foreign_key(
        "fk_work_package_bovenliggend", "work_package", "work_package",
        ["tenant_id", "bovenliggend_id"], ["tenant_id", "id"], ondelete="RESTRICT",
    )
    op.execute("ALTER TABLE work_package ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE work_package FORCE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON work_package "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )
    op.execute("REVOKE ALL ON work_package FROM cd_app")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON work_package TO cd_app")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON work_package")
    op.drop_constraint("fk_work_package_bovenliggend", "work_package", type_="foreignkey")
    op.drop_constraint("fk_work_package_element", "work_package", type_="foreignkey")
    op.drop_index("ix_work_package_tenant_bovenliggend", table_name="work_package")
    op.drop_index("ix_work_package_tenant", table_name="work_package")
    op.drop_table("work_package")
