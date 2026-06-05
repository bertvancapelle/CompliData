"""SQLAlchemy declarative base + gedeelde mixins (framework).

`Base` wordt door Alembic (`alembic/env.py`) gebruikt voor autogenerate.
Module-modellen importeren `Base`, `TenantMixin` en `TimestampMixin` hier.
Nog geen modellen gedefinieerd — V001 vult deze tijdens module-ontwikkeling.
"""
from app.models.base import Base, TenantMixin, TimestampMixin

__all__ = ["Base", "TenantMixin", "TimestampMixin"]
