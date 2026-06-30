"""Anti-divergentie-borging voor de likara-skillset (gate, structureel).

Drie bronnen moeten één blijven:
  1. de likara-skills op disk (.claude/skills/likara/*/SKILL.md),
  2. de afgeleide bron die de generators consumeren (skills_bron.likara_skill_paden),
  3. de likara-* lijst die CLAUDE.md in 'Normale modus' voorschrijft.

Aanleiding: gen_sessiestart.py (CURATED_SKILLS) en gen_build.py (REQUIRED_SKILLS)
hadden hardgecodeerde lijsten die achterliepen op CLAUDE.md, waardoor de borgende
skills (likara-werkprotocol, -ux, -domeinmodel) buiten de sessie-ZIP vielen.

De test laadt skills_bron via importlib van pad (geen import-side-effects) en
draait zonder DB. De 'bijt'-test bewijst met tijdelijke fixtures dat een mismatch
hard faalt — zonder de echte repo-bestanden aan te raken.
"""
import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
GEN = REPO / "docs" / "_generators"


def _laad_skills_bron():
    spec = importlib.util.spec_from_file_location("skills_bron", GEN / "skills_bron.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Live borging tegen de echte repo ─────────────────────────────────────────

def test_disk_glob_gelijk_aan_claude_md_normale_modus():
    """De likara-skills op disk MOETEN exact gelijk zijn aan wat CLAUDE.md in
    normale modus laat inlezen. Divergentie => duidelijke verschilset."""
    sb = _laad_skills_bron()

    op_disk = set(sb.likara_skill_namen())
    in_claude = set(sb.claude_md_likara_skillnamen())

    assert op_disk == in_claude, (
        "likara-skillset divergeert tussen disk en CLAUDE.md normale modus.\n"
        f"  alleen op disk:      {sorted(op_disk - in_claude)}\n"
        f"  alleen in CLAUDE.md: {sorted(in_claude - op_disk)}"
    )


def test_afgeleide_paden_dekken_elke_disk_skill():
    """De afgeleide bron (die generators consumeren) bevat elke likara-skill van
    disk, als repo-relatief SKILL.md-pad, gesorteerd en ontdubbeld."""
    sb = _laad_skills_bron()

    paden = sb.likara_skill_paden()
    assert paden == sorted(paden)
    assert len(paden) == len(set(paden)), "geen duplicaten toegestaan"

    namen_uit_paden = {p.split("/")[3] for p in paden}
    assert namen_uit_paden == set(sb.likara_skill_namen())
    assert all(p.endswith("/SKILL.md") for p in paden)


# ── Bijt-bewijs (groen -> rood -> groen) met tijdelijke fixtures ──────────────

def _maak_skilltree(basis: pathlib.Path, namen):
    skills_dir = basis / ".claude" / "skills" / "likara"
    for naam in namen:
        d = skills_dir / naam
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(f"# {naam}\n" + "x" * 300, encoding="utf-8")
    return skills_dir


def _maak_claude_md(basis: pathlib.Path, namen):
    regels = "\n".join(
        f"Read .claude/skills/likara/{n}/SKILL.md" for n in namen
    )
    claude = basis / "CLAUDE.md"
    claude.write_text(
        "# kop\n\n### Normale modus (sessie 2 en verder)\n\n"
        f"{regels}\n\n---\n\neinde\n",
        encoding="utf-8",
    )
    return claude


def test_borging_groen_bij_gelijke_sets(tmp_path):
    """GROEN: disk en CLAUDE.md noemen dezelfde drie skills => geen verschil."""
    sb = _laad_skills_bron()
    namen = ["likara-backend", "likara-ux", "likara-werkprotocol"]
    skills_dir = _maak_skilltree(tmp_path, namen)
    claude = _maak_claude_md(tmp_path, namen)

    op_disk = set(sb.likara_skill_namen(skills_dir))
    in_claude = set(sb.claude_md_likara_skillnamen(claude))
    assert op_disk == in_claude == set(namen)


def test_borging_bijt_als_skill_uit_claude_md_valt(tmp_path):
    """ROOD: CLAUDE.md mist één skill die wel op disk staat => mismatch detecteerbaar.
    Dit is exact het gat dat de drie borgende skills uit de ZIP liet vallen."""
    sb = _laad_skills_bron()
    disk_namen = ["likara-backend", "likara-ux", "likara-werkprotocol"]
    claude_namen = ["likara-backend", "likara-ux"]  # werkprotocol ontbreekt
    skills_dir = _maak_skilltree(tmp_path, disk_namen)
    claude = _maak_claude_md(tmp_path, claude_namen)

    op_disk = set(sb.likara_skill_namen(skills_dir))
    in_claude = set(sb.claude_md_likara_skillnamen(claude))

    assert op_disk != in_claude
    assert op_disk - in_claude == {"likara-werkprotocol"}
