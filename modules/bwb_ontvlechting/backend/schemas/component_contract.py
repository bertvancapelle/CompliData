"""Pydantic v2-schemas voor ComponentContract (ADR-021 Besluit 7 — Fase B).

Generaliseert de contract-koppeling naar component-niveau (élk component kan contracten
dragen). Zelfde vorm/rol-validatie als ApplicatieContract (CD041); `relatie_rol` is een
sleutel uit de contract-catalogus-dimensie `relatie_rol`.
"""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from models.models import ContractType


class ComponentContractCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    component_id: uuid.UUID
    contract_id: uuid.UUID
    relatie_rol: str


class ComponentContractUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relatie_rol: str


class ComponentContractRead(BaseModel):
    id: uuid.UUID
    component_id: uuid.UUID
    contract_id: uuid.UUID
    relatie_rol: str
    relatie_rol_label: str
    created_at: datetime
    updated_at: datetime


class ContractVoorComponent(BaseModel):
    """Item van 'component → contracten' (zelfde vorm als het app→contracten-overzicht)."""

    koppeling_id: uuid.UUID
    contract_id: uuid.UUID
    contractnaam: str
    contracttype: ContractType
    leverancier_id: uuid.UUID
    leverancier_naam: str
    begindatum: date | None
    einddatum: date | None
    relatie_rol: str
    relatie_rol_label: str
