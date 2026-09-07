# -*- coding: utf-8 -*-
"""GARD (07.09.2026) — cele 50 de declarații de pe ecranul public nu pot rămâne în urmă.

TREI LUCRURI, fiecare cu felul lui de a se strica:

  SURSA     fiecare `core/dNNN.py` poartă `DENUMIRE_OFICIALA`. O declarație nouă fără ea ar apărea
            pe ecranul public fără nume — de-aia generatorul REFUZĂ, și de-aia se cere aici.
  BLOCUL    ce e în `login.js` între ancore trebuie să fie IDENTIC cu ce produce generatorul azi.
            Altfel ecranul arată o listă de ieri despre o aplicație de azi.
  RANDAREA  „toate cele 50, fără bară de derulare" e o afirmație despre așezare, nu despre cod. O
            ține proba din browser (`frontend_test/proba_decl50.py`), cuplată la `ui_hash`: dacă
            `login.js` sau `stil.css` se schimbă după probă, proba e INVALIDĂ, nu doar veche.

ANTI-VACUU: dacă artefactul ar fi gol sau lista ar fi goală, toate probele de mai sus ar trece
degeaba. De-aia se cere numărul, și se cere să fie EGAL cu câte tipuri are `DECLARATII`.
"""
import importlib
import io
import json
import os
import re
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "scripts"))
sys.path.insert(0, os.path.join(_RAD, "frontend_test", "vizual"))

from core import declaratii_api as da  # noqa: E402
import genereaza_declaratii_lista as G  # noqa: E402
from acoperire_hash import ui_hash  # noqa: E402

ARTEFACT = os.path.join(_RAD, "frontend_test", "proba_decl50.json")
LOGIN = os.path.join(_RAD, "static", "js", "ecrane", "login.js")
DIACRITICE = set("ăâîșțĂÂÎȘȚ")


def test_fiecare_declaratie_are_denumire_oficiala():
    fara = []
    for tip in sorted(da.DECLARATII):
        m = importlib.import_module("core." + tip)
        d = (getattr(m, "DENUMIRE_OFICIALA", "") or "").strip()
        if not d:
            fara.append(tip)
    assert fara == [], "declarații fără DENUMIRE_OFICIALA: %s" % fara


def test_denumirile_au_diacritice():
    """Text AFIȘAT, deci cu diacritice.

    Prima formă a acestui test căuta substringul „declara" ca semn de lipsă — dar
    „Declarație".lower() îl conține, deci se aprindea pe TOATE cele 50, inclusiv pe cele scrise
    corect. Se caută acum FORMELE ASCII care, în românește, cer obligatoriu diacritică.
    «Decont de TVA» n-are nicio diacritică și e scris corect — de-aia criteriul e pe cuvinte,
    nu pe prezența unei diacritice în fiecare denumire."""
    ASCII_GRESIT = ("declaratie", "declaratii", "declaratia", "informativa", "speciala",
                    "privind obligatiile", "platitor", "retinut", "anuala", "juridica")
    rele = []
    for tip in sorted(da.DECLARATII):
        d = (getattr(importlib.import_module("core." + tip), "DENUMIRE_OFICIALA", "") or "").lower()
        for w in ASCII_GRESIT:
            if w in d:
                rele.append((tip, w))
    assert rele == [], "denumiri cu forme ASCII care cer diacritice: %s" % rele


def test_blocul_din_login_e_cel_de_ACUM():
    src = io.open(LOGIN, encoding="utf-8").read()
    m = re.search(r"const DECLARATII_50 = (\[.*?\]);", src, re.S)
    assert m, "blocul generat lipsește din login.js"
    din_ecran = json.loads(m.group(1))
    assert din_ecran == G.lista(), (
        "blocul din login.js diferă de ce produce generatorul — rulează "
        "scripts/genereaza_declaratii_lista.py --scrie")
    assert len(din_ecran) == len(da.DECLARATII)


def test_generatorul_refuza_o_declaratie_fara_denumire(monkeypatch, capsys):
    """CALIBRARE: fără refuz, o declarație nouă ar ajunge pe ecranul public fără nume."""
    monkeypatch.setattr(G, "_denumire", lambda tip: "" if tip == "d100" else "x")
    assert G.main([]) == 2
    # tipul refuzat se cere ca ELEMENT al listei tiparite, nu ca subsir al iesirii: un `in` pe text
    # ar trece si daca „D100" ar aparea din alt motiv, oriunde in mesaj.
    iesire = capsys.readouterr().out
    tipuri = [x.strip(" []'\",") for linie in iesire.splitlines() if "REFUZ" in linie
              for x in linie.split("[")[-1].split("]")[0].split(",")]
    assert tipuri == ["D100"], tipuri


def _proba():
    if not os.path.exists(ARTEFACT):
        pytest.fail("proba lipsește — rulează frontend_test/proba_decl50.py")
    return json.load(io.open(ARTEFACT, encoding="utf-8"))


def test_proba_e_proaspata():
    assert _proba().get("ui_hash") == ui_hash(), (
        "login.js / stil.css s-au schimbat de la ultima probă a celor 50 — rulează "
        "frontend_test/proba_decl50.py și comite artefactul")


def test_toate_cele_50_se_randeaza_si_incap():
    p = _proba()
    assert p["celule"] == len(da.DECLARATII) == p["butoane_ce"]
    assert set(p["coduri"]) == {t.upper() for t in da.DECLARATII}
    assert p["derulare"]["grila"] is False, "grila are bară de derulare"
    assert p["derulare"]["corp"] is False, "fereastra are bară de derulare"
    assert p["invizibile"] == [], "celule tăiate sau în afara ecranului: %s" % p["invizibile"]


def test_semnul_intrebarii_chiar_explica():
    """Și explică DIFERIT pentru declarații diferite — altfel ar merge și cu un text fix."""
    p = _proba()
    assert p["explicatii_diferite"] is True
    assert all(len(t) > 20 for t in p["explicatii"])


def test_ecranul_public_e_curat_la_privire():
    p = _proba()
    assert p["axe"]["violari"] == []
    assert sum(len(v) for v in p["axe"]["title_only"].values()) == 0
    m = p["mobil"]
    assert m["celule"] == len(da.DECLARATII)
    assert m["revarsare_x"] is False
    assert m["tinte_sub_24"] == 0
