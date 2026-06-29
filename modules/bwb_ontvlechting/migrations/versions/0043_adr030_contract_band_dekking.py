"""ADR-030 — per-band (component↔contract) dekking.

Eén nieuwe tenant-scoped tabel (RLS + FORCE): `contract_band_dekking`. Eén rij per
(contract, component) met `dekking_sleutels` (text[]) uit de catalogus-dimensie `dekking`
(app-side gevalideerd, geen harde FK). Composiet-FK's naar `element` (zowel contract als
component zijn element-subtypes) met ON DELETE CASCADE → de band-dekking verdwijnt vanzelf als
het contract óf het component wordt verwijderd. Additief; náást de contract-brede `contract_dekking`.

Revision ID: 0043_adr030_contract_band_dekking
Revises: 0042_adr033_opgeslagen_view
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0043_adr030_contract_band_dekking"
down_revision: Union[str, Sequence[str], None] = "0042_adr033_opgeslagen_view"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contract_band_dekking",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("component_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dekking_sleutels", postgresql.ARRAY(sa.String(60)),
                  nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "contract_id", "component_id", name="uq_contract_band_dekking"),
    )
    op.create_index("ix_contract_band_dekking_tenant", "contract_band_dekking", ["tenant_id"])
    op.create_index("ix_contract_band_dekking_tenant_contract", "contract_band_dekking", ["tenant_id", "contract_id"])
    op.create_foreign_key(
        "fk_contract_band_dekking_contract", "contract_band_dekking", "element",
        ["tenant_id", "contract_id"], ["tenant_id", "id"], ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_contract_band_dekking_component", "contract_band_dekking", "element",
        ["tenant_id", "component_id"], ["tenant_id", "id"], ondelete="CASCADE",
    )
    op.execute("ALTER TABLE contract_band_dekking ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE contract_band_dekking FORCE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON contract_band_dekking "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )
    op.execute("REVOKE ALL ON contract_band_dekking FROM lk_app")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON contract_band_dekking TO lk_app")


def downgrade() -> None:
    op.drop_table("contract_band_dekking")
