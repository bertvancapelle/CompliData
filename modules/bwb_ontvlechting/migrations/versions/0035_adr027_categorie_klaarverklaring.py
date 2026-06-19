"""ADR-027 slice 1 — tabel `categorie_klaarverklaring` (niet-scorende categorie-klaarverklaring).

Revision ID: 0035_adr027_klaarverklaring
Revises: 0034_component_dep_velden
Create Date: 2026-06-19

Eigen tenant-scoped registratie-tabel (GEEN element-subtype — een klaarverklaring is een feit, geen
ArchiMate-element). Eén levende verklaring per (component, categorie_nr) → `UNIQUE(tenant_id,
component_id, categorie_nr)`. `status` (klaar/open, default klaar) + verplichte `reden` +
server-gestempelde `verklaard_door`/`verklaard_op`; het verloop blijft via de append-only
audit-trail terug te lezen (geen aparte historie-tabel).

- `component_id` → composiet-FK `(tenant_id, component_id) → element(tenant_id, id)` ON DELETE
  CASCADE (verklaring verdwijnt met de component); `categorie_nr` zonder harde FK (categorie is
  geen entiteit; app-side gevalideerd tegen de checklistvragen van het componenttype);
- FORCE RLS + `tenant_isolation`-policy + REVOKE/GRANT conform db-skill;
- reverse-lookup-index `(tenant_id, component_id)`.

Engine onaangeroerd — registratief, geen lifecycle/score/blokkade.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0035_adr027_klaarverklaring"
down_revision: Union[str, Sequence[str], None] = "0034_component_dep_velden"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    status_enum = postgresql.ENUM("klaar", "open", name="klaarverklaring_status_enum", create_type=False)
    status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "categorie_klaarverklaring",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("component_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("categorie_nr", sa.Integer(), nullable=False),
        sa.Column("status", status_enum, nullable=False, server_default=sa.text("'klaar'")),
        sa.Column("reden", sa.Text(), nullable=False),
        sa.Column("verklaard_door", sa.String(255), nullable=True),
        sa.Column("verklaard_op", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "component_id", "categorie_nr", name="uq_categorie_klaarverklaring"),
    )
    op.create_index("ix_categorie_klaarverklaring_tenant", "categorie_klaarverklaring", ["tenant_id"])
    op.create_index("ix_categorie_klaarverklaring_tenant_component", "categorie_klaarverklaring",
                    ["tenant_id", "component_id"])
    op.create_foreign_key(
        "fk_categorie_klaarverklaring_component", "categorie_klaarverklaring", "element",
        ["tenant_id", "component_id"], ["tenant_id", "id"], ondelete="CASCADE",
    )
    op.execute("ALTER TABLE categorie_klaarverklaring ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE categorie_klaarverklaring FORCE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON categorie_klaarverklaring "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )
    op.execute("REVOKE ALL ON categorie_klaarverklaring FROM cd_app")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON categorie_klaarverklaring TO cd_app")


def downgrade() -> None:
    op.drop_table("categorie_klaarverklaring")
    postgresql.ENUM(name="klaarverklaring_status_enum").drop(op.get_bind(), checkfirst=True)
