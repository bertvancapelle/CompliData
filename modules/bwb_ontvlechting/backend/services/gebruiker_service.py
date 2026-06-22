"""Service-laag — gebruikersbeheer (ADR-029 Fase 2).

LIKARA is de primaire ingang voor gebruikers: aanmaken maakt in één reeks een persoon-partij
(ADR-024) + een Keycloak-account (Admin API) + de koppelrij `gebruiker_persoon`. De koppeling
`keycloak_sub <-> persoon_id` ontstaat bij aanmaak.

ENGINE-INVARIANT: dit raakt de score-/lifecycle-engine NIET. Importeert bewust géén
`lifecycle_service`/`herbereken_lifecycle`/`bepaal_lifecycle`/`ComponentProfiel`/`Blokkade`/
`Checklistscore`. Puur registratief + provisioning.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import keycloak
from models.models import GebruikerPersoon, Partij
from schemas.gebruiker import GebruikerPersoonRead
from services import partij_service
from services.errors import KeycloakNietBeschikbaar, OngeldigeRegistratie
from services.pagination import (
    decode_sort_cursor_nullable,
    encode_sort_cursor_nullable,
    keyset_order_by_nulls_last,
    keyset_seek_nulls_last,
)

_LIMIET = 25
_MAX_LIMIET = 100


def _tenant_uuid(tenant_id) -> uuid.UUID:
    return tenant_id if isinstance(tenant_id, uuid.UUID) else uuid.UUID(str(tenant_id))


def _lees(rij: GebruikerPersoon, persoon: Partij) -> GebruikerPersoonRead:
    return GebruikerPersoonRead(
        id=rij.id, keycloak_sub=rij.keycloak_sub, persoon_id=rij.persoon_id,
        naam=persoon.naam, email=persoon.email, aangemaakt_op=rij.aangemaakt_op,
    )


async def maak_gebruiker(
    session: AsyncSession, tenant_id, *, naam: str, email: str,
    afdeling_id: uuid.UUID | None, functietitel: str | None, rol: str,
) -> tuple[GebruikerPersoonRead, str]:
    """Maak een gebruiker aan (persoon + Keycloak-account + koppelrij).

    Retourneert (read-object, tijdelijk_wachtwoord) — het wachtwoord is uitsluitend voor de
    eenmalige 201-respons. Flow met transactionele veiligheid:
      1. email niet al gekoppeld binnen de tenant → anders 422 EMAIL_AL_IN_GEBRUIK.
      2. persoon-partij aanmaken (flush, géén commit) via partij_service.
      3. Keycloak-account aanmaken; faalt dit → rollback (niets in KC of create faalde) → 503.
      4. koppelrij gebruiker_persoon aanmaken (sub uit stap 3).
      5. commit; faalt dit → best-effort KC-account deactiveren (orphan-cleanup) → 503.
    """
    tid = _tenant_uuid(tenant_id)

    # 1. Email mag nog niet aan een gekoppelde gebruiker hangen (join koppelrij <-> persoon).
    bestaat = (
        await session.execute(
            select(GebruikerPersoon.id)
            .join(Partij, Partij.id == GebruikerPersoon.persoon_id)
            .where(GebruikerPersoon.tenant_id == tid, Partij.email == email)
        )
    ).scalar_one_or_none()
    if bestaat is not None:
        raise OngeldigeRegistratie("EMAIL_AL_IN_GEBRUIK", "Er bestaat al een gebruiker met dit e-mailadres.")

    # 2. Persoon-partij aanmaken (flush, geen commit).
    persoon = await partij_service.maak_persoon_flush(
        session, tid, naam=naam, email=email, afdeling_id=afdeling_id, functietitel=functietitel,
    )

    # 3. Keycloak-account aanmaken; bij fout: rollback (geen orphan — create faalde of niets gemaakt).
    wachtwoord = keycloak.genereer_tijdelijk_wachtwoord()
    try:
        sub = await keycloak.maak_keycloak_gebruiker(email=email, naam=naam, tijdelijk_wachtwoord=wachtwoord, rol=rol)
    except keycloak.KeycloakProvisioningFout as exc:
        await session.rollback()
        raise KeycloakNietBeschikbaar(f"Aanmaken Keycloak-account mislukt: {exc.bericht}") from exc

    # 4. Koppelrij.
    koppel = GebruikerPersoon(tenant_id=tid, keycloak_sub=sub, persoon_id=persoon.id)
    session.add(koppel)

    # 5. Commit; faalt dit dan bestaat het KC-account al → best-effort deactiveren (orphan-cleanup).
    try:
        await session.commit()
    except Exception as exc:
        await session.rollback()
        await keycloak.deactiveer_keycloak_gebruiker(sub)
        raise KeycloakNietBeschikbaar("Opslaan van de gebruiker mislukt; het account is gedeactiveerd.") from exc

    await session.refresh(koppel)
    await session.refresh(persoon)
    return _lees(koppel, persoon), wachtwoord


async def lijst_gebruikers(
    session: AsyncSession, tenant_id, *, limit: int = _LIMIET, after: str | None = None,
) -> tuple[list[GebruikerPersoonRead], str | None]:
    """Gekoppelde gebruikers (join koppelrij <-> persoon), gesorteerd op naam; v2n-keyset."""
    tid = _tenant_uuid(tenant_id)
    limit = max(1, min(limit, _MAX_LIMIET))
    kolom = Partij.naam

    stmt = (
        select(GebruikerPersoon, Partij.naam, Partij.email)
        .join(Partij, Partij.id == GebruikerPersoon.persoon_id)
        .where(GebruikerPersoon.tenant_id == tid)
    )
    if after:
        c_sort, c_order, c_isnull, c_waarde, c_id = decode_sort_cursor_nullable(after)
        if c_sort != "naam" or c_order != "asc":
            raise ValueError("cursor past niet bij de sortering")
        stmt = stmt.where(
            keyset_seek_nulls_last(
                kolom, GebruikerPersoon.id, order="asc", is_null=c_isnull, waarde=c_waarde, cursor_id=c_id
            )
        )
    stmt = stmt.order_by(*keyset_order_by_nulls_last(kolom, GebruikerPersoon.id, "asc")).limit(limit + 1)

    rijen = (await session.execute(stmt)).all()
    meer = len(rijen) > limit
    rijen = rijen[:limit]
    items = [
        GebruikerPersoonRead(
            id=gp.id, keycloak_sub=gp.keycloak_sub, persoon_id=gp.persoon_id,
            naam=naam, email=email, aangemaakt_op=gp.aangemaakt_op,
        )
        for gp, naam, email in rijen
    ]
    volgende = None
    if meer and items:
        laatste_gp, laatste_naam, _ = rijen[-1]
        volgende = encode_sort_cursor_nullable(sort="naam", order="asc", waarde=laatste_naam, id=str(laatste_gp.id))
    return items, volgende
