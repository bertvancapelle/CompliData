# LIKARA — Projectgeheugen

> Repo-gebundeld projectgeheugen. Bijwerken bij **elke** sessie-afsluiting **vóór**
> `gen_build.py`, zodat het automatisch in de sessie-ZIP wordt meegenomen
> (`gen_sessiestart.py` globt `docs/*.md`). Spiegel hierna de claude.ai-memory.

## Bouwstand
- **Build:** V026 · 2026-06-30
- **Commit:** 74966b7 (sessie-afsluiting LI051)
- **Tests:** backend 931 / 2 skipped / 0 failed · frontend 745 groen (65 files) · 0 kritieken
- **Migratie-head:** `0044_lk_audit_append_only`
- **TST-rapport:** `docs/TST-V026-Validatierapport.md`

## Deze sessie (LI038–LI051)
Code-rebrand `cd_`/`complidata`/`CompliData`/`CompliMan` → `lk`/`likara`/`LIKARA` **compleet**:
- Skills/docs/generators (LI038–LI042) + alle gedragsbepalende identifiers in slices S1–S8:
  cosmetische namen + role-prefix, CSS-tokens `--lk-`, cookies `lk_session`/`lk_refresh`,
  env `LIKARA_TEST_MODE`/`LIKARA_FIXTURE_SET`, localStorage `lk-sidebar-ingeklapt` +
  backup-basisnaam `likara_*.sql`, infra (`lk_rabbit`, vhost `lk-{slug}`, MinIO `likara_admin`,
  paden `~/likara/`), DB-triggerfunctie `lk_audit_append_only`.
- **Deploy-blocker verholpen** (LI049): migratie-revisie-id ≤32 tekens, geborgd met een
  handhavingstest over **beide** migratiebomen (`backend/alembic` + `modules/**/migrations`).
- **Audit-triggerfunctie hernoemd** (LI050, forward-migratie 0044): append-only LIVE bewezen
  (UPDATE/DELETE geweigerd), ADR-006 hash-keten intact.
- Geen `cd_`/`complidata` meer in live code/config/schema; **historie bewust behouden** in
  migratie `0010` + `docs/OPVOLGPUNTEN.md` + `docs/changelog/`.

## Top-5 prioriteiten volgende sessie (LI052)
1. ADR-035 Slice 3 — registratie onvolledig (configureerbare score-drempelwaarde)
2. Modus ego→impact ontkoppelen van set-grootte (ADR-033-revisie)
3. GebruikersgroepDetail — standalone pagina
4. BlokkadeDetail — standalone pagina
5. Zoekbalk contextlabel "Component toevoegen aan beeld" (kaart-modus)

## Resterend uit de rebrand (geen code)
- **DC013** — GitHub-repo/remote `bertvancapelle/CompliData` → LIKARA + remote-URL; lokale
  map `~/complidata/` opruimen (stack draait op `~/likara/`). Berts GitHub-actie.
- **Deploy-side** — andere omgevingen: `.env`/secrets bijwerken (`RABBITMQ_URL`→`lk_rabbit`,
  `MINIO_ROOT_USER`→`likara_admin`, cookie-/env-namen) + re-provision.
- **OP-30** — env-test-robuustheid: `test_callback_succes_zet_lk_session_cookie` laat
  `cookie_secure` van de omgeving afhangen; expliciet zetten.
- **Procesgat secrets-backup** — `~/likara/secrets/` gedocumenteerd maar feitelijk nooit gevuld → verzoenen.

> Volledige backlog: `docs/OPVOLGPUNTEN.md` (enige bron).
