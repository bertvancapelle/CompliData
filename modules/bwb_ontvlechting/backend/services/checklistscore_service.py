"""Service-laag voor de entiteit Checklistscore (ADR-009/013, Model A).

Naast de standaard tenant-bescherming (RLS + expliciete `tenant_id`-filter):
- ouder-`Applicatie` tenant-scoped valideren (→ 404);
- `vraag_code` valideren tegen de globale `ChecklistVraag`-set (→ 404);
- uniciteit (tenant, applicatie, vraag_code) afdwingen (→ 409, met
  `uq_checklistscore_app_vraag` als backstop);
- de invariant score↔blokkade handhaven (auto-blokkade, ADR-013 B2);
- na elke schrijf/verwijder `herbereken_lifecycle` aanroepen (ADR-013 B3).

`applicatie_id`/`vraag_code` zijn immutabel (niet in Update).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, tuple_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import (
    Blokkade,
    BlokkadeStatus,
    ChecklistScore,
    ChecklistVraag,
    Checklistscore,
)
from schemas.checklistscore import ChecklistscoreCreate, ChecklistscoreUpdate
from services import applicatie_service, lifecycle_service
from services.errors import ChecklistscoreConflict, NietGevonden
from services.pagination import decode_cursor, encode_cursor

_ENTITEIT = "checklistscore"
_STANDAARD_LIMIT = 25
_MAX_LIMIT = 100

# Scores die een actieve blokkade vereisen (ADR-013 B2).
_BLOKKADE_VEREIST = (ChecklistScore.nee, ChecklistScore.deels)
_BLOKKADE_ACTIEF = (BlokkadeStatus.open, BlokkadeStatus.in_behandeling)


def _tenant_uuid(tenant_id) -> uuid.UUID:
    return tenant_id if isinstance(tenant_id, uuid.UUID) else uuid.UUID(str(tenant_id))


def enum_opties() -> dict[str, list[str]]:
    """Read-only keuzewaarden voor de score (single source, DB-vrij)."""
    return {"score": [e.value for e in ChecklistScore]}


async def _valideer_vraag_code(session: AsyncSession, vraag_code: str) -> None:
    """Onbekende `vraag_code` (globale vragenset) ⇒ NietGevonden (404)."""
    bestaat = (
        await session.execute(
            select(ChecklistVraag.code).where(ChecklistVraag.code == vraag_code)
        )
    ).scalar_one_or_none()
    if bestaat is None:
        raise NietGevonden("checklistvraag", vraag_code)


def _is_blokkerend(score) -> bool:
    """Score die een blokkade rechtvaardigt (`nee`/`deels`)."""
    return score in _BLOKKADE_VEREIST


async def _synchroniseer_blokkade(
    session: AsyncSession, tid: uuid.UUID, score_obj, oude_score
) -> None:
    """Handhaaf de invariant score↔blokkade op basis van de TRANSITIE (ADR-013 B2).

    De auto-logica reageert uitsluitend op een score die de blokkerende grens
    kruist — nooit op een ongewijzigde of binnen-blokkerende score. Daardoor is
    "score `nee` + blokkade `opgelost`" een geldige, stabiele eindtoestand
    (geremedieerd → `migratieklaar`); een latere bewerking heropent niets.

    - `oude_score=None` ⇒ aanmaken: blokkerende score → nieuwe blokkade `open`.
    - regressie `ja`/`nvt` → `nee`/`deels`: geen actieve blokkade ⇒ maak `open`;
      alleen een `opgelost` exemplaar ⇒ heropen (`open`, `opgelost_op=null`).
    - correctie `nee`/`deels` → `ja`/`nvt`: actieve blokkade ⇒ auto-`opgelost`.
    - score ongewijzigd of binnen-blokkerend (`nee↔deels`, `ja↔nvt`): NIETS
      (handmatige blokkade-status, incl. `opgelost`, blijft ongemoeid).
    """
    nieuw_blokkerend = _is_blokkerend(score_obj.score)
    oud_blokkerend = _is_blokkerend(oude_score) if oude_score is not None else False

    # Geen kruising van de blokkerende grens ⇒ blokkade volledig ongemoeid.
    if oude_score is not None and nieuw_blokkerend == oud_blokkerend:
        return

    blok = (
        await session.execute(
            select(Blokkade).where(Blokkade.checklistscore_id == score_obj.id)
        )
    ).scalar_one_or_none()

    if nieuw_blokkerend and not oud_blokkerend:
        # Aanmaken met blokkerende score, of regressie ja/nvt → nee/deels.
        if blok is None:
            session.add(
                Blokkade(
                    tenant_id=tid,
                    checklistscore_id=score_obj.id,
                    applicatie_id=score_obj.applicatie_id,
                    status=BlokkadeStatus.open,
                )
            )
        elif blok.status == BlokkadeStatus.opgelost:
            blok.status = BlokkadeStatus.open
            blok.opgelost_op = None
        # open/in_behandeling → ongemoeid
    elif oud_blokkerend and not nieuw_blokkerend:
        # Score-correctie nee/deels → ja/nvt: actieve blokkade auto-oplossen.
        if blok is not None and blok.status in _BLOKKADE_ACTIEF:
            blok.status = BlokkadeStatus.opgelost
            blok.opgelost_op = datetime.now(timezone.utc)

    await session.flush()


async def lijst(
    session: AsyncSession,
    tenant_id,
    *,
    limit: int = _STANDAARD_LIMIT,
    after: str | None = None,
    applicatie_id: uuid.UUID | None = None,
) -> tuple[list[Checklistscore], str | None]:
    limit = max(1, min(limit, _MAX_LIMIT))
    tid = _tenant_uuid(tenant_id)

    stmt = select(Checklistscore).where(Checklistscore.tenant_id == tid)
    if applicatie_id is not None:
        stmt = stmt.where(Checklistscore.applicatie_id == applicatie_id)
    if after:
        cursor_created_at, cursor_id = decode_cursor(after)
        stmt = stmt.where(
            tuple_(Checklistscore.created_at, Checklistscore.id)
            > (cursor_created_at, cursor_id)
        )
    stmt = stmt.order_by(Checklistscore.created_at, Checklistscore.id).limit(limit + 1)

    rijen = list((await session.execute(stmt)).scalars().all())
    heeft_meer = len(rijen) > limit
    items = rijen[:limit]
    volgende = encode_cursor(items[-1]) if heeft_meer else None
    return items, volgende


async def haal_op(session: AsyncSession, tenant_id, checklistscore_id) -> Checklistscore:
    tid = _tenant_uuid(tenant_id)
    stmt = select(Checklistscore).where(
        Checklistscore.id == checklistscore_id,
        Checklistscore.tenant_id == tid,
    )
    obj = (await session.execute(stmt)).scalar_one_or_none()
    if obj is None:
        raise NietGevonden(_ENTITEIT, checklistscore_id)
    return obj


async def maak_aan(
    session: AsyncSession, tenant_id, data: ChecklistscoreCreate
) -> Checklistscore:
    tid = _tenant_uuid(tenant_id)
    # Ouder + vraag_code valideren (beide tenant-/referentie-scoped) → 404.
    await applicatie_service.haal_op(session, tenant_id, data.applicatie_id)
    await _valideer_vraag_code(session, data.vraag_code)

    # Uniciteit up-front (tenant, applicatie, vraag_code) → 409.
    bestaat = (
        await session.execute(
            select(Checklistscore.id).where(
                Checklistscore.tenant_id == tid,
                Checklistscore.applicatie_id == data.applicatie_id,
                Checklistscore.vraag_code == data.vraag_code,
            )
        )
    ).scalar_one_or_none()
    if bestaat is not None:
        raise ChecklistscoreConflict()

    obj = Checklistscore(tenant_id=tid, **data.model_dump())
    session.add(obj)
    try:
        await session.flush()  # id toekennen + unieke index als backstop
    except IntegrityError as exc:
        await session.rollback()
        raise ChecklistscoreConflict() from exc

    await _synchroniseer_blokkade(session, tid, obj, oude_score=None)
    await lifecycle_service.herbereken_lifecycle(session, tid, obj.applicatie_id)
    await session.commit()
    await session.refresh(obj)
    return obj


async def werk_bij(
    session: AsyncSession, tenant_id, checklistscore_id, data: ChecklistscoreUpdate
) -> Checklistscore:
    tid = _tenant_uuid(tenant_id)
    obj = await haal_op(session, tenant_id, checklistscore_id)
    oude_score = obj.score  # vóór de update — bepaalt de transitie
    for veld, waarde in data.model_dump(exclude_unset=True).items():
        setattr(obj, veld, waarde)
    await session.flush()

    await _synchroniseer_blokkade(session, tid, obj, oude_score)
    await lifecycle_service.herbereken_lifecycle(session, tid, obj.applicatie_id)
    await session.commit()
    await session.refresh(obj)
    return obj


async def verwijder(session: AsyncSession, tenant_id, checklistscore_id) -> None:
    tid = _tenant_uuid(tenant_id)
    obj = await haal_op(session, tenant_id, checklistscore_id)
    applicatie_id = obj.applicatie_id
    await session.delete(obj)  # 1-op-1 blokkade gaat mee via ON DELETE CASCADE
    await session.flush()
    await lifecycle_service.herbereken_lifecycle(session, tid, applicatie_id)
    await session.commit()
