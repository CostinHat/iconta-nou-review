# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 600] „Conectarea SPV a eșuat de trei ori cu certificatul DigiSign care a mers pe 16.10 (sesiune ANAF invalidă,
apoi pagina de ieșire ANAF); află cauza, iar la orice eșec contabilul se întoarce în iConta cu un mesaj clar.”

Ce se păzește aici (pe server, fără ANAF: schimbul codului e simulat):
  1. fiecare întoarcere din ANAF -> un MOTIV din mulțimea închisă `spv_rute.MOTIVE_RETUR`, niciodată o excepție (înainte: o cădere din
     afara lui `EroareSpv` — rețeaua spre ANAF, baza — ieșea 500, iar celelalte puneau textul excepției în URL: `?eroare=state invalid:
     token expirat`);
  2. pagina de retur (`static/spv_callback.html`) are un text pentru FIECARE motiv și numai pentru ele, fără termeni tehnici, iar „10
     minute” din textul expirării = `spv_conector.STATE_DURATA_SEC`;
  3. detaliul tehnic al eșecului ajunge în jurnalul serverului (`observare.esec_secundar`), fără codul de autorizare.
Cazul în care ANAF nu trimite deloc înapoi („sesiune invalidă” / pagina de ieșire ANAF) e prins de fila iConta.eu la întoarcere
(`setari.js::asteaptaIntoarcerea`), probat în browser: `frontend_test/e2e/e2e_lot12_notif.py::test_def_600_*`.

Temei: N/A — fluxul OAuth al conectorului (ARHITECTURA_SPV.md „FLUXUL DE AUTORIZARE”: state CSRF expiră în 10 minute; fereastra de
obținere a tokenului 60 de secunde), nu o regulă fiscală.
"""
import json
import os
import re
import time

import pytest
import requests

from core import observare
from core import spv_conector as C
from core import spv_rute as R

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINA = os.path.join(RAD, "static", "spv_callback.html")
#: ce nu are voie să apară în textele pentru contabil
TEHNIC = re.compile(r"\b(state|token|HTTP|OAuth|callback|exception|excep|Error|code|cod\s+\d|\d{3}\b)", re.I)


@pytest.fixture()
def jurnal(monkeypatch):
    scrise = []
    monkeypatch.setattr(observare, "esec_secundar", lambda et, e, alerta=False: scrise.append((et, str(e))))
    return scrise


def _state(acum=None):
    return C.genereaza_state(C.principal_firm(4242), acum=acum)


def _mesaje_pagina():
    src = open(PAGINA, encoding="utf-8").read()
    bloc = re.search(r"const MESAJE = \{(.*?)\n    \};", src, re.S).group(1)
    return dict(re.findall(r'^\s+(\w+): "([^"]+)",$', bloc, re.M)), src


def test_def_600_fiecare_intoarcere_are_motivul_ei_fara_exceptie(monkeypatch, jurnal):
    """MUTAȚIE: ramura `except requests.exceptions.RequestException` scoasă din `rezultat_callback` -> „nesalvata”, nu „anaf_tace” -> pică;
    `except Exception` final scos -> excepția bazei urcă (500) -> pică."""
    apel = {}

    def schimb(principal, code, acum=None):
        apel["principal"], apel["code"] = principal, code
        return 1
    monkeypatch.setattr(C, "finalizeaza_autorizare", schimb)
    assert R.rezultat_callback("COD-OK", _state()) == "ok"
    assert apel == {"principal": C.principal_firm(4242), "code": "COD-OK"}

    assert R.rezultat_callback("", "", error="access_denied", error_description="Utilizatorul a refuzat") == "anulata"
    assert R.rezultat_callback("", _state()) == "fara_cod"
    assert R.rezultat_callback("X", _state(acum=int(time.time()) - C.STATE_DURATA_SEC - 5)) == "expirata"
    assert R.rezultat_callback("X", "nu-e-un-state") == "nelegata"
    assert R.rezultat_callback("X", "e30.!!!") == "nelegata"            # base64 / JSON stricat: tot „nelegată”, nu 500
    falsificat = _state().split(".")[0] + ".AAAA"
    assert R.rezultat_callback("X", falsificat) == "nelegata"

    def refuz(principal, code, acum=None):
        raise C.EroareSpv("HTTP 400 la /token: {\"error\":\"invalid_grant\"}")
    monkeypatch.setattr(C, "finalizeaza_autorizare", refuz)
    assert R.rezultat_callback("X", _state()) == "refuz_anaf"

    def tace(principal, code, acum=None):
        raise requests.exceptions.ReadTimeout("HTTPSConnectionPool(host='logincert.anaf.ro'): Read timed out.")
    monkeypatch.setattr(C, "finalizeaza_autorizare", tace)
    assert R.rezultat_callback("X", _state()) == "anaf_tace"

    def baza(principal, code, acum=None):
        raise RuntimeError("could not connect to server")
    monkeypatch.setattr(C, "finalizeaza_autorizare", baza)
    assert R.rezultat_callback("X", _state()) == "nesalvata"

    monkeypatch.delenv("JWT_SECRET")
    assert R.rezultat_callback("X", "a.b") == "nesalvata"               # configurarea serverului: tot o întoarcere cu mesaj

    # detaliul tehnic e în jurnal (fiecare eșec, cu motivul), iar codul de autorizare nu apare acolo
    assert [et for et, _ in jurnal] == ["conectare SPV: %s" % m for m in
                                        ("anulata", "fara_cod", "expirata", "nelegata", "nelegata", "nelegata", "refuz_anaf",
                                         "anaf_tace", "nesalvata", "nesalvata")], jurnal
    assert "access_denied" in jurnal[0][1] and "invalid_grant" in jurnal[6][1]
    assert "COD-OK" not in "\n".join(d for _, d in jurnal)   # cele 10 rânduri de mai sus, toate


def test_def_600_ruta_trimite_numai_motivul_spre_pagina_de_retur(monkeypatch):
    """Ruta (`/anaf/oauth/callback`) redirecționează cu `?motiv=<motiv>` și nimic altceva — niciun text de excepție în URL."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    app = FastAPI()
    R.monteaza(app, lambda: {})
    monkeypatch.setattr(observare, "esec_secundar", lambda *a, **k: None)
    c = TestClient(app)
    r = c.get("/anaf/oauth/callback", params={"code": "X", "state": "nu-e-un-state"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/static/spv_callback.html?motiv=nelegata", r.headers
    r = c.get("/anaf/oauth/callback", params={"error": "server_error", "error_description": "HTTP 500 java.lang.NullPointerException"},
              follow_redirects=False)
    assert r.headers["location"] == "/static/spv_callback.html?motiv=anulata"


def test_def_600_pagina_de_retur_are_un_text_clar_pentru_fiecare_motiv():
    """MUTAȚIE: cheia `expirata` scoasă din `MESAJE` (pagina) -> pică; `?eroare=` afișat din nou -> pică."""
    mesaje, src = _mesaje_pagina()
    assert set(mesaje) == set(R.MOTIVE_RETUR), (sorted(mesaje), R.MOTIVE_RETUR)
    for motiv, text in mesaje.items():
        assert not TEHNIC.search(text), (motiv, TEHNIC.search(text).group(0), text)
        if motiv != "ok":
            # textul, pe bucățile lui: o propoziție care se încheie cu „SPV nu s-a conectat” și butonul pe care îl apasă (ori Suportul)
            bucati = [b.strip() for b in re.split(r"[,;:]|\.(?=\s|$)", text)]
            neconectat = [b for b in bucati if b.endswith("SPV nu s-a conectat")]
            butoane = set(re.findall(r"„([^”]+)”", text))
            assert (len(neconectat) == 1 and butoane >= {"Conectează SPV"}) or set(re.findall(r"\w+", text)) >= {"Suport"}, (motiv, text)
    # ARHITECTURA_SPV.md: „state, legat de accounting_firm_id, expira in 10 min” — textul spune aceeași durată ca serverul
    assert C.STATE_DURATA_SEC == 600 and set(re.findall(r"(\d+) minute", mesaje["expirata"])) == {str(C.STATE_DURATA_SEC // 60)}, (
        mesaje["expirata"])
    # pagina nu mai afișează un text venit din URL (`?eroare=` era scris direct în pagină: oricine putea pune acolo orice text)
    assert 'get("eroare")' not in src and "get('eroare')" not in src
    assert json.dumps(R.MOTIVE_RETUR)   # mulțimea e serializabilă (o tuplă de șiruri)
