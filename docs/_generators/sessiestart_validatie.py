#!/usr/bin/env python3
"""
Valideert de sessie-start ZIP bij het begin van een nieuwe sessie.
Eigenaar: G. van Capelle Beheer B.V.
"""

import sys
import zipfile
from pathlib import Path

VERPLICHT = [
    "CLAUDE.md",
    "NEXT_SESSION.md",
    "SESSIE_BRIEFING.md",
    "SESSIESTART.md",
]

def valideer(zip_pad: str):
    p = Path(zip_pad)
    if not p.exists():
        print(f"❌ ZIP niet gevonden: {zip_pad}")
        sys.exit(1)

    with zipfile.ZipFile(p) as zf:
        namen = set(zf.namelist())

    fouten = [v for v in VERPLICHT if v not in namen]
    if fouten:
        print("❌ Sessiestart-ZIP ongeldig — ontbrekende bestanden:")
        for f in fouten:
            print(f"   • {f}")
        sys.exit(1)

    print(f"✅ Sessiestart-ZIP geldig ({len(namen)} bestanden)")
    print(f"   Verplichte bestanden aanwezig: {', '.join(VERPLICHT)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Gebruik: python3 sessiestart_validatie.py <pad-naar-zip>")
        sys.exit(1)
    valideer(sys.argv[1])
