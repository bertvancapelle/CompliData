"""ADR-023 Fase F (F-3) — checklistvraag-betekenis: catalogus + koppeling + datamigratie.

Voegt toe (additief):
- platform-brede catalogus `vraagbetekenis_optie` (GEEN RLS) + de eerste betekenis
  `technische_plaatsing`. Grants identiek aan `relatiekenmerk_optie` (lk_app SELECT,
  lk_platform SELECT/INSERT/UPDATE — geen DELETE);
- kolom `checklistvraag.betekenis` (nullable) + `UNIQUE(tenant_id, componenttype,
  betekenis)` — per (tenant, componenttype) hoogstens één vraag met een gegeven betekenis;
  NULL is distinct in Postgres → onbeperkt veel vragen zonder betekenis;
- datamigratie (eenmalig, expand/contract): zet `betekenis='technische_plaatsing'` op de
  bestaande plaatsingsvraag (`code='2.2' AND componenttype='applicatie'`) **over álle
  tenants**. De migratie draait als lk_admin (superuser) → bypasst FORCE RLS, dus de UPDATE
  raakt elke tenant. Fresh deploys krijgen dit via `seed.py` (de 2.2-baseline-rij draagt de
  betekenis al).

Engine onaangeroerd: `betekenis` is classificatie — geen `component_profiel`/`checklistscore`/
`blokkade`/lifecycle wordt geraakt.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0024_adr023_vraagbetekenis"
down_revision: Union[str, Sequence[str], None] = "0023_checklist_dragend_fix"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_BETEKENISSEN = [
    ("technische_plaatsing", "Technische plaatsing (waar draait dit op)"),
]


def upgrade() -> None:
    # --- (a) platform-brede betekenis-catalogus (GEEN RLS) --------------------------
    op.create_table(
        "vraagbetekenis_optie",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("optie_sleutel", sa.String(60), nullable=False),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("volgorde", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("actief", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("optie_sleutel", name="uq_vraagbetekenis_optie"),
    )
    # Grants identiek aan relatiekenmerk_optie: lk_app SELECT (keuzeveld/validatie),
    # lk_platform beheer (geen DELETE).
    op.execute("REVOKE ALL ON vraagbetekenis_optie FROM lk_app")
    op.execute("GRANT SELECT ON vraagbetekenis_optie TO lk_app")
    op.execute("GRANT SELECT, INSERT, UPDATE ON vraagbetekenis_optie TO lk_platform")
    op.execute("GRANT USAGE, SELECT ON SEQUENCE vraagbetekenis_optie_id_seq TO lk_platform")
    for volgorde, (sleutel, label) in enumerate(_BETEKENISSEN):
        op.execute(
            sa.text(
                "INSERT INTO vraagbetekenis_optie (optie_sleutel, label, volgorde, actief) "
                "VALUES (:s, :l, :v, true) "
                "ON CONFLICT (optie_sleutel) DO NOTHING"
            ).bindparams(s=sleutel, l=label, v=volgorde)
        )

    # --- (b) koppeling-kolom + uniciteit op checklistvraag --------------------------
    op.add_column("checklistvraag", sa.Column("betekenis", sa.String(60), nullable=True))
    op.create_unique_constraint(
        "uq_checklistvraag_betekenis", "checklistvraag",
        ["tenant_id", "componenttype", "betekenis"],
    )

    # --- (c) datamigratie over álle tenants (lk_admin → bypasst FORCE RLS) ----------
    op.execute(
        sa.text(
            "UPDATE checklistvraag SET betekenis = 'technische_plaatsing' "
            "WHERE code = '2.2' AND componenttype = 'applicatie'"
        )
    )


def downgrade() -> None:
    op.drop_constraint("uq_checklistvraag_betekenis", "checklistvraag", type_="unique")
    op.drop_column("checklistvraag", "betekenis")
    op.drop_table("vraagbetekenis_optie")
