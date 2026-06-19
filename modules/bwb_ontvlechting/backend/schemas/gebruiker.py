"""Pydantic v2-schemas — gebruikersbeheer (ADR-029 Fase 2).

`GebruikerAanmakenRequest` bevat BEWUST geen wachtwoord-veld: de backend genereert een sterk
tijdelijk wachtwoord en geeft het éénmalig terug in `GebruikerAangemaaktResponse`. Email als
plain `str` + lichte format-validatie (consistent met de partij-schema's; geen harde
email-validator-dependency).
"""
import re
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from schemas.applicatie import _verplichte_tekst

_EMAIL_PATROON = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class GebruikerAanmakenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    naam: str
    email: str
    afdeling_id: uuid.UUID | None = None
    functietitel: str | None = None
    rol: Literal["medewerker", "viewer"] = "medewerker"

    @field_validator("naam")
    @classmethod
    def _naam(cls, v: str) -> str:
        return _verplichte_tekst(v, "naam", 255)

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        v = _verplichte_tekst(v, "email", 255).lower()
        if not _EMAIL_PATROON.match(v):
            raise ValueError("Geef een geldig e-mailadres op.")
        return v

    @field_validator("functietitel")
    @classmethod
    def _functietitel(cls, v: str | None) -> str | None:
        return v if v is None else _verplichte_tekst(v, "functietitel", 150)


class GebruikerPersoonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    keycloak_sub: str
    persoon_id: uuid.UUID
    naam: str
    email: str | None = None
    aangemaakt_op: datetime


class GebruikerAangemaaktResponse(BaseModel):
    """201-respons bij aanmaak. `tijdelijk_wachtwoord` wordt éénmalig getoond aan de
    beheerder en NOOIT opgeslagen of gelogd."""

    gebruiker: GebruikerPersoonRead
    tijdelijk_wachtwoord: str
