"""ADR-024 (Optie 1) — functietitel op partij (geldt voor aard=persoon; service dwingt af).

Revision ID: 0033_adr024_functietitel
Revises: 0032_adr024_eigenaar_org
Create Date: 2026-06-19

Voegt een nullable `functietitel` (String 150) toe aan `partij`. Schema-breed nullable; de
persoon-only-regel handhaaft de service (422 FUNCTIETITEL_ALLEEN_PERSOON). E-mail/telefoon zijn
en blijven gedeelde contactvelden (Optie 1). RLS ongewijzigd (partij heeft al FORCE RLS); audit
ongewijzigd (bouw_wijziging snapshot't alle kolommen automatisch). Engine onaangeroerd.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0033_adr024_functietitel"
down_revision: Union[str, Sequence[str], None] = "0032_adr024_eigenaar_org"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("partij", sa.Column("functietitel", sa.String(150), nullable=True))


def downgrade() -> None:
    op.drop_column("partij", "functietitel")
