"""ADR-024 — vrije-tekstvelden component.eigenaar_naam + component.leverancier verwijderd.

Revision ID: 0034_component_dep_velden
Revises: 0033_adr024_functietitel
Create Date: 2026-06-19

De vrije-tekstvelden `eigenaar_naam` (String 255) en `leverancier` (String 255) zijn vervangen
door de VerantwoordelijkheidSectie (roltoewijzingen, ADR-024 slice 2b) als enige plek voor
eigenaar-/leveranciersinformatie. `eigenaar_organisatie_id` (de partij-FK) blijft ongemoeid.
Geen te behouden data (dev-seed zette beide op None). Engine onaangeroerd.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0034_component_dep_velden"
down_revision: Union[str, Sequence[str], None] = "0033_adr024_functietitel"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("component", "eigenaar_naam")
    op.drop_column("component", "leverancier")


def downgrade() -> None:
    op.add_column("component", sa.Column("eigenaar_naam", sa.String(255), nullable=True))
    op.add_column("component", sa.Column("leverancier", sa.String(255), nullable=True))
