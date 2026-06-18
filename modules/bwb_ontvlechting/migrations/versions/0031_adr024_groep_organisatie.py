"""ADR-024 UX-B6-a — gebruikersgroep-organisatie: vrije tekst → verwijzing naar een organisatie-partij.

Revision ID: 0031_adr024_groep_org
Revises: 0030_adr024_roltoewijzing
Create Date: 2026-06-18

Vervangt `gebruikersgroep.organisatie` (String NOT NULL) door een optionele composiet-FK
`(tenant_id, organisatie_id) → element(tenant_id, id)` naar een partij met aard=organisatie
(app-side geborgd, zoals de contract-leverancier). ON DELETE **SET NULL** (optioneel veld; een
verwijderde organisatie maakt de groep-organisatie 'onbekend', geen RESTRICT-blokkade).
Reverse-lookup-index. Geen backfill (besluit Bert: geen te behouden data — verse dev-reset).

Engine onaangeroerd (registratief/relationeel). De eigenaar-organisatie op applicatie/component
is B6-b en valt hier buiten.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0031_adr024_groep_org"
down_revision: Union[str, Sequence[str], None] = "0030_adr024_roltoewijzing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("gebruikersgroep", sa.Column("organisatie_id", postgresql.UUID(as_uuid=True), nullable=True))
    # Composiet-FK (tenant_id, organisatie_id) → element. ON DELETE SET NULL moet ALLEEN
    # `organisatie_id` nullen — een kale `SET NULL` zou óók de gedeelde `tenant_id` (NOT NULL)
    # nullen en de NOT-NULL-constraint schenden. PostgreSQL 15+ kolom-specifieke variant.
    op.execute(
        "ALTER TABLE gebruikersgroep ADD CONSTRAINT fk_gebruikersgroep_organisatie "
        "FOREIGN KEY (tenant_id, organisatie_id) REFERENCES element (tenant_id, id) "
        "ON DELETE SET NULL (organisatie_id)"
    )
    op.create_index("ix_gebruikersgroep_tenant_organisatie", "gebruikersgroep", ["tenant_id", "organisatie_id"])
    op.drop_column("gebruikersgroep", "organisatie")


def downgrade() -> None:
    op.add_column("gebruikersgroep", sa.Column("organisatie", sa.String(120), nullable=False, server_default=""))
    op.alter_column("gebruikersgroep", "organisatie", server_default=None)
    op.drop_index("ix_gebruikersgroep_tenant_organisatie", table_name="gebruikersgroep")
    op.drop_constraint("fk_gebruikersgroep_organisatie", "gebruikersgroep", type_="foreignkey")
    op.drop_column("gebruikersgroep", "organisatie_id")
