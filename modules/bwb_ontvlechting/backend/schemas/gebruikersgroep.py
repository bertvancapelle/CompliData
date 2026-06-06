"""Pydantic v2-schemas voor de entiteit Gebruikersgroep (P5-vervolg, ADR-009).

Zelfde patroon als `schemas/applicatie.py`, zónder lifecycle. `organisatie` is
vrije tekst (≤120, niet-leeg) — geen enum, net als `eigenaar_organisatie`.
`aantal_gebruikers` is optioneel en niet-negatief (`ge=0`). `applicatie_id`
zit in Create maar niet in Update (immutabel).
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from schemas.applicatie import _optionele_tekst, _verplichte_tekst

_VERPLICHTE_VELDEN = frozenset({"organisatie"})


class GebruikersgroepCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    applicatie_id: uuid.UUID
    organisatie: str
    afdeling: str | None = None
    aantal_gebruikers: int | None = Field(default=None, ge=0)

    @field_validator("organisatie")
    @classmethod
    def _v_organisatie(cls, v: str) -> str:
        # Vrije tekst (configureerbaar per tenant) — geen enum.
        return _verplichte_tekst(v, "organisatie", 120)

    @field_validator("afdeling")
    @classmethod
    def _v_afdeling(cls, v: str | None) -> str | None:
        return _optionele_tekst(v, 255)


class GebruikersgroepUpdate(BaseModel):
    """Partiële update; `applicatie_id` immutabel ⇒ niet aanwezig."""

    model_config = ConfigDict(extra="forbid")

    organisatie: str | None = None
    afdeling: str | None = None
    aantal_gebruikers: int | None = Field(default=None, ge=0)

    @field_validator("organisatie")
    @classmethod
    def _v_organisatie(cls, v: str | None) -> str | None:
        return v if v is None else _verplichte_tekst(v, "organisatie", 120)

    @field_validator("afdeling")
    @classmethod
    def _v_afdeling(cls, v: str | None) -> str | None:
        return _optionele_tekst(v, 255)

    @model_validator(mode="after")
    def _verbied_null_op_verplicht(self) -> "GebruikersgroepUpdate":
        for veld in _VERPLICHTE_VELDEN:
            if veld in self.model_fields_set and getattr(self, veld) is None:
                raise ValueError(f"{veld} mag niet op null worden gezet")
        return self


class GebruikersgroepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    applicatie_id: uuid.UUID
    organisatie: str
    afdeling: str | None
    aantal_gebruikers: int | None
    created_at: datetime
    updated_at: datetime


class GebruikersgroepPagina(BaseModel):
    items: list[GebruikersgroepRead]
    volgende_cursor: str | None = None
