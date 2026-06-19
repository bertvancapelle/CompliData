"""ADR-029 Fase 2 — koppeltabel `gebruiker_persoon` (Keycloak-login <-> persoon-partij).

Revision ID: 0037_adr029_gebruiker_persoon
Revises: 0036_adr027_kv_component
Create Date: 2026-06-20

Tenant-scoped registratiefeit (FORCE RLS), géén element-subtype. Composiet-FK
`(tenant_id, persoon_id) -> element(tenant_id, id)` ON DELETE CASCADE. Twee UNIQUE-constraints:
één login per tenant (`keycloak_sub`) en één persoon per tenant (`persoon_id`). Puur
registratief — raakt lifecycle/score niet.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0037_adr029_gebruiker_persoon"
down_revision: Union[str, Sequence[str], None] = "0036_adr027_kv_component"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gebruiker_persoon",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("keycloak_sub", sa.String(255), nullable=False),
        sa.Column("persoon_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("aangemaakt_op", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "keycloak_sub", name="uq_gebruiker_persoon_sub"),
        sa.UniqueConstraint("tenant_id", "persoon_id", name="uq_gebruiker_persoon_persoon"),
    )
    op.create_index("ix_gebruiker_persoon_sub", "gebruiker_persoon", ["tenant_id", "keycloak_sub"])
    op.create_foreign_key(
        "fk_gebruiker_persoon_element", "gebruiker_persoon", "element",
        ["tenant_id", "persoon_id"], ["tenant_id", "id"], ondelete="CASCADE",
    )
    op.execute("ALTER TABLE gebruiker_persoon ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE gebruiker_persoon FORCE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON gebruiker_persoon "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )
    op.execute("REVOKE ALL ON gebruiker_persoon FROM PUBLIC")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON gebruiker_persoon TO cd_app")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON gebruiker_persoon")
    op.drop_table("gebruiker_persoon")
