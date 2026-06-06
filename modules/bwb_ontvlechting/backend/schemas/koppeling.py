"""Pydantic v2-schemas voor de entiteit Koppeling (P5-vervolg, ADR-009).

Twee ouder-FK's (`bron_applicatie_id`, `doel_applicatie_id`), beide in Create,
immutabel (niet in Update). `richting`/`protocol`/`impact_bij_verbreking` zijn
enums (code leidend t.o.v. ADR-009). `bron ≠ doel` wordt op schema-niveau
afgedwongen → standaard FastAPI-422 (consistent met overige validatie); de
DB-`CHECK` is backstop (zie service).
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from models.models import ImpactVerbreking, Koppelprotocol, Koppelrichting
from schemas.applicatie import _optionele_tekst

_VERPLICHTE_VELDEN = frozenset({"richting", "protocol", "impact_bij_verbreking"})


class KoppelingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bron_applicatie_id: uuid.UUID
    doel_applicatie_id: uuid.UUID
    richting: Koppelrichting
    protocol: Koppelprotocol
    impact_bij_verbreking: ImpactVerbreking
    omschrijving: str | None = None

    @field_validator("omschrijving")
    @classmethod
    def _v_omschrijving(cls, v: str | None) -> str | None:
        return _optionele_tekst(v, 10_000)

    @model_validator(mode="after")
    def _bron_ongelijk_doel(self) -> "KoppelingCreate":
        if self.bron_applicatie_id == self.doel_applicatie_id:
            raise ValueError("bron_applicatie_id en doel_applicatie_id moeten verschillen")
        return self


class KoppelingUpdate(BaseModel):
    """Partiële update; ouder-FK's immutabel ⇒ niet aanwezig."""

    model_config = ConfigDict(extra="forbid")

    richting: Koppelrichting | None = None
    protocol: Koppelprotocol | None = None
    impact_bij_verbreking: ImpactVerbreking | None = None
    omschrijving: str | None = None

    @field_validator("omschrijving")
    @classmethod
    def _v_omschrijving(cls, v: str | None) -> str | None:
        return _optionele_tekst(v, 10_000)

    @model_validator(mode="after")
    def _verbied_null_op_verplicht(self) -> "KoppelingUpdate":
        for veld in _VERPLICHTE_VELDEN:
            if veld in self.model_fields_set and getattr(self, veld) is None:
                raise ValueError(f"{veld} mag niet op null worden gezet")
        return self


class KoppelingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    bron_applicatie_id: uuid.UUID
    doel_applicatie_id: uuid.UUID
    richting: Koppelrichting
    protocol: Koppelprotocol
    impact_bij_verbreking: ImpactVerbreking
    omschrijving: str | None
    created_at: datetime
    updated_at: datetime


class KoppelingPagina(BaseModel):
    items: list[KoppelingRead]
    volgende_cursor: str | None = None
