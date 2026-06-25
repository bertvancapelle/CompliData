"""ADR-033 slice 2 — opgeslagen & deelbare Impact-verkenner-views.

Twee nieuwe tenant-scoped tabellen (RLS + FORCE):
- `impact_view` (header): naam + maker (Keycloak-sub + e-mail-fallback) + `gedeeld`-vlag.
- `impact_view_component` (junctie): de geselecteerde componenten van een view.

Echte FK's (geen id-lijst-in-een-veld), beide ON DELETE CASCADE: view→junctie (view weg ⇒ selectie
weg) en component→element (component weg ⇒ valt vanzelf uit de selectie). `impact_view` krijgt een
`UNIQUE(tenant_id, id)` zodat de junctie er composiet naar kan FK'en. Additief — geen bestaande data
geraakt; registratie naast de engine.

Revision ID: 0042_adr033_opgeslagen_view
Revises: 0041_partij_aard_burger
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0042_adr033_opgeslagen_view"
down_revision: Union[str, Sequence[str], None] = "0041_partij_aard_burger"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Header: impact_view ────────────────────────────────────────────────────────
    op.create_table(
        "impact_view",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("naam", sa.String(150), nullable=False),
        sa.Column("maker_sub", sa.String(255), nullable=True),
        sa.Column("maker_email", sa.String(255), nullable=True),
        sa.Column("gedeeld", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        # (tenant_id, id) — nodig als doel voor de composiet-FK vanuit de junctie.
        sa.UniqueConstraint("tenant_id", "id", name="uq_impact_view_tenant_id"),
        # Geen twee gelijknamige views per maker.
        sa.UniqueConstraint("tenant_id", "maker_sub", "naam", name="uq_impact_view_maker_naam"),
    )
    op.create_index("ix_impact_view_tenant", "impact_view", ["tenant_id"])
    op.create_index("ix_impact_view_tenant_maker", "impact_view", ["tenant_id", "maker_sub"])
    op.execute("ALTER TABLE impact_view ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE impact_view FORCE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON impact_view "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )
    op.execute("REVOKE ALL ON impact_view FROM lk_app")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON impact_view TO lk_app")

    # ── Junctie: impact_view_component (de selectie) ───────────────────────────────
    op.create_table(
        "impact_view_component",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("view_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("component_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "view_id", "component_id", name="uq_impact_view_component"),
    )
    op.create_index("ix_impact_view_component_tenant", "impact_view_component", ["tenant_id"])
    op.create_index("ix_impact_view_component_tenant_view", "impact_view_component", ["tenant_id", "view_id"])
    op.create_index("ix_impact_view_component_tenant_comp", "impact_view_component", ["tenant_id", "component_id"])
    op.create_foreign_key(
        "fk_impact_view_component_view", "impact_view_component", "impact_view",
        ["tenant_id", "view_id"], ["tenant_id", "id"], ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_impact_view_component_element", "impact_view_component", "element",
        ["tenant_id", "component_id"], ["tenant_id", "id"], ondelete="CASCADE",
    )
    op.execute("ALTER TABLE impact_view_component ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE impact_view_component FORCE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON impact_view_component "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )
    op.execute("REVOKE ALL ON impact_view_component FROM lk_app")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON impact_view_component TO lk_app")


def downgrade() -> None:
    op.drop_table("impact_view_component")
    op.drop_table("impact_view")
