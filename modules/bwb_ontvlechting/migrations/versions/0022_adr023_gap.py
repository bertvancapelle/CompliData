"""ADR-023 Fase E (E4) — Gap: geregistreerde kloof baseline → doel (additief).

Revision ID: 0022_adr023_gap
Revises: 0021_adr023_deliverable
Create Date: 2026-06-15

Voegt de subtype-tabel `gap` toe (element-subtype: shared-PK composiet-FK → element,
FORCE RLS). Een gap verwijst hard naar precies één **baseline-plateau** en één
**doel-plateau** via twee verplichte composiet-FK-kolommen
`(tenant_id, <kolom>) → element(tenant_id, id)` (2-ariteit hard in het schema; Besluit 1).
Een DB-CHECK `baseline <> doel` is de backstop op de service-validatie
(`BASELINE_GELIJK_AAN_DOEL`). De FK's wijzen naar `element` (dat draagt de
`UNIQUE(tenant_id, id)`); dat het écht plateaus zijn wordt door de service afgedwongen
(`ONGELDIG_PLATEAU`).

Gap-leden (component/contract) lopen via het bestaande relatietype `association` in het
unified relatiemodel — géén schema hier, géén nieuw relatietype, géén FK-kolommen.

`element_type_enum` bevat 'gap' al sinds 0011 → geen enum-wijziging. Geen datamigratie
(er is geen bestaande gap-data).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0022_adr023_gap"
down_revision: Union[str, Sequence[str], None] = "0021_adr023_deliverable"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gap",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("naam", sa.String(255), nullable=False),
        sa.Column("toelichting", sa.Text(), nullable=True),
        sa.Column("baseline_plateau_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("doel_plateau_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("baseline_plateau_id <> doel_plateau_id", name="ck_gap_baseline_ne_doel"),
    )
    op.create_index("ix_gap_tenant", "gap", ["tenant_id"])
    # Shared-PK → element (cascade element → gap-subtype + association-relaties).
    op.create_foreign_key(
        "fk_gap_element", "gap", "element",
        ["tenant_id", "id"], ["tenant_id", "id"], ondelete="CASCADE",
    )
    # 2-ariteit hard: baseline + doel verwijzen naar element (tenant-consistent). Géén
    # cascade — een gap mag nooit stilzwijgend verdwijnen als een plateau wordt verwijderd
    # (RESTRICT-default: een referentieel plateau kan niet weg zolang een gap eraan hangt).
    op.create_foreign_key(
        "fk_gap_baseline_plateau", "gap", "element",
        ["tenant_id", "baseline_plateau_id"], ["tenant_id", "id"],
    )
    op.create_foreign_key(
        "fk_gap_doel_plateau", "gap", "element",
        ["tenant_id", "doel_plateau_id"], ["tenant_id", "id"],
    )
    op.execute("ALTER TABLE gap ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE gap FORCE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON gap "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )
    op.execute("REVOKE ALL ON gap FROM lk_app")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON gap TO lk_app")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON gap")
    op.drop_constraint("fk_gap_doel_plateau", "gap", type_="foreignkey")
    op.drop_constraint("fk_gap_baseline_plateau", "gap", type_="foreignkey")
    op.drop_constraint("fk_gap_element", "gap", type_="foreignkey")
    op.drop_index("ix_gap_tenant", table_name="gap")
    op.drop_table("gap")
