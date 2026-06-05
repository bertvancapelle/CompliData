#!/usr/bin/env python3
"""
Genereert SESSIE_BRIEFING.md voor CompliData.
Wordt door CC gelezen bij sessiestart als context-briefing.
Eigenaar: G. van Capelle Beheer B.V.
"""

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = REPO_ROOT / "SESSIE_BRIEFING.md"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
NEXT_SESSION = REPO_ROOT / "NEXT_SESSION.md"
COUNTER_FILE = REPO_ROOT / "docs" / "_generators" / "build_counter.json"

def lees_bouwstatus():
    tekst = CLAUDE_MD.read_text()
    blok = re.search(
        r"<!-- BOUWSTATUS_START -->(.*?)<!-- BOUWSTATUS_END -->",
        tekst, re.DOTALL
    )
    return blok.group(1).strip() if blok else "_geen bouwstatus gevonden_"

def lees_next_session():
    if NEXT_SESSION.exists():
        return NEXT_SESSION.read_text()
    return "_NEXT_SESSION.md niet gevonden_"

def git_log(n=5):
    try:
        result = subprocess.run(
            ["git", "log", f"--oneline", f"-{n}"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        return result.stdout.strip() if result.returncode == 0 else "_git log niet beschikbaar_"
    except Exception:
        return "_git log niet beschikbaar_"

def main():
    build_label = sys.argv[1] if len(sys.argv) > 1 else "V???"

    inhoud = f"""# SESSIE_BRIEFING.md — CompliData {build_label}

**Gegenereerd**: {date.today().isoformat()}

---

## Bouwstatus

{lees_bouwstatus()}

---

## Recente commits

```
{git_log()}
```

---

## Prioriteiten volgende sessie

{lees_next_session()}

---

## Instructie voor CC

1. Lees deze briefing volledig
2. Lees CLAUDE.md (sessiestart-protocol)
3. Bevestig: "Sessie-briefing geladen — CompliData {build_label}"
4. Wacht op START: [naam] van Bert
"""
    OUTPUT.write_text(inhoud)
    print(f"✅ SESSIE_BRIEFING.md gegenereerd ({build_label})")

if __name__ == "__main__":
    main()
