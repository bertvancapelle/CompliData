#!/usr/bin/env python3
"""
Genereert NEXT_SESSION.md voor CompliData.
Eigenaar: G. van Capelle Beheer B.V.
"""

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = REPO_ROOT / "NEXT_SESSION.md"

TEMPLATE = """\
# NEXT_SESSION.md — CompliData {build_label}

**Gegenereerd**: {datum}
**Vorige build**: {build_label}

---

## Top-5 prioriteiten volgende sessie

1. _[Vul in tijdens sessie-afsluiting]_
2. _[Vul in tijdens sessie-afsluiting]_
3. _[Vul in tijdens sessie-afsluiting]_
4. _[Vul in tijdens sessie-afsluiting]_
5. _[Vul in tijdens sessie-afsluiting]_

---

## Openstaande beslissingen

_[Vul in tijdens sessie-afsluiting]_

---

## Bekende risico's en aandachtspunten

_[Vul in tijdens sessie-afsluiting]_

---

## Technische schuld

_[Vul in tijdens sessie-afsluiting]_

---

## Geleerde patronen deze sessie

_[Vul in tijdens sessie-afsluiting — worden verwerkt in complidata-skills]_
"""

def main():
    build_label = sys.argv[1] if len(sys.argv) > 1 else "V???"
    inhoud = TEMPLATE.format(
        build_label=build_label,
        datum=date.today().isoformat()
    )
    OUTPUT.write_text(inhoud)
    print(f"✅ NEXT_SESSION.md gegenereerd ({build_label})")

if __name__ == "__main__":
    main()
