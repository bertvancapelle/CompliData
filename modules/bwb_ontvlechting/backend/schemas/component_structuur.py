"""Pydantic v2-schemas voor ComponentStructuur (ADR-021 Besluit 6)."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from schemas.applicatie import _verplichte_tekst


class ComponentStructuurCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    component_id: uuid.UUID
    op_component_id: uuid.UUID
    relatietype: str
    omschrijving: str | None = None

    @field_validator("relatietype")
    @classmethod
    def _v(cls, v: str) -> str:
        return _verplichte_tekst(v, "relatietype", 60)


class ComponentStructuurUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relatietype: str | None = None
    omschrijving: str | None = None

    @field_validator("relatietype")
    @classmethod
    def _v(cls, v: str | None) -> str | None:
        return v if v is None else _verplichte_tekst(v, "relatietype", 60)


class ComponentStructuurRead(BaseModel):
    id: uuid.UUID
    component_id: uuid.UUID
    op_component_id: uuid.UUID
    relatietype: str
    relatietype_label: str
    omschrijving: str | None
    created_at: datetime
    updated_at: datetime
