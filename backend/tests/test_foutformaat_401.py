"""Tests — foutcontract ADR-014: 401 canoniek envelope, 422 bewust native.

Bewijst het twee-vormen-contract (B3) in één app: 401 = `{"fout":{...}}`,
422 = native FastAPI `{"detail":[...]}`. En dat `NietGeauthenticeerd` (subclass
van HTTPException) óók zonder geregistreerde handler een echte 401 geeft.
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.middleware.auth import NietGeauthenticeerd, niet_geauthenticeerd_handler


class _Body(BaseModel):
    naam: str


def _app(met_handler=True):
    app = FastAPI()
    if met_handler:
        app.add_exception_handler(NietGeauthenticeerd, niet_geauthenticeerd_handler)

    @app.get("/beveiligd")
    async def _beveiligd():
        raise NietGeauthenticeerd("Geen sessie gevonden.")

    @app.post("/valideer")
    async def _valideer(body: _Body):
        return {"ok": True}

    return app


def test_401_canoniek_envelope():
    r = TestClient(_app()).get("/beveiligd")
    assert r.status_code == 401
    assert r.json() == {
        "fout": {"code": "NIET_GEAUTHENTICEERD", "http_status": 401, "bericht": "Geen sessie gevonden."}
    }
    assert "detail" not in r.json()


def test_422_blijft_native_detail_lijst():
    r = TestClient(_app()).post("/valideer", json={})  # naam ontbreekt
    assert r.status_code == 422
    body = r.json()
    assert isinstance(body.get("detail"), list)  # native FastAPI-vorm
    assert "fout" not in body


def test_401_zonder_handler_blijft_401():
    # HTTPException-subclass → 401-fallback ook zonder geregistreerde handler.
    r = TestClient(_app(met_handler=False)).get("/beveiligd")
    assert r.status_code == 401
