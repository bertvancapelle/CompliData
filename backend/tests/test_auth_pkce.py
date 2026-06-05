"""Tests — Keycloak PKCE login/callback (ADR-002), offline (Keycloak gemockt)."""
import base64
import hashlib
import json
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

from app.core import pkce
from app.core.config import settings
from app.main import app

_UNRESERVED = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
)


# ── Test-fixtures / fakes ────────────────────────────────────────────────────


class FakeRedis:
    """In-memory async Redis-vervanger (set/getdel/incr/expire)."""

    def __init__(self):
        self.store = {}

    async def set(self, k, v, ex=None):
        self.store[k] = v

    async def get(self, k):
        return self.store.get(k)

    async def getdel(self, k):
        return self.store.pop(k, None)

    async def incr(self, k):
        self.store[k] = int(self.store.get(k, 0)) + 1
        return self.store[k]

    async def expire(self, k, t):
        return True


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def fake_redis(monkeypatch):
    fr = FakeRedis()

    async def _get():
        return fr

    monkeypatch.setattr("app.api.v1.auth.get_redis", _get)
    return fr


@pytest.fixture
def fail_counter(monkeypatch):
    calls = []

    async def _fake(ip_hash):
        calls.append(ip_hash)

    monkeypatch.setattr("app.api.v1.auth._increment_fail_counter", _fake)
    return calls


def _doe_login(client):
    """Voer /login uit en geef (state, nonce) uit de redirect terug."""
    resp = client.get("/api/v1/auth/login", follow_redirects=False)
    assert resp.status_code == 302
    q = parse_qs(urlparse(resp.headers["location"]).query)
    return q["state"][0], q["nonce"][0]


# ── PKCE-helper ──────────────────────────────────────────────────────────────


def test_pkce_code_challenge_is_s256():
    v = pkce.generate_code_verifier()
    assert 43 <= len(v) <= 128
    assert set(v) <= _UNRESERVED
    verwacht = (
        base64.urlsafe_b64encode(hashlib.sha256(v.encode("ascii")).digest())
        .rstrip(b"=")
        .decode("ascii")
    )
    assert pkce.code_challenge_s256(v) == verwacht
    assert "=" not in pkce.code_challenge_s256(v)


def test_pkce_state_en_nonce_uniek():
    assert pkce.generate_state() != pkce.generate_state()
    assert pkce.generate_nonce() != pkce.generate_nonce()


# ── /login ───────────────────────────────────────────────────────────────────


def test_login_redirect_met_pkce_en_serverside_state(client, fake_redis):
    resp = client.get("/api/v1/auth/login", follow_redirects=False)
    assert resp.status_code == 302
    loc = resp.headers["location"]
    q = parse_qs(urlparse(loc).query)

    assert q["response_type"] == ["code"]
    assert q["scope"] == ["openid"]
    assert q["code_challenge_method"] == ["S256"]
    assert q["client_id"] == [settings.keycloak_client_id]
    assert q["redirect_uri"] == [
        settings.oidc_redirect_uri
        or f"{settings.platform_origin}/api/v1/auth/callback"
    ]
    # verifier/nonce mogen NIET in de browser-zichtbare redirect staan
    assert "code_verifier" not in loc

    state = q["state"][0]
    opslag = json.loads(fake_redis.store[f"auth_login:{state}"])
    assert set(opslag) == {"verifier", "nonce", "next"}
    # challenge in de URL hoort bij de server-side verifier
    assert q["code_challenge"][0] == pkce.code_challenge_s256(opslag["verifier"])
    assert q["nonce"][0] == opslag["nonce"]


def test_login_weigert_onbekende_queryparam(client, fake_redis):
    resp = client.get("/api/v1/auth/login?foo=bar", follow_redirects=False)
    assert resp.status_code == 400
    assert resp.json()["fout"]["code"] == "LOGIN_PARAMS_ONGELDIG"


def test_login_next_open_redirect_genormaliseerd(client, fake_redis):
    resp = client.get(
        "/api/v1/auth/login?next=https://kwaad.example/x", follow_redirects=False
    )
    state = parse_qs(urlparse(resp.headers["location"]).query)["state"][0]
    assert json.loads(fake_redis.store[f"auth_login:{state}"])["next"] == "/"


def test_login_next_relatief_pad_behouden(client, fake_redis):
    resp = client.get("/api/v1/auth/login?next=/dashboard", follow_redirects=False)
    state = parse_qs(urlparse(resp.headers["location"]).query)["state"][0]
    assert json.loads(fake_redis.store[f"auth_login:{state}"])["next"] == "/dashboard"


# ── /callback — succes ───────────────────────────────────────────────────────


def test_callback_succes_zet_cd_session_cookie(client, fake_redis, monkeypatch):
    state, nonce = _doe_login(client)
    gezien = {}

    async def fake_exchange(code, redirect_uri, code_verifier=None):
        gezien["code"] = code
        gezien["verifier"] = code_verifier
        return {"access_token": "acc-token", "id_token": "id-token"}

    def fake_decode_id(token, expected_nonce=None):
        gezien["nonce"] = expected_nonce
        return {"sub": "user-1", "nonce": expected_nonce}

    monkeypatch.setattr("app.api.v1.auth.exchange_code_for_tokens", fake_exchange)
    monkeypatch.setattr("app.api.v1.auth.decode_id_token", fake_decode_id)

    resp = client.get(
        f"/api/v1/auth/callback?code=auth-code-123&state={state}",
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert gezien["code"] == "auth-code-123"
    assert gezien["verifier"]  # PKCE code_verifier server-side meegestuurd
    assert gezien["nonce"] == nonce  # nonce uit login server-side teruggekoppeld

    setcookie = resp.headers["set-cookie"].lower()
    assert f"{settings.cookie_name}=acc-token".lower() in setcookie
    assert "httponly" in setcookie
    assert "secure" in setcookie
    assert "samesite=strict" in setcookie


def test_callback_succes_dan_me_geeft_gebruiker(client, fake_redis, monkeypatch):
    state, _ = _doe_login(client)

    async def fake_exchange(code, redirect_uri, code_verifier=None):
        return {"access_token": "acc-token", "id_token": "id-token"}

    monkeypatch.setattr("app.api.v1.auth.exchange_code_for_tokens", fake_exchange)
    monkeypatch.setattr(
        "app.api.v1.auth.decode_id_token", lambda t, expected_nonce=None: {"sub": "u"}
    )

    r = client.get(
        f"/api/v1/auth/callback?code=x&state={state}", follow_redirects=False
    )
    assert r.status_code == 303

    # /me met de sessie-cookie → gebruiker (decode_token gemockt)
    monkeypatch.setattr(
        "app.middleware.auth.decode_token",
        lambda t: {"sub": "user-1", "tenant_id": "tenant-1", "email": "u@x.nl"},
    )
    client.cookies.set(settings.cookie_name, "acc-token")
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["tenant_id"] == "tenant-1"


def test_me_zonder_cookie_401(client):
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 401
    assert me.json()["detail"]["code"] == "TOKEN_ONGELDIG"


# ── /callback — foutpaden ────────────────────────────────────────────────────


def test_callback_state_ongeldig_geen_sessie(client, fake_redis, fail_counter):
    # Syntactisch geldige maar onbekende state → geen sessie, fail-counter+1
    resp = client.get(
        "/api/v1/auth/callback?code=x&state=" + "A" * 24, follow_redirects=False
    )
    assert resp.status_code == 400
    assert resp.json()["fout"]["code"] == "STATE_ONGELDIG"
    assert "set-cookie" not in resp.headers
    assert fail_counter  # IP-gepseudonimiseerde teller aangeroepen


def test_callback_replay_state_is_eenmalig(client, fake_redis, monkeypatch):
    state, _ = _doe_login(client)

    async def fake_exchange(code, redirect_uri, code_verifier=None):
        return {"access_token": "acc", "id_token": "id"}

    monkeypatch.setattr("app.api.v1.auth.exchange_code_for_tokens", fake_exchange)
    monkeypatch.setattr(
        "app.api.v1.auth.decode_id_token", lambda t, expected_nonce=None: {"sub": "u"}
    )

    eerste = client.get(
        f"/api/v1/auth/callback?code=x&state={state}", follow_redirects=False
    )
    assert eerste.status_code == 303
    tweede = client.get(
        f"/api/v1/auth/callback?code=x&state={state}", follow_redirects=False
    )
    assert tweede.status_code == 400
    assert tweede.json()["fout"]["code"] == "STATE_ONGELDIG"


def test_callback_token_exchange_mislukt(client, fake_redis, fail_counter, monkeypatch):
    state, _ = _doe_login(client)

    async def fake_exchange_fail(code, redirect_uri, code_verifier=None):
        raise RuntimeError("keycloak onbereikbaar")

    monkeypatch.setattr("app.api.v1.auth.exchange_code_for_tokens", fake_exchange_fail)

    resp = client.get(
        f"/api/v1/auth/callback?code=x&state={state}", follow_redirects=False
    )
    assert resp.status_code == 502
    assert resp.json()["fout"]["code"] == "TOKEN_UITWISSELING_MISLUKT"
    assert "set-cookie" not in resp.headers
    assert fail_counter


def test_callback_id_token_ongeldig(client, fake_redis, fail_counter, monkeypatch):
    state, _ = _doe_login(client)

    async def fake_exchange(code, redirect_uri, code_verifier=None):
        return {"access_token": "acc", "id_token": "id"}

    def fake_decode_bad(token, expected_nonce=None):
        raise ValueError("nonce/aud/exp ongeldig")

    monkeypatch.setattr("app.api.v1.auth.exchange_code_for_tokens", fake_exchange)
    monkeypatch.setattr("app.api.v1.auth.decode_id_token", fake_decode_bad)

    resp = client.get(
        f"/api/v1/auth/callback?code=x&state={state}", follow_redirects=False
    )
    assert resp.status_code == 401
    assert resp.json()["fout"]["code"] == "ID_TOKEN_ONGELDIG"
    assert "set-cookie" not in resp.headers
    assert fail_counter


def test_callback_keycloak_error_param(client, fake_redis):
    resp = client.get(
        "/api/v1/auth/callback?error=access_denied&error_description=geweigerd&state="
        + "A" * 24,
        follow_redirects=False,
    )
    assert resp.status_code == 400
    assert resp.json()["fout"]["code"] == "AUTH_GEWEIGERD"
    assert "set-cookie" not in resp.headers


def test_callback_weigert_onbekende_queryparam(client, fake_redis):
    resp = client.get(
        "/api/v1/auth/callback?code=x&state=" + "A" * 24 + "&foo=bar",
        follow_redirects=False,
    )
    assert resp.status_code == 400
    assert resp.json()["fout"]["code"] == "CALLBACK_PARAMS_ONGELDIG"
