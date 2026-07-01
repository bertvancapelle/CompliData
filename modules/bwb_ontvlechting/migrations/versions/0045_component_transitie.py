"""LI057 (Slice 1) — transitie-attributen component-breed + migratiepad-rename.

`migratiepad`/`complexiteit`/`prioriteit` verhuizen van de `applicatie`-subtabel naar het
basis-`component` (élk componenttype), NOT NULL met defaults. Prod-veilig (expand):
1. `migratiepad_enum`-waarde `tijdelijk_gedeeld` → `gedeeld` (atomair; bestaande rijen mee-hernoemd).
2. kolommen toevoegen mét `server_default` → bestaande rijen krijgen direct de default (geen NULL-venster).
3. backfill uit de `applicatie`-subtabel voor bestaande applicaties.

De `applicatie`-subtabel-kolommen blijven (voorlopig) staan als spiegel; de service dual-writet.
De daadwerkelijke drop + service-opruiming is de latere contract-slice. Engine onaangeroerd:
de scoring leest deze velden niet (lifecycle-driver blijft de checklistscore).

Revision ID: 0045_component_transitie
Revises: 0044_lk_audit_append_only
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0045_component_transitie"
down_revision: Union[str, Sequence[str], None] = "0044_lk_audit_append_only"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Bestaande DB-enumtypes (in 0001 aangemaakt) — hier alléén refereren, niet opnieuw creëren.
_migratiepad = postgresql.ENUM(name="migratiepad_enum", create_type=False)
_niveau = postgresql.ENUM(name="niveau_enum", create_type=False)


def upgrade() -> None:
    # 1. Enum-waarde hernoemen — atomair; alle rijen die 'tijdelijk_gedeeld' gebruiken worden mee-hernoemd.
    op.execute("ALTER TYPE migratiepad_enum RENAME VALUE 'tijdelijk_gedeeld' TO 'gedeeld'")

    # 2. Kolommen op het basis-component met server_default (bestaande rijen krijgen direct de default).
    op.add_column(
        "component",
        sa.Column("migratiepad", _migratiepad, nullable=False, server_default=sa.text("'onbekend'")),
    )
    op.add_column(
        "component",
        sa.Column("complexiteit", _niveau, nullable=False, server_default=sa.text("'midden'")),
    )
    op.add_column(
        "component",
        sa.Column("prioriteit", _niveau, nullable=False, server_default=sa.text("'midden'")),
    )

    # 3. Backfill uit de applicatie-subtabel (shared-PK a.id == c.id) — apps behouden hun waarden.
    op.execute(
        """
        UPDATE component c
        SET migratiepad = a.migratiepad,
            complexiteit = a.complexiteit,
            prioriteit = a.prioriteit
        FROM applicatie a
        WHERE a.tenant_id = c.tenant_id AND a.id = c.id
        """
    )


def downgrade() -> None:
    op.drop_column("component", "prioriteit")
    op.drop_column("component", "complexiteit")
    op.drop_column("component", "migratiepad")
    op.execute("ALTER TYPE migratiepad_enum RENAME VALUE 'gedeeld' TO 'tijdelijk_gedeeld'")
