"""Pydantic v2-schemas voor de entiteit Blokkade (ADR-009/013).

Blokkades zijn systeem-afgeleid (Model A): er is **geen** Create — ze ontstaan
automatisch uit een blokkerende Checklistscore. De gebruiker beheert alleen de
opvolging via Update (`status`, `toelichting`, `eigenaar`). `opgelost_op` is
server-beheerd (afgeleid uit `status`) en zit niet in Update.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from models.models import BlokkadeStatus
from schemas.applicatie import _optionele_tekst

_VERPLICHTE_VELDEN = frozenset({"status"})


class BlokkadeUpdate(BaseModel):
    """Handmatige opvolging. `opgelost_op` wordt server-zijdig uit `status` afgeleid."""

    model_config = ConfigDict(extra="forbid")

    status: BlokkadeStatus | None = None
    toelichting: str | None = None
    eigenaar: str | None = None

    @field_validator("toelichting")
    @classmethod
    def _v_toelichting(cls, v: str | None) -> str | None:
        return _optionele_tekst(v, 10_000)

    @field_validator("eigenaar")
    @classmethod
    def _v_eigenaar(cls, v: str | None) -> str | None:
        return _optionele_tekst(v, 255)

    @model_validator(mode="after")
    def _verbied_null_op_verplicht(self) -> "BlokkadeUpdate":
        for veld in _VERPLICHTE_VELDEN:
            if veld in self.model_fields_set and getattr(self, veld) is None:
                raise ValueError(f"{veld} mag niet op null worden gezet")
        return self


class BlokkadeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    checklistscore_id: uuid.UUID
    applicatie_id: uuid.UUID
    status: BlokkadeStatus
    toelichting: str | None
    eigenaar: str | None
    opgelost_op: datetime | None
    created_at: datetime
    updated_at: datetime


class BlokkadePagina(BaseModel):
    items: list[BlokkadeRead]
    volgende_cursor: str | None = None


class BlokkadeOpties(BaseModel):
    """Read-only keuzewaarden per enumveld (voor de frontend-dropdowns)."""

    status: list[str]
