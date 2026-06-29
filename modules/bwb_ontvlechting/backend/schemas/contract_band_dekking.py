"""Pydantic v2-schemas — ADR-030 per-band (component↔contract) dekking."""
from pydantic import BaseModel, field_validator


class BandDekkingRead(BaseModel):
    contract_breed: list[str]            # labels (contract-brede dekking)
    per_band: list[str] | None = None    # labels (per-band dekking; None = niet ingesteld)
    per_band_sleutels: list[str] | None = None  # sleutels (voor de bewerk-multiselect)
    toon_per_band: bool


class BandDekkingUpdate(BaseModel):
    model_config = {"extra": "forbid"}
    dekking_sleutels: list[str]

    @field_validator("dekking_sleutels")
    @classmethod
    def _v_sleutels(cls, v: list[str]) -> list[str]:
        if any((not isinstance(s, str)) or not s.strip() or len(s) > 60 for s in v):
            raise ValueError("dekking_sleutels: niet-lege strings van max 60 tekens.")
        return v
