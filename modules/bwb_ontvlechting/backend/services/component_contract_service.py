"""Service-laag voor ComponentContract (ADR-021 Besluit 7 — Fase B).

Component-breed (élk component, niet alleen applicaties). Component + contract tenant-scoped
resolven (404); `relatie_rol` tegen de actieve catalogus-dimensie `relatie_rol`; dubbele
`(component, contract)` ⇒ 409 `KOPPELING_BESTAAT`. Gedrag identiek aan ApplicatieContract;
alleen de validatie loopt via `component_service` (kale infra mag contracten dragen).
"""
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import (
    ComponentContract,
    Contract,
    ContractConfigDimensie,
    Leverancier,
)
from schemas.component_contract import ComponentContractCreate, ComponentContractUpdate
from services import component_service, contract_service
from services import contractconfig_catalog as catalog
from services.errors import NietGevonden, RegistratieConflict

_ENTITEIT = "component_contract"


def _tenant_uuid(tenant_id) -> uuid.UUID:
    return tenant_id if isinstance(tenant_id, uuid.UUID) else uuid.UUID(str(tenant_id))


async def haal_op(session: AsyncSession, tenant_id, koppeling_id) -> ComponentContract:
    tid = _tenant_uuid(tenant_id)
    obj = (
        await session.execute(
            select(ComponentContract).where(
                ComponentContract.id == koppeling_id, ComponentContract.tenant_id == tid
            )
        )
    ).scalar_one_or_none()
    if obj is None:
        raise NietGevonden(_ENTITEIT, koppeling_id)
    return obj


async def _lees(session: AsyncSession, obj: ComponentContract) -> dict:
    rol_labels = await catalog.labels(session, ContractConfigDimensie.relatie_rol)
    return {
        "id": obj.id,
        "component_id": obj.component_id,
        "contract_id": obj.contract_id,
        "relatie_rol": obj.relatie_rol,
        "relatie_rol_label": catalog.resolveer_een(obj.relatie_rol, rol_labels),
        "created_at": obj.created_at,
        "updated_at": obj.updated_at,
    }


async def maak_aan(session: AsyncSession, tenant_id, data: ComponentContractCreate) -> dict:
    tid = _tenant_uuid(tenant_id)
    await component_service.haal_op(session, tenant_id, data.component_id)  # élk type, 404 buiten tenant
    await contract_service.haal_op(session, tenant_id, data.contract_id)
    await catalog.valideer_sleutels(session, ContractConfigDimensie.relatie_rol, [data.relatie_rol])

    bestaat = (
        await session.execute(
            select(ComponentContract.id).where(
                ComponentContract.tenant_id == tid,
                ComponentContract.component_id == data.component_id,
                ComponentContract.contract_id == data.contract_id,
            )
        )
    ).scalar_one_or_none()
    if bestaat is not None:
        raise RegistratieConflict("KOPPELING_BESTAAT", "Dit component is al aan dit contract gekoppeld.")

    obj = ComponentContract(
        tenant_id=tid, component_id=data.component_id, contract_id=data.contract_id,
        relatie_rol=data.relatie_rol,
    )
    session.add(obj)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise RegistratieConflict("KOPPELING_BESTAAT", "Dit component is al aan dit contract gekoppeld.") from exc
    await session.refresh(obj)
    return await _lees(session, obj)


async def werk_bij(session: AsyncSession, tenant_id, koppeling_id, data: ComponentContractUpdate) -> dict:
    obj = await haal_op(session, tenant_id, koppeling_id)
    await catalog.valideer_sleutels(session, ContractConfigDimensie.relatie_rol, [data.relatie_rol])
    obj.relatie_rol = data.relatie_rol
    await session.commit()
    await session.refresh(obj)
    return await _lees(session, obj)


async def verwijder(session: AsyncSession, tenant_id, koppeling_id) -> None:
    obj = await haal_op(session, tenant_id, koppeling_id)
    await session.delete(obj)
    await session.commit()


async def contracten_van_component(session: AsyncSession, tenant_id, component_id) -> list[dict]:
    """'Component → contracten': gekoppelde contracten (met rol + leverancier).
    Component onbekend ⇒ 404."""
    tid = _tenant_uuid(tenant_id)
    await component_service.haal_op(session, tenant_id, component_id)
    rol_labels = await catalog.labels(session, ContractConfigDimensie.relatie_rol)
    rijen = (
        await session.execute(
            select(
                ComponentContract.id.label("koppeling_id"),
                Contract.id.label("contract_id"),
                Contract.contractnaam.label("contractnaam"),
                Contract.contracttype.label("contracttype"),
                Contract.leverancier_id.label("leverancier_id"),
                Leverancier.naam.label("leverancier_naam"),
                Contract.begindatum.label("begindatum"),
                Contract.einddatum.label("einddatum"),
                ComponentContract.relatie_rol.label("relatie_rol"),
            )
            .join(Contract, Contract.id == ComponentContract.contract_id)
            .join(Leverancier, Leverancier.id == Contract.leverancier_id)
            .where(ComponentContract.tenant_id == tid, ComponentContract.component_id == component_id)
            .order_by(Contract.contractnaam, ComponentContract.id)
        )
    ).all()
    return [
        {
            "koppeling_id": r.koppeling_id, "contract_id": r.contract_id,
            "contractnaam": r.contractnaam, "contracttype": r.contracttype,
            "leverancier_id": r.leverancier_id, "leverancier_naam": r.leverancier_naam,
            "begindatum": r.begindatum, "einddatum": r.einddatum,
            "relatie_rol": r.relatie_rol,
            "relatie_rol_label": catalog.resolveer_een(r.relatie_rol, rol_labels),
        }
        for r in rijen
    ]
