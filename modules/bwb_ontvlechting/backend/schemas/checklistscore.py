"""Pydantic v2-schemas voor de entiteit Checklistscore (ADR-009/013).

`score` is in Create **verplicht** (besluit Bert / ADR-013): een rij betekent
"gescoord". `applicatie_id` + `vraag_code` zitten in Create maar zijn immutabel
(niet in Update). `score` is bewerkbaar maar mag niet op null. Validatie-helpers
worden hergebruikt uit `schemas.applicatie`.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from models.models import ChecklistScore
from schemas.applicatie import _optionele_tekst

_VERPLICHTE_VELDEN = frozenset({"score"})


def _v_vraag_code(v: str) -> str:
    v = v.strip()
    if not v or len(v) > 10:
        raise ValueError("vraag_code is verplicht (max 10 tekens)")
    return v


class ChecklistscoreCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    applicatie_id: uuid.UUID
    vraag_code: str
    score: ChecklistScore  # verplicht (geen default)
    bevinding: str | None = None
    eigenaar: str | None = None
    actie: str | None = None

    @field_validator("vraag_code")
    @classmethod
    def _vraag_code(cls, v: str) -> str:
        return _v_vraag_code(v)

    @field_validator("bevinding", "actie")
    @classmethod
    def _v_lange_tekst(cls, v: str | None) -> str | None:
        return _optionele_tekst(v, 10_000)

    @field_validator("eigenaar")
    @classmethod
    def _v_eigenaar(cls, v: str | None) -> str | None:
        return _optionele_tekst(v, 255)


class ChecklistscoreUpdate(BaseModel):
    """Partiële update; `applicatie_id`/`vraag_code` immutabel ⇒ niet aanwezig.

    `score` mag worden gewijzigd maar niet op null gezet.
    """

    model_config = ConfigDict(extra="forbid")

    score: ChecklistScore | None = None
    bevinding: str | None = None
    eigenaar: str | None = None
    actie: str | None = None

    @field_validator("bevinding", "actie")
    @classmethod
    def _v_lange_tekst(cls, v: str | None) -> str | None:
        return _optionele_tekst(v, 10_000)

    @field_validator("eigenaar")
    @classmethod
    def _v_eigenaar(cls, v: str | None) -> str | None:
        return _optionele_tekst(v, 255)

    @model_validator(mode="after")
    def _verbied_null_op_verplicht(self) -> "ChecklistscoreUpdate":
        for veld in _VERPLICHTE_VELDEN:
            if veld in self.model_fields_set and getattr(self, veld) is None:
                raise ValueError(f"{veld} mag niet op null worden gezet")
        return self


class ChecklistscoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    applicatie_id: uuid.UUID
    vraag_code: str
    # Kolom is nullable in de DB; defensief getypeerd hoewel Create score afdwingt.
    score: ChecklistScore | None
    bevinding: str | None
    eigenaar: str | None
    actie: str | None
    created_at: datetime
    updated_at: datetime


class ChecklistscorePagina(BaseModel):
    items: list[ChecklistscoreRead]
    volgende_cursor: str | None = None


class ChecklistscoreOpties(BaseModel):
    """Read-only keuzewaarden per enumveld (voor de frontend-dropdowns)."""

    score: list[str]
