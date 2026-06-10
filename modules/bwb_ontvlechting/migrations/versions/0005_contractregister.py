"""ADR-020 — leverancier-/contractregister (additieve feitenlaag).

Revision ID: 0005_contractregister
Revises: 0004_bio2_bbn
Create Date: 2026-06-10

Volledig ADDITIEF (geen wijziging aan bestaande tabellen/logica/engine):
vijf nieuwe tenant-scoped tabellen (RLS + FORCE) — `leverancier`, `contract`
(self-FK `mantelcontract_id` + CHECK type<->mantel), `contract_dekking`,
`contract_kostenmodel`, `applicatie_contract` — en één platform-brede
classificatie-catalogus `contractconfig_optie` (GEEN RLS, dimensie-discriminator).

Grants (least-privilege): tenant-tabellen volledige CRUD voor `cd_app` onder RLS;
de catalogus SELECT-only voor `cd_app` en SELECT/INSERT/UPDATE (géén DELETE —
soft-deactivate = UPDATE) voor `cd_platform`, identiek aan `checklistvraag_optie`
(ADR-019 fase 2A). De cross-row-invarianten horen in de service-laag (Fase B).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_contractregister"
down_revision: Union[str, Sequence[str], None] = "0004_bio2_bbn"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Tenant-scoped tabellen die de RLS-boilerplate krijgen (db-skill-patroon).
_TENANT_TABELLEN = [
    "leverancier",
    "contract",
    "contract_dekking",
    "contract_kostenmodel",
    "applicatie_contract",
]


def upgrade() -> None:
    bind = op.get_bind()

    contracttype = postgresql.ENUM(
        "mantelcontract", "deelcontract", "los_contract",
        name="contracttype_enum", create_type=False,
    )
    contracttype.create(bind, checkfirst=True)
    dimensie = postgresql.ENUM(
        "dekking", "kostenmodel", "relatie_rol",
        name="contractconfig_dimensie_enum", create_type=False,
    )
    dimensie.create(bind, checkfirst=True)

    # --- (a) Platform-brede catalogus (referentiedata, GEEN RLS) ---
    op.create_table(
        "contractconfig_optie",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("dimensie", dimensie, nullable=False),
        sa.Column("optie_sleutel", sa.String(60), nullable=False),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("volgorde", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("actief", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("dimensie", "optie_sleutel", name="uq_contractconfig_optie"),
    )

    # --- (b) Tenant-scoped feitenlaag (ouder vóór kind) ---
    op.create_table(
        "leverancier",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("naam", sa.String(255), nullable=False),
        sa.Column("straat_huisnummer", sa.String(255), nullable=True),
        sa.Column("postcode", sa.String(20), nullable=True),
        sa.Column("plaats", sa.String(255), nullable=True),
        sa.Column("contactpersoon", sa.String(255), nullable=True),
        sa.Column("telefoon", sa.String(40), nullable=True),
        sa.Column("mobiel", sa.String(40), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("omschrijving", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "contract",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("leverancier_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leverancier.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("contracttype", contracttype, nullable=False),
        sa.Column("mantelcontract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contract.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("contractnaam", sa.String(255), nullable=False),
        sa.Column("extern_contract_id", sa.String(255), nullable=True),
        sa.Column("leverancier_contract_id", sa.String(255), nullable=True),
        sa.Column("begindatum", sa.Date(), nullable=True),
        sa.Column("einddatum", sa.Date(), nullable=True),
        sa.Column("vernieuwingsdatum", sa.Date(), nullable=True),
        sa.Column("omschrijving", sa.Text(), nullable=True),
        sa.Column("toelichting", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "(contracttype = 'deelcontract' AND mantelcontract_id IS NOT NULL) "
            "OR (contracttype <> 'deelcontract' AND mantelcontract_id IS NULL)",
            name="ck_contract_mantel_consistentie",
        ),
    )

    for tag in ("contract_dekking", "contract_kostenmodel"):
        op.create_table(
            tag,
            sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contract.id", ondelete="CASCADE"), nullable=False),
            sa.Column("optie_sleutel", sa.String(60), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.UniqueConstraint("tenant_id", "contract_id", "optie_sleutel", name=f"uq_{tag}"),
        )

    op.create_table(
        "applicatie_contract",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("applicatie_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("applicatie.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contract.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relatie_rol", sa.String(60), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "applicatie_id", "contract_id", name="uq_applicatie_contract"),
    )

    # --- (c) Indexen (tenant_id als eerste kolom) ---
    op.create_index("ix_leverancier_tenant", "leverancier", ["tenant_id"])
    op.create_index("ix_contract_tenant_leverancier", "contract", ["tenant_id", "leverancier_id"])
    op.create_index("ix_contract_tenant_mantel", "contract", ["tenant_id", "mantelcontract_id"])
    op.create_index("ix_contract_tenant_type", "contract", ["tenant_id", "contracttype"])
    op.create_index("ix_contract_dekking_tenant_contract", "contract_dekking", ["tenant_id", "contract_id"])
    op.create_index("ix_contract_kostenmodel_tenant_contract", "contract_kostenmodel", ["tenant_id", "contract_id"])
    op.create_index("ix_applicatie_contract_tenant_app", "applicatie_contract", ["tenant_id", "applicatie_id"])
    op.create_index("ix_applicatie_contract_tenant_contract", "applicatie_contract", ["tenant_id", "contract_id"])

    # --- (d) RLS + grants op de tenant-tabellen (db-skill-boilerplate) ---
    for tabel in _TENANT_TABELLEN:
        op.execute(f"ALTER TABLE {tabel} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {tabel} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation ON {tabel} "
            f"USING (tenant_id = current_setting('app.tenant_id')::uuid)"
        )
        op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {tabel} TO cd_app")

    # --- (e) Catalogus-grants (identiek aan checklistvraag_optie, ADR-019 fase 2A) ---
    #     géén DELETE op de catalogus: soft-deactivate = UPDATE (ADR-012 Addendum B).
    op.execute("REVOKE ALL ON contractconfig_optie FROM cd_app")
    op.execute("GRANT SELECT ON contractconfig_optie TO cd_app")
    op.execute("GRANT SELECT, INSERT, UPDATE ON contractconfig_optie TO cd_platform")
    op.execute("GRANT USAGE, SELECT ON SEQUENCE contractconfig_optie_id_seq TO cd_platform")


def downgrade() -> None:
    bind = op.get_bind()
    # Kind vóór ouder; indexen/policies/grants/sequence vallen met de tabel weg.
    op.drop_table("applicatie_contract")
    op.drop_table("contract_kostenmodel")
    op.drop_table("contract_dekking")
    op.drop_table("contract")
    op.drop_table("leverancier")
    op.drop_table("contractconfig_optie")
    postgresql.ENUM(name="contractconfig_dimensie_enum").drop(bind, checkfirst=True)
    postgresql.ENUM(name="contracttype_enum").drop(bind, checkfirst=True)
