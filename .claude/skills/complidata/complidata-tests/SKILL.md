---
name: complidata-tests
description: Test-patronen voor CompliData (pytest unit-tests + TST-validatiecyclus). Beschrijft de werkelijke V001-staat.
stack: pytest, asyncio, unittest.mock, SQLAlchemy models
bijgewerkt: V001
---

# CompliData Tests Skill

## conftest.py sys.path-patroon

```python
# modules/bwb_ontvlechting/backend/tests/conftest.py
import pathlib, sys
# tests/ -> backend/ -> bwb_ontvlechting/ -> modules/ -> repo-root = parents[4]
ROOT = pathlib.Path(__file__).resolve().parents[4]
for _p in (ROOT / "backend", ROOT / "modules" / "bwb_ontvlechting" / "backend"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
```

`backend/` levert `app.models.base`; de module-`backend/` levert de
top-level packages `models` en `services`.

## Import-conventie

```python
# Absolute imports — geen relative imports buiten een top-level package
from models.models import Applicatie, HostingModel
from services.seed import seed_checklist_vragen, CHECKLIST_VRAGEN
```

`models/` en `services/` hebben een `__init__.py`; `tests/` en de module-
`backend/` bewust NIET (voorkomt pytest package-mode-conflicten).

## Model-unit-test-patroon (geen DB nodig)

```python
def test_modellen_importeerbaar():
    from models import models as m
    for naam in ["Applicatie", "Datatype", "Gebruikersgroep", "Koppeling",
                 "ChecklistVraag", "Checklistscore", "Blokkade"]:
        assert hasattr(m, naam)

def test_enum_waarden():
    from models import models as m
    assert [e.value for e in m.HostingModel] == [
        "on_premise", "private_cloud", "saas", "iaas", "paas", "hybride", "onbekend"]
```

## Seed-test (asyncio.run — bewust géén pytest-asyncio)

De seed-functie is async maar wordt zonder DB getest via een `AsyncMock`.
`asyncio.run(...)` vermijdt een pytest-asyncio-afhankelijkheid.

```python
import asyncio
from unittest.mock import AsyncMock

def test_seed_codes_uniek_en_89():
    from services.seed import CHECKLIST_VRAGEN
    codes = [v["code"] for v in CHECKLIST_VRAGEN]
    assert len(codes) == 89 and len(set(codes)) == 89

def test_seed_geeft_89_terug():
    session = AsyncMock()
    assert asyncio.run(seed_checklist_vragen(session)) == 89
    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()

def test_seed_idempotent():
    session = AsyncMock()
    assert asyncio.run(seed_checklist_vragen(session)) == 89
    assert asyncio.run(seed_checklist_vragen(session)) == 89  # geen fout
```

De seed retourneert `len(CHECKLIST_VRAGEN)` (vast 89), niet `rowcount` —
daarom blijft de assertie ook bij de tweede (idempotente) run kloppen.

## TST-validatiecyclus (4 assen)

Bij elke sessie-afsluiting conform CONTRIBUTING.md sectie 6:

| As | Commando | Verwacht |
|---|---|---|
| 1 — py_compile | `find . -name "*.py" ... \| xargs python3 -m py_compile` | 0 fouten |
| 2 — pytest | `python3 -m pytest modules/.../tests/ -q` | alle tests groen |
| 3 — Alembic | `alembic heads` / `alembic branches` | 1 head, 0 branches |
| 4 — referentie-grep | grep op `backend/ frontend/src/ modules/ docs/adr/` | 0 hits |

Rapport opslaan als `docs/TST-{build_label}-Validatierapport.md`.
Eerst `python3 docs/_generators/sluit_acties.py` draaien (TST-rapport,
skills gevuld, NEXT_SESSION ingevuld, git clean).
