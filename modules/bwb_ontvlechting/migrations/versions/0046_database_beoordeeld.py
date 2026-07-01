"""LI058 (Slice 2) — activeer componenttype `database` als beoordeeld type.

Reconcile (contract) van `checklist_dragend` op de componentcatalogus voor bestaande DB's:
zet `database` op `true` (fresh deploys doen dit al via seed_componentconfig). Spiegelt het
0023-patroon. Data-only; downgrade zet 'm terug op false.

De runtime-backfill van bestaande `database`-componenten (profiel + herberekening) loopt via de
platform-toggle-handler (checklist_dragend False→True); deze migratie zet enkel de catalogus-vlag.

Revision ID: 0046_database_beoordeeld
Revises: 0045_component_transitie
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0046_database_beoordeeld"
down_revision: Union[str, Sequence[str], None] = "0045_component_transitie"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE componentconfig_optie SET checklist_dragend = true "
        "WHERE dimensie = 'componenttype' AND optie_sleutel = 'database'"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE componentconfig_optie SET checklist_dragend = false "
        "WHERE dimensie = 'componenttype' AND optie_sleutel = 'database'"
    )
