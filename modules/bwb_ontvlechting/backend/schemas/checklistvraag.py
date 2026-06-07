"""Pydantic v2-schema voor ChecklistVraag (read-only referentiedata)."""
from pydantic import BaseModel, ConfigDict

from models.models import ChecklistPrioriteit


class ChecklistVraagRead(BaseModel):
    """Volledige weergave — exact het model (geen tenant_id; referentiedata)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    categorie_nr: int
    categorie_naam: str
    vraag: str
    prioriteit: ChecklistPrioriteit
