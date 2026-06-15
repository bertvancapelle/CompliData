"""ADR-023 Fase D — vaste ArchiMate-typing van de element-typen (laag-borging).

Anders dan de **componenttypen** (waarvan de typing tenant-/beheer-configureerbaar in de
catalogus `componentconfig_optie` staat, dim `componenttype`), ligt de typing van de
**element-typen** architectonisch **vast** — niet per tenant aan te passen. Daarom een
code-constante (single source) i.p.v. een catalogus.

Bron van waarheid: de model-docstrings (`models.py`): datatype = ArchiMate data object,
gebruikersgroep = business actor/role, contract = business-laag (contract).

Een dekkingstest (`test_archimate_fase_d.py`) bewaakt dat **elk** `ElementType` óf een
volledige vaste typing draagt, óf bewust geparkeerd is (migratielaag, Fase E), óf zijn
typing via de componenttype-catalogus krijgt (`component`). Zo kan een vergeten indeling
niet ongemerkt ontstaan wanneer Fase E nieuwe element-typen realiseert.
"""
from models.models import ElementType

# Toegestane waardelijsten (ADR-023 OK-3). `behavior` is in het huidige gecureerde model
# nog leeg (geen gedragselementen); de migratie-elementen vullen dit mogelijk in Fase E.
TOEGESTANE_LAGEN = frozenset({"business", "application", "technology", "implementation_migration"})
TOEGESTANE_ASPECTEN = frozenset({"active", "passive", "behavior"})

# Vaste typing per element-type: {archimate_element, laag, aspect}.
# `component` ontbreekt hier bewust — zie ELEMENT_TYPEN_VIA_COMPONENTTYPE.
ELEMENT_ARCHIMATE_TYPING: dict[ElementType, dict[str, str]] = {
    # Contract: business-laag, passieve structuur (ArchiMate Contract ⊂ Business Object).
    ElementType.contract: {"archimate_element": "contract", "laag": "business", "aspect": "passive"},
    # Datatype: applicatielaag, passieve structuur (ArchiMate Data Object).
    ElementType.datatype: {"archimate_element": "data_object", "laag": "application", "aspect": "passive"},
    # Gebruikersgroep: business-laag, actieve structuur (ArchiMate Business Role/Actor).
    ElementType.gebruikersgroep: {"archimate_element": "business_role", "laag": "business", "aspect": "active"},
}

# Element-typen die de `ElementType`-enum al kent maar die in het huidige model nog GEEN
# subtype-tabel hebben (ADR-023 migratielaag). Bewust geparkeerd: Fase E vult de vaste
# typing in (verplaatst het type uit deze set naar ELEMENT_ARCHIMATE_TYPING). De
# dekkingstest dwingt af dat een nieuw, niet-geclassificeerd type hier niet stil doorheen valt.
ELEMENT_TYPEN_NOG_NIET_GEREALISEERD: frozenset[ElementType] = frozenset({
    ElementType.plateau,
    ElementType.gap,
    ElementType.work_package,
    ElementType.deliverable,
})

# `component` krijgt zijn ArchiMate-typing PER componenttype uit de catalogus
# (`componentconfig_optie`, dim `componenttype`) — geborgd door
# `test_dekkingstest_elk_componenttype_heeft_mapping`. Het kent dus geen één vaste waarde.
ELEMENT_TYPEN_VIA_COMPONENTTYPE: frozenset[ElementType] = frozenset({ElementType.component})


def typing_voor(element_type: ElementType) -> dict[str, str] | None:
    """De vaste ArchiMate-typing van een element-type, of None als die niet vast is
    (`component`: per componenttype) of nog niet gerealiseerd (migratielaag, Fase E)."""
    return ELEMENT_ARCHIMATE_TYPING.get(element_type)
