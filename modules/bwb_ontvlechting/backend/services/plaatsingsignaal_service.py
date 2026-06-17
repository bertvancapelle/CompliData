"""Service-laag — consistentie-signalering technische plaatsing (ADR-023 Fase F / F-3 stap 2).

Eén read die per checklist-dragend component een **zacht signaal** afleidt waar het
checklist-antwoord over technische plaatsing níét overeenkomt met het bestaan van een
`draait_op`-relatie. Geen fout, blokkeert niets — louter een attentiepunt.

Scope volgt uit de **markering** (F-3 stap 1), niet uit een vaste componenttype-regel:
in scope is elk component waarvan de checklist (binnen zijn componenttype) een vraag met
betekenis `technische_plaatsing` draagt. Generiek over componenttypen.

Signaal-afleiding (read-only, uit score × draait_op):
- positief = score in {ja, deels}; niet-positief/ongescoord = {nee, nvt, geen score};
- `draait_op` = ≥1 `assignment`-relatie met dit component als **doel** (host→gehoste =
  bron→doel; oriëntatie zoals in `component_service.structuur_overzicht`);
- **beoordeeld_niet_vastgelegd:** positief én GEEN draait_op;
- **vastgelegd_niet_beoordeeld:** draait_op én niet-positief/ongescoord.

Puur read-only, afgeleid — geen schema/migratie. Engine onaangeroerd: bewust GEEN import
van lifecycle/profiel/blokkade en geen mutatie van score (alleen SELECT). RLS scoopt op
de tenant.
"""
import uuid

from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Checklistscore, ChecklistVraag, Component, Relatie

_POSITIEF = {"ja", "deels"}
_BETEKENIS_PLAATSING = "technische_plaatsing"

# Leesbare reden per signaaltype (geen jargon in de uiteindelijke UI; hier de feitelijke grond).
_REDEN = {
    "beoordeeld_niet_vastgelegd": (
        "De plaatsingsvraag is positief beoordeeld, maar er is geen draait_op-relatie vastgelegd."
    ),
    "vastgelegd_niet_beoordeeld": (
        "Er is een draait_op-relatie vastgelegd, maar de plaatsingsvraag is niet positief beoordeeld."
    ),
}


def _tenant_uuid(tenant_id) -> uuid.UUID:
    return tenant_id if isinstance(tenant_id, uuid.UUID) else uuid.UUID(str(tenant_id))


def _score_value(score) -> str | None:
    if score is None:
        return None
    return score.value if hasattr(score, "value") else str(score)


def _signaal(score_val: str | None, draait_op: bool) -> str | None:
    positief = score_val in _POSITIEF
    if positief and not draait_op:
        return "beoordeeld_niet_vastgelegd"
    if draait_op and not positief:
        return "vastgelegd_niet_beoordeeld"
    return None


async def lijst(session: AsyncSession, tenant_id) -> list[dict]:
    """Alle componenten mét een plaatsingssignaal (+ signaaltype + leesbare reden).
    Gesorteerd op componenttype, naam. Read-only — geen mutatie, engine onaangeroerd."""
    tid = _tenant_uuid(tenant_id)

    # In scope: component ⋈ de technische_plaatsing-vraag van zijn componenttype (INNER).
    # Score: LEFT JOIN (ongescoord = NULL). draait_op: EXISTS assignment met doel=component.
    draait_op_expr = exists(
        select(Relatie.id).where(
            Relatie.tenant_id == tid,
            Relatie.relatietype == "assignment",
            Relatie.doel_id == Component.id,
        )
    )
    stmt = (
        select(
            Component.id,
            Component.naam,
            Component.componenttype,
            Checklistscore.score,
            draait_op_expr.label("draait_op"),
        )
        .join(
            ChecklistVraag,
            and_(
                ChecklistVraag.tenant_id == tid,
                ChecklistVraag.componenttype == Component.componenttype,
                ChecklistVraag.betekenis == _BETEKENIS_PLAATSING,
            ),
        )
        .outerjoin(
            Checklistscore,
            and_(
                Checklistscore.tenant_id == tid,
                Checklistscore.component_id == Component.id,
                Checklistscore.checklistvraag_id == ChecklistVraag.id,
            ),
        )
        .where(Component.tenant_id == tid)
        .order_by(Component.componenttype.asc(), Component.naam.asc(), Component.id.asc())
    )

    rijen = (await session.execute(stmt)).all()
    items: list[dict] = []
    for r in rijen:
        score_val = _score_value(r.score)
        signaal = _signaal(score_val, bool(r.draait_op))
        if signaal is None:
            continue
        items.append({
            "component_id": r.id,
            "naam": r.naam,
            "componenttype": r.componenttype,
            "signaal": signaal,
            "score": score_val,
            "draait_op": bool(r.draait_op),
            "reden": _REDEN[signaal],
        })
    return items
