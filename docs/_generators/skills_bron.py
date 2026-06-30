#!/usr/bin/env python3
"""Eén bron van waarheid voor de LIKARA likara-skillset.

Zowel de sessie-ZIP-bundeling (gen_sessiestart.py) als de build-validatie
(gen_build.py) leiden de likara-skills deterministisch af via deze helper —
in plaats van handgecodeerde lijsten die uit elkaar lopen. De anti-divergentie-
test (backend/tests/test_skill_bron_consistentie.py) borgt dat deze afgeleide
set gelijk blijft aan wat CLAUDE.md in normale modus voorschrijft.

Eigenaar: G. van Capelle Beheer B.V.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIKARA_SKILLS_DIR = REPO_ROOT / ".claude" / "skills" / "likara"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

_NORMALE_MODUS_KOP = "### Normale modus"
_SKILL_PAD_RE = re.compile(r"\.claude/skills/likara/(likara-[a-z0-9-]+)/SKILL\.md")


def likara_skill_namen(skills_dir: Path = LIKARA_SKILLS_DIR):
    """Directorynamen van alle likara-skills met een niet-leeg SKILL.md op disk,
    gesorteerd voor stabiele, deterministische volgorde."""
    return sorted(
        p.parent.name
        for p in Path(skills_dir).glob("*/SKILL.md")
        if p.is_file()
    )


def likara_skill_paden(skills_dir: Path = LIKARA_SKILLS_DIR):
    """Repo-relatieve POSIX-paden naar elke likara SKILL.md, gesorteerd, stabiel.

    Dit is de enige afgeleide bron die generators consumeren."""
    return [
        f".claude/skills/likara/{naam}/SKILL.md"
        for naam in likara_skill_namen(skills_dir)
    ]


def claude_md_likara_skillnamen(claude_md: Path = CLAUDE_MD):
    """Likara-skillnamen die CLAUDE.md voorschrijft in het 'Normale modus'-blok
    (sessie 2 en verder).

    Het blok loopt vanaf de '### Normale modus'-kop tot de eerstvolgende
    horizontale regel ('---'). Zo tellen losse verwijzingen elders in CLAUDE.md
    (bv. de structuursectie) niet mee. Gesorteerd, ontdubbeld."""
    tekst = Path(claude_md).read_text(encoding="utf-8")
    start = tekst.find(_NORMALE_MODUS_KOP)
    if start == -1:
        return []
    rest = tekst[start:]
    eind = rest.find("\n---")
    blok = rest if eind == -1 else rest[:eind]
    return sorted(set(_SKILL_PAD_RE.findall(blok)))
