# CONTRIBUTING.md — CompliData

## Sectie 6 — TST-validatiecyclus

De TST-validatiecyclus wordt uitgevoerd bij elke sessie-afsluiting.
Resultaat: een TST-validatierapport opgeslagen in docs/ als
`TST-{build_label}-Validatierapport.md`.

### As 1 — Code-kwaliteit

- py_compile op alle Python-bestanden: 0 syntaxfouten
- Import-check: alle modules importeerbaar
- Geen hardcoded tenant-IDs, platform-namen of operator-referenties
- Geen localStorage-gebruik voor tokens
- Geen cd_admin in applicatie-code

```bash
find . -name "*.py" \
  ! -path "./node_modules/*" \
  ! -path "./.git/*" \
  ! -path "*/__pycache__/*" \
  | xargs python3 -m py_compile && echo "py_compile: OK"
```

### As 2 — Tests

- Alle unit-tests slagen
- Testdekking op nieuwe code aanwezig
- Geen gebroken imports in testbestanden

Draai vanaf de **repo-root** (tests staan in `backend/tests/` én
`modules/.../tests/`; `cd backend && pytest modules/` faalt omdat `modules/`
in de repo-root staat):

```bash
python3 -m pytest backend/tests/ modules/ -v --tb=short
```

### As 3 — Database-integriteit

- Alembic heads: exact 1 head per module
- Geen split branches: `alembic branches` leeg
- RLS aanwezig op alle tenant-scoped tabellen
- Geen migraties met down_revision conflicten

```bash
cd backend && python3 -m alembic heads
cd backend && python3 -m alembic branches
cd backend && python3 -m alembic upgrade head --sql | grep -c "ENABLE ROW LEVEL SECURITY"
```

### As 4 — Veiligheid en conventies

- Geen Eraneos-referenties in de repo
- Geen CompliMan-referenties (cm_, compliman) in de repo
- Alle complidata-skills gevuld (>200 bytes)
- CLAUDE.md bouwstatus actueel

```bash
grep -r "Eraneos\|compliman\|cm_" \
  backend/ frontend/src/ modules/ docs/adr/ \
  --include="*.py" --include="*.md" --include="*.js" --include="*.json" \
  2>/dev/null | wc -l
# Verwacht: 0
# Bewust uitgesloten: .claude/ (overgenomen framework-skills),
# docs/_generators/ (bevat de patronen zelf),
# docs/_skills/ (overgenomen skill-documentatie)
```

### TST-rapport format

Sla het rapport op als:
`docs/TST-{build_label}-Validatierapport.md`

Inhoud minimaal:
- Build label
- Datum
- Resultaat per as (geslaagd / gefaald)
- Aantal kritieken
- Geaccepteerde afwijkingen (indien van toepassing)
