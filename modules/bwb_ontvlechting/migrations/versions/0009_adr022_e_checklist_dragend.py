"""ADR-022 Fase E — `checklist_dragend`-vlag op de componentcatalogus.

Revision ID: 0009_adr022_e_checklist_dragend
Revises: 0008_adr022_w1_tenant_vragenset
Create Date: 2026-06-13

Besluit 1: "checklist-dragend" wordt een expliciete catalogus-eigenschap op
`componentconfig_optie` (dim=`componenttype`) — de enige bron voor "krijgt dit type
een component_profiel + engine". `applicatie` = true; alle overige typen default
false. Platform-brede catalogus (geen RLS); grants ongewijzigd.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_adr022_e_checklist_dragend"
down_revision: Union[str, Sequence[str], None] = "0008_adr022_w1_tenant_vragenset"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "componentconfig_optie",
        sa.Column("checklist_dragend", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    # Backfill: alleen het systeemtype `applicatie` is standaard checklist-dragend.
    op.execute(
        "UPDATE componentconfig_optie SET checklist_dragend = true "
        "WHERE dimensie = 'componenttype' AND optie_sleutel = 'applicatie'"
    )


def downgrade() -> None:
    op.drop_column("componentconfig_optie", "checklist_dragend")
