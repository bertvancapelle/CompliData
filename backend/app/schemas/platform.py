"""Platform-schemas (ADR-012) — tenant-provisioning, strikte invoervalidatie."""
import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,38}[a-z0-9]$")


class TenantAanmaken(BaseModel):
    """Body voor POST /platform/tenants."""

    model_config = ConfigDict(extra="forbid")

    naam: str
    slug: str

    @field_validator("naam")
    @classmethod
    def _naam(cls, v: str) -> str:
        v = v.strip()
        if not (1 <= len(v) <= 255):
            raise ValueError("naam moet 1–255 tekens zijn")
        return v

    @field_validator("slug")
    @classmethod
    def _slug(cls, v: str) -> str:
        v = v.strip().lower()
        if not _SLUG_RE.match(v):
            raise ValueError("slug moet kleine letters/cijfers/koppeltekens zijn (2–40)")
        return v


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    naam: str
    slug: str
    status: str
    created_at: datetime
