"""Cryptografische utilities — AVG Art. 25 privacy by design.

Gedeelde hash-functie voor pseudonimisering van PII in exports,
logs en audit trails.
"""
import hashlib


def hash_waarde(waarde: str | None) -> str | None:
    """Pseudonimiseert een waarde via SHA-256 (eerste 16 hex-karakters).

    Gebruik voor PII in exports, logs en audit trails.
    AVG Art. 25 — privacy by design.
    """
    if not waarde:
        return None
    return hashlib.sha256(waarde.encode()).hexdigest()[:16]
