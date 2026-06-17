"""Seed — default checklistvraag-betekenis-catalogus (ADR-023 Fase F / F-3).

Platform-brede referentiedata (tabel `vraagbetekenis_optie`). Idempotent via
`ON CONFLICT (optie_sleutel) DO NOTHING`. Draait UITSLUITEND via `platform_init`
(init-container). `bouw_vraagbetekenis()` is puur (DB-vrij) en testbaar.

Nu: de eerste betekenis `technische_plaatsing` ("waar draait dit op"). Toekomstige
betekenissen (bv. contractuele dekking) landen hier eveneens. Voedt de engine NIET.
"""
from sqlalchemy.dialects.postgresql import insert as pg_insert

from models.models import VraagBetekenisOptie

_BETEKENISSEN: list[tuple[str, str]] = [
    ("technische_plaatsing", "Technische plaatsing (waar draait dit op)"),
]


def bouw_vraagbetekenis() -> list[dict]:
    """Puur (DB-vrij): geordende lijst optie-rijen. Deterministisch."""
    return [
        {"optie_sleutel": sleutel, "label": label, "volgorde": volgorde, "actief": True}
        for volgorde, (sleutel, label) in enumerate(_BETEKENISSEN)
    ]


async def seed_vraagbetekenis(session) -> int:
    """Zaai de default-catalogus (idempotent). Geeft het aantal optie-rijen terug."""
    rijen = bouw_vraagbetekenis()
    stmt = pg_insert(VraagBetekenisOptie).values(rijen).on_conflict_do_nothing(
        index_elements=["optie_sleutel"]
    )
    await session.execute(stmt)
    await session.commit()
    return len(rijen)
