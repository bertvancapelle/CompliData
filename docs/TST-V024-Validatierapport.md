# TST-V024 — Validatierapport

**Build:** V024 (→ V025 bij gen_build)
**Datum:** 2026-06-29
**Sessie:** LI024 (volledige prioriteitenlijst + UX-verbeteringen Landschapskaart)
**Teststatus:** backend 928 / frontend 745 groen (2 skipped)
**Kritieke bevindingen:** 0

---

## 1. py_compile
`backend/app/main.py` + alle `modules/bwb_ontvlechting/backend/**/*.py` → **OK**.

## 2. Backend pytest (`backend/tests/ modules/`)
**928 passed, 2 skipped, 1 warning** (≈19s). Geen failures.

## 3. Alembic
- `alembic heads` → **1 head**: `0043_adr030_contract_band_dekking`.
- `alembic branches` → **0 branches**.
- Migraties met `FORCE ROW LEVEL SECURITY`: **22** (incl. de nieuwe `contract_band_dekking`).

## 4. Verboden patronen (grep) — alle 0
- `localStorage` voor tokens: **0**
- Hardcoded `tenant_id = '...'` in query: **0**
- `NIST`-referenties: **0**
- `lk_admin` als app-connectie-string: **0** (de 12 treffers zijn comments/docstrings over het rolmodel + test-fixtures `_CD_ADMIN_URL`; geen app-code verbindt als lk_admin).

## 5. Frontend
- **vitest**: 65 test files, **745 passed**.
- **vite build**: exit 0 (built in ~0.4s).
- **test:css-build**: exit 0 (alle 6 kritische interactie-klassen aanwezig).

---

## Conclusie
Volledige validatiecyclus **groen**, **0 kritieke bevindingen**. Klaar voor build-bump V024 → V025.

### Geland in LI024 (samengevat)
ADR-035 Slice 1+2 (signalering), ADR-025 (Bekijk op kaart), ADR-030 (contract band-dekking, migratie 0043),
Landschapskaart-UX: interactieve/draggable legenda (dim), zoekresultaten in kaart-modus, fcose-layout,
positie-stabiele re-render, dubbele-node-fix, eigenaar-ring, draggable detail-popup, tagline-fix.
ADR-026 (ArchiMate-typering) en het klaarverklaring-blok bleken al gerealiseerd (geen bouw).
