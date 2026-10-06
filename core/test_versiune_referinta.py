# -*- coding: utf-8 -*-
"""GARD — anunțul „Versiune nouă” compară cu amprenta CODULUI ÎNCĂRCAT, nu cu prima citire de după autentificare (comanda
Costin 06.10.2026, pct.1a: „factura începută se pierde a PATRA oară”).

Măsurat pe producție (nginx + systemd): fila a încărcat aplicația la 19:12:40 (cod fără ciornă), publicarea la 19:15:26,
autentificarea la 19:46:51 fără reîncărcare. `versiune.js` își lua referința la PRIMA verificare, iar prima verificare pornește
la autentificare (`porneste`) — referința era amprenta nouă, deci anunțul nu apărea, iar retestul rula pe codul vechi.
CE FACE IMPOSIBIL: referința luată altundeva decât la evaluarea modulului. LIMITA (declarată și în cod): dacă citirea de la
încărcare eșuează, referința rămâne prima citire reușită. Proba de browser: `frontend_test/proba_versiune_la_incarcare.py`.
"""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(RAD, "static", "js", "versiune.js"), encoding="utf-8").read()


def _corp(nume):
    m = re.search(r"^(?:export )?(?:async )?function %s\([^)]*\)\s*\{(.*?)^\}" % nume, SRC, re.S | re.M)
    assert m, "funcția %s lipsește din versiune.js" % nume
    return m.group(1)


def test_amprenta_se_citeste_la_evaluarea_modulului():
    """MUTAȚIE: `const laIncarcare = citeste()…` mutat în `porneste` (sau scos) -> pică."""
    assert re.search(r"^const laIncarcare = citeste\(\)", SRC, re.M), "citirea de la încărcare nu e la nivelul modulului"
    assert "laIncarcare" not in _corp("porneste")


def test_referinta_e_amprenta_de_la_incarcare_nu_prima_verificare():
    """MUTAȚIE: `incarcata = await laIncarcare` înlocuit cu `incarcata = acum` -> pică."""
    v = _corp("verifica")
    i_inc = v.find("incarcata = await laIncarcare")
    assert i_inc >= 0, "verifica() nu ia referința de la încărcare"
    i_acum = v.find("incarcata = acum")
    assert i_acum == -1 or i_acum > i_inc, "prima citire devine referință înaintea amprentei de la încărcare"
    assert re.search(r"if \(incarcata === null\) \{ incarcata = acum; return; \}", v), "rezerva (citirea de la încărcare eșuată) lipsește"
