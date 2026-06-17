"""Pydantic v2-schemas — consistentie-signalering technische plaatsing
(ADR-023 Fase F / F-3 stap 2).

Read-only afgeleid signaal: per component het signaaltype + een leesbare reden. Geen
schema-/modelwijziging.
"""
import uuid

from pydantic import BaseModel


class PlaatsingSignaalRead(BaseModel):
    component_id: uuid.UUID
    naam: str
    componenttype: str
    signaal: str  # 'beoordeeld_niet_vastgelegd' | 'vastgelegd_niet_beoordeeld'
    score: str | None = None  # score van de plaatsingsvraag (None = ongescoord)
    draait_op: bool
    reden: str
