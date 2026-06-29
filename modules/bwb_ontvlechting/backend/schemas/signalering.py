"""Pydantic v2-schemas — Signalering registratiegaten (ADR-035, Slice 1).

Read-only afgeleide signalen; geen schema-/modelwijziging.
"""
import uuid

from pydantic import BaseModel


class ComponentSignaalRead(BaseModel):
    id: uuid.UUID
    naam: str
    lifecycle_status: str | None = None
    signaal: str  # 'component_zonder_eigenaar' | 'component_zonder_verantwoordelijke'
    niveau: str  # 'kritiek' (Slice 1)


class RegistratiegatenRead(BaseModel):
    component_zonder_eigenaar: list[ComponentSignaalRead]
    component_zonder_verantwoordelijke: list[ComponentSignaalRead]


class BadgeRead(BaseModel):
    signalen: list[str]
    kritiek: int
    aandacht: int
