"""PKCE- en CSRF-helpers voor de OAuth2 Authorization Code-flow (ADR-002).

RFC 7636 (PKCE, S256) + OIDC `state`/`nonce`. Alleen stdlib — geen externe
afhankelijkheden, volledig offline testbaar. Alle waarden zijn
cryptografisch willekeurig (`secrets`).
"""
import base64
import hashlib
import secrets


def _b64url(ruw: bytes) -> str:
    """base64url zonder padding (RFC 7636 §A)."""
    return base64.urlsafe_b64encode(ruw).rstrip(b"=").decode("ascii")


def generate_code_verifier() -> str:
    """code_verifier: 43–128 tekens uit de unreserved-set (RFC 7636 §4.1)."""
    return _b64url(secrets.token_bytes(64))


def code_challenge_s256(code_verifier: str) -> str:
    """code_challenge = base64url(SHA-256(code_verifier)) zonder padding (S256)."""
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return _b64url(digest)


def generate_state() -> str:
    """Ondoorzichtige CSRF-state-token."""
    return secrets.token_urlsafe(32)


def generate_nonce() -> str:
    """OIDC nonce — bindt het id_token aan deze login-aanvraag (replay-bescherming)."""
    return secrets.token_urlsafe(32)
