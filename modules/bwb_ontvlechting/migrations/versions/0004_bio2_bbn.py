"""O2 (CD035) — 7.5 BIO2-classificatie: legacy Laag/Midden/Hoog soft-deactiveren.

Revision ID: 0004_bio2_bbn
Revises: 0003_antwoordconfig
Create Date: 2026-06-10

Contract-stap van een expand/contract (ADR-019 Besluit 9, soft-deactivate):
- `seed_antwoordconfig` (expand) levert 7.5 voortaan BBN1/BBN2/BBN3 (fresh + idempotent
  toegevoegd op bestaande deploys).
- Deze migratie deactiveert de legacy `laag/midden/hoog`-opties van **uitsluitend vraag
  7.5**, zodat ze niet meer kiesbaar zijn maar bestaande `antwoord_waarde` die ernaar
  verwijst resolvebaar blijft (de read levert inactieve sleutels mét `actief`-vlag).

NOOIT hard verwijderen of hernummeren (stabiele sleutels). Op een fresh deploy draait
deze migratie vóór `platform_init`: 7.5 heeft dan nog geen opties → 0 rijen geraakt;
de seed voegt daarna BBN toe. Idempotent (herhaald = no-op). Raakt de
score-/lifecycle-/blokkade-engine niet (alleen referentiedata).
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0004_bio2_bbn"
down_revision: Union[str, Sequence[str], None] = "0003_antwoordconfig"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_LEGACY = ("laag", "midden", "hoog")


def upgrade() -> None:
    op.execute(
        "UPDATE checklistvraag_optie SET actief = false "
        "WHERE vraag_code = '7.5' AND optie_sleutel IN ('laag', 'midden', 'hoog')"
    )


def downgrade() -> None:
    # Best-effort: heractiveer de legacy-opties (verwijdert BBN bewust NIET — die
    # zijn referentiedata en kunnen al in gebruik zijn).
    op.execute(
        "UPDATE checklistvraag_optie SET actief = true "
        "WHERE vraag_code = '7.5' AND optie_sleutel IN ('laag', 'midden', 'hoog')"
    )
