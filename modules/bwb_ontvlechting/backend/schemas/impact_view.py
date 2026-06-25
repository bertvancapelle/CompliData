"""Pydantic v2-schemas — opgeslagen Impact-verkenner-view (ADR-033 slice 2).

Create/Update met `extra='forbid'` + field-validators. De maker (`maker_sub`/`maker_email`) staat
NOOIT in de invoer — die stempelt de service server-side. `component_ids` = de startselectie (≥1,
gededupliceerd). `Read` levert de read-side geresolveerde maker-naam + `is_eigenaar` (mag de huidige
gebruiker bewerken/verwijderen) als transiente attributen die de service zet.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


def _verplichte_naam(v: str) -> str:
    if v is None or not str(v).strip():
        raise ValueError("naam is verplicht")
    v = str(v).strip()
    if len(v) > 150:
        raise ValueError("naam mag maximaal 150 tekens zijn")
    return v


def _dedup(ids: list[uuid.UUID]) -> list[uuid.UUID]:
    """Behoud-volgorde dedup; lege selectie is niet toegestaan."""
    if not ids:
        raise ValueError("selectie mag niet leeg zijn")
    gezien: set[uuid.UUID] = set()
    uniek: list[uuid.UUID] = []
    for cid in ids:
        if cid not in gezien:
            gezien.add(cid)
            uniek.append(cid)
    return uniek


class ImpactViewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    naam: str
    component_ids: list[uuid.UUID]
    gedeeld: bool = False

    @field_validator("naam")
    @classmethod
    def _v_naam(cls, v: str) -> str:
        return _verplichte_naam(v)

    @field_validator("component_ids")
    @classmethod
    def _v_ids(cls, v: list[uuid.UUID]) -> list[uuid.UUID]:
        return _dedup(v)


class ImpactViewUpdate(BaseModel):
    """Partieel: alleen meegestuurde velden wijzigen. Een meegestuurde `component_ids` VERVANGT de
    hele selectie."""

    model_config = ConfigDict(extra="forbid")

    naam: str | None = None
    component_ids: list[uuid.UUID] | None = None
    gedeeld: bool | None = None

    @field_validator("naam")
    @classmethod
    def _v_naam(cls, v: str | None) -> str | None:
        return _verplichte_naam(v) if v is not None else v

    @field_validator("component_ids")
    @classmethod
    def _v_ids(cls, v: list[uuid.UUID] | None) -> list[uuid.UUID] | None:
        return _dedup(v) if v is not None else v


class ImpactViewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    naam: str
    component_ids: list[uuid.UUID]
    gedeeld: bool
    maker_email: str | None              # e-mail-fallback (de stabiele sub blijft server-side)
    maker_naam: str | None = None        # read-side geresolveerd (sub → persoon.naam) of e-mail
    is_eigenaar: bool = False            # mag de huidige gebruiker deze view bewerken/verwijderen?
    created_at: datetime
    updated_at: datetime
