"""Service-laag — opgeslagen & deelbare Impact-verkenner-views (ADR-033 slice 2).

Een opgeslagen view is een bewaarde startselectie (naam + componenten) voor de Impact-verkenner.
Tenant-scoped (RLS + expliciet `tenant_id`-filter). Bovenop RLS leeft hier de **maker-laag**:

- de maker wordt server-side gestempeld (Keycloak-`sub` + e-mail-fallback, nooit client-aanleverbaar);
- **lijst** = eigen views + gedeelde views van anderen (`maker_sub = :sub OR gedeeld`);
- **ophalen/gebruik** = alleen als `gedeeld OR maker_sub = :sub`, anders 404 (andermans privé-view
  lekt niet eens z'n bestaan);
- **bewerken/verwijderen** = alleen de maker (anders 404, zelfde no-leak).

Driedeling: RLS = tenant-grens · RBAC = welke rollen views mogen beheren · deze servicelaag = welke
views júíst deze maker ziet/muteert.

Puur registratief — RAAKT DE ENGINE NOOIT: importeert géén `lifecycle_service`/`herbereken_lifecycle`/
`bepaal_lifecycle`/`ComponentProfiel`/`Blokkade`/`Checklistscore` en raakt geen lifecycle-/score-/
blokkade-state.
"""
import uuid

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant_context import huidige_actor
from models.models import Component, ImpactView, ImpactViewComponent
from schemas.impact_view import ImpactViewCreate, ImpactViewUpdate
from services import actor_resolutie
from services.errors import NietGevonden, RegistratieConflict

_ENTITEIT = "impact_view"


def _tenant_uuid(tenant_id) -> uuid.UUID:
    return tenant_id if isinstance(tenant_id, uuid.UUID) else uuid.UUID(str(tenant_id))


def _huidige_sub() -> str | None:
    """De stabiele Keycloak-sub van de huidige request (server-side; nooit client-aanleverbaar)."""
    sub, _email = huidige_actor()
    return sub


async def _componenten_bestaan(session: AsyncSession, tid: uuid.UUID, ids: list[uuid.UUID]) -> None:
    """Elk component bestaat binnen de tenant; een onbekende ⇒ 404 (geen lek)."""
    gevonden = set(
        (
            await session.execute(
                select(Component.id).where(Component.id.in_(ids), Component.tenant_id == tid)
            )
        )
        .scalars()
        .all()
    )
    for cid in ids:
        if cid not in gevonden:
            raise NietGevonden("component", cid)


async def _selectie(session: AsyncSession, tid: uuid.UUID, view_ids: list[uuid.UUID]) -> dict[uuid.UUID, list[uuid.UUID]]:
    """Component-ids per view (één query; deterministisch geordend op component_id)."""
    if not view_ids:
        return {}
    rijen = (
        await session.execute(
            select(ImpactViewComponent.view_id, ImpactViewComponent.component_id)
            .where(ImpactViewComponent.tenant_id == tid, ImpactViewComponent.view_id.in_(view_ids))
            .order_by(ImpactViewComponent.component_id)
        )
    ).all()
    uit: dict[uuid.UUID, list[uuid.UUID]] = {vid: [] for vid in view_ids}
    for view_id, component_id in rijen:
        uit.setdefault(view_id, []).append(component_id)
    return uit


def _verrijk(obj: ImpactView, *, component_ids: list[uuid.UUID], maker_naam: str | None, sub: str | None) -> ImpactView:
    """Transiente read-velden zetten (zoals het `verklaard_door_naam`-patroon)."""
    obj.component_ids = component_ids
    obj.maker_naam = maker_naam
    obj.is_eigenaar = bool(sub) and obj.maker_sub == sub
    return obj


async def _verrijk_een(session: AsyncSession, tid: uuid.UUID, obj: ImpactView) -> ImpactView:
    sub = _huidige_sub()
    sel = await _selectie(session, tid, [obj.id])
    naam = await actor_resolutie.resolveer_naam(session, tid, sub=obj.maker_sub, email=obj.maker_email)
    return _verrijk(obj, component_ids=sel.get(obj.id, []), maker_naam=naam, sub=sub)


async def _zet_selectie(session: AsyncSession, tid: uuid.UUID, view_id: uuid.UUID, component_ids: list[uuid.UUID]) -> None:
    """Vervang de selectie van een view (delete + insert) binnen de lopende transactie."""
    await session.execute(
        delete(ImpactViewComponent).where(
            ImpactViewComponent.tenant_id == tid, ImpactViewComponent.view_id == view_id
        )
    )
    for cid in component_ids:
        session.add(ImpactViewComponent(tenant_id=tid, view_id=view_id, component_id=cid))


async def maak_aan(session: AsyncSession, tenant_id, data: ImpactViewCreate) -> ImpactView:
    tid = _tenant_uuid(tenant_id)
    await _componenten_bestaan(session, tid, data.component_ids)
    sub, email = huidige_actor()
    obj = ImpactView(tenant_id=tid, naam=data.naam, maker_sub=sub, maker_email=email, gedeeld=data.gedeeld)
    session.add(obj)
    try:
        await session.flush()  # view-id beschikbaar vóór de junctie-inserts
        await _zet_selectie(session, tid, obj.id, data.component_ids)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise RegistratieConflict(
            "VIEW_NAAM_BESTAAT_AL",
            "Je hebt al een opgeslagen view met deze naam; kies een andere naam.",
        )
    await session.refresh(obj)
    return await _verrijk_een(session, tid, obj)


async def lijst(session: AsyncSession, tenant_id) -> list[ImpactView]:
    """Eigen views + gedeelde views van anderen (binnen de tenant-RLS-scope).

    Bewust géén keyset-paginering: een begrensde persoonlijke lijst, niet de generieke lijst-norm.
    """
    tid = _tenant_uuid(tenant_id)
    sub = _huidige_sub()
    stmt = select(ImpactView).where(ImpactView.tenant_id == tid)
    # Eigen + gedeeld. Zonder bekende sub (defensief): alleen gedeelde views.
    if sub:
        stmt = stmt.where((ImpactView.maker_sub == sub) | (ImpactView.gedeeld.is_(True)))
    else:
        stmt = stmt.where(ImpactView.gedeeld.is_(True))
    stmt = stmt.order_by(ImpactView.naam)
    rijen = list((await session.execute(stmt)).scalars().all())
    sel = await _selectie(session, tid, [r.id for r in rijen])
    naam_map = await actor_resolutie.resolveer_namen(session, tid, {r.maker_sub for r in rijen})
    for r in rijen:
        _verrijk(
            r,
            component_ids=sel.get(r.id, []),
            maker_naam=naam_map.get(r.maker_sub) or r.maker_email,
            sub=sub,
        )
    return rijen


async def haal_op(session: AsyncSession, tenant_id, view_id) -> ImpactView:
    """Eén view, alleen zichtbaar als gedeeld OF eigen; anders 404 (no-leak)."""
    tid = _tenant_uuid(tenant_id)
    obj = (
        await session.execute(
            select(ImpactView).where(ImpactView.id == view_id, ImpactView.tenant_id == tid)
        )
    ).scalar_one_or_none()
    if obj is None or not (obj.gedeeld or obj.maker_sub == _huidige_sub()):
        raise NietGevonden(_ENTITEIT, view_id)
    return await _verrijk_een(session, tid, obj)


async def _haal_eigen(session: AsyncSession, tid: uuid.UUID, view_id) -> ImpactView:
    """Een view die de huidige gebruiker mag muteren (de maker); anders 404 (no-leak)."""
    obj = (
        await session.execute(
            select(ImpactView).where(ImpactView.id == view_id, ImpactView.tenant_id == tid)
        )
    ).scalar_one_or_none()
    if obj is None or obj.maker_sub != _huidige_sub() or _huidige_sub() is None:
        raise NietGevonden(_ENTITEIT, view_id)
    return obj


async def werk_bij(session: AsyncSession, tenant_id, view_id, data: ImpactViewUpdate) -> ImpactView:
    """Naam/selectie/gedeeld wijzigen — uitsluitend door de maker."""
    tid = _tenant_uuid(tenant_id)
    obj = await _haal_eigen(session, tid, view_id)
    velden = data.model_dump(exclude_unset=True)
    if "naam" in velden:
        obj.naam = velden["naam"]
    if "gedeeld" in velden:
        obj.gedeeld = velden["gedeeld"]
    if data.component_ids is not None:
        await _componenten_bestaan(session, tid, data.component_ids)
        await _zet_selectie(session, tid, obj.id, data.component_ids)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise RegistratieConflict(
            "VIEW_NAAM_BESTAAT_AL",
            "Je hebt al een opgeslagen view met deze naam; kies een andere naam.",
        )
    await session.refresh(obj)
    return await _verrijk_een(session, tid, obj)


async def verwijder(session: AsyncSession, tenant_id, view_id) -> None:
    """Een view verwijderen — uitsluitend door de maker. De junctie cascadeert mee (DB)."""
    tid = _tenant_uuid(tenant_id)
    obj = await _haal_eigen(session, tid, view_id)
    await session.delete(obj)
    await session.commit()
