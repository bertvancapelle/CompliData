"""Auth-flow request-schemas (ADR-002) — strikte invoervalidatie.

`extra='forbid'` weigert onbekende queryparameters; field-validators bewaken
lengte en tekenset. De callback-velden dekken de OIDC-parameters die Keycloak
meestuurt (code/state bij succes; error/error_description bij weigering;
session_state/iss altijd) — alles daarbuiten wordt geweigerd.
"""
import re

from pydantic import BaseModel, ConfigDict, field_validator

_STATE_RE = re.compile(r"^[A-Za-z0-9_\-]{16,256}$")
_CODE_RE = re.compile(r"^[A-Za-z0-9._\-]{1,2048}$")


class LoginParams(BaseModel):
    """Queryparameters voor GET /auth/login."""

    model_config = ConfigDict(extra="forbid")

    next: str | None = None

    @field_validator("next")
    @classmethod
    def _next_grenzen(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if len(v) > 512 or any(ord(c) < 0x20 for c in v):
            # Te lang of bevat control-chars → onbruikbaar; open-redirect-
            # normalisatie gebeurt in de route (_valideer_next → app-root).
            return None
        return v


class CallbackParams(BaseModel):
    """Queryparameters voor GET /auth/callback (Keycloak-redirect)."""

    model_config = ConfigDict(extra="forbid")

    code: str | None = None
    state: str | None = None
    error: str | None = None
    error_description: str | None = None
    session_state: str | None = None
    iss: str | None = None

    @field_validator("state")
    @classmethod
    def _state_vorm(cls, v: str | None) -> str | None:
        if v is not None and not _STATE_RE.match(v):
            raise ValueError("ongeldige state")
        return v

    @field_validator("code")
    @classmethod
    def _code_vorm(cls, v: str | None) -> str | None:
        if v is not None and not _CODE_RE.match(v):
            raise ValueError("ongeldige code")
        return v
