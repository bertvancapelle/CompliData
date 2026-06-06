"""Platform-modellen (ADR-012) — NIET tenant-scoped, GEEN RLS.

De `tenant`-tabel is het platform-register van tenants. Hij wordt uitsluitend
via het platform-domein (cd_platform) benaderd; tenant-accounts (cd_app) hebben
er geen toegang toe. Het aanmaken van een tenant-record raakt geen
tenant-gescopete data — een nieuwe tenant start leeg.
"""
import uuid

from sqlalchemy import String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenant"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    naam: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'actief'")
    )
