# -*- coding: utf-8 -*-
"""GARD — FAPT_FISCAL_NECERUT în ecranele scrise de mână (comanda Costin 07.10.2026: „Extinde regula la ecranele scrise de mână, cu
clasificarea celor 82”; DS cap.17).

Instanța: în afara registrului Operațiunilor, 82 de selecturi veneau cu prima opțiune aleasă. 59 erau fapte fiscale (declarații manuale,
moneda / țara / tipul operației la emitere, tipul firmei, S1005/S1003, categoria dispoziției de casă, codul CM, RIP, eTransport …):
acum pornesc cu „— alege —” și handlerul refuză trimiterea fără alegere, lângă câmp. Celelalte 23 sunt clasificate, fiecare cu
motivul (ne-fiscale, valoare existentă, opțiune goală în builder, un conflict DS). Instrumentul: `scripts/scan_selecturi_ecrane.py`
(același cu regula din verificator).
"""
import collections
import io
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))

import scan_selecturi_ecrane as S  # noqa: E402


def _js(p):
    return io.open(os.path.join(RAD, p), encoding="utf-8").read()


def test_niciun_fapt_fiscal_nu_vine_ales_de_ecran():
    """MUTAȚIE: „— alege —” scos de la moneda emiterii -> pică; `#em-moneda` scos din `cereAlegerile` -> pică."""
    assert S.masoara() == []


def test_clasificarea_acopera_cele_82_si_fiecare_are_motiv():
    toate = S.selecturi()
    assert len(toate) >= 100                                   # premisă: selecturile chiar se văd (108 măsurate)
    clase = collections.Counter(c for c, _m in S.CLASIFICARE.values())
    assert clase[S.FISCAL] == 59 and sum(clase.values()) == 81  # 82 de selecturi: `je-centru` apare de două ori
    assert all(len(m) > 40 for _c, m in S.CLASIFICARE.values())
    assert set(S.HELPERE) <= set(S.CLASIFICARE)


def test_mecanismul_comun_din_api():
    """`ALEGE` e selectată, neselectabilă după alegere și MARCATĂ (`data-alege`, nu valoarea goală — „” e o valoare legitimă la
    D212); `cereAlegerile` caută marcajul și sare peste câmpurile ascunse."""
    api = _js("static/js/api.js")
    alege = re.search(r"export const ALEGE = '([^']+)'", api).group(1)
    assert all(x in alege.split() or x in alege for x in ("data-alege", "selected", "disabled", "hidden"))
    corp = api[api.index("export function cereAlegerile"):]
    corp = corp[:corp.index("\n}\n")]
    assert re.search(r'hasAttribute\("data-alege"\)', corp) and re.search(r"offsetParent === null", corp)


def test_CALIBRARE_select_fiscal_fara_alege_e_prins():
    p = "static/js/ecrane/emitere_ecran.js"
    s = _js(p)
    a = '<select class="camp-input" id="em-moneda">${ALEGE}'
    assert s.count(a) == 1
    rele = dict(S.masoara([(p, s.replace(a, '<select class="camp-input" id="em-moneda">'))]))
    assert rele.get("emitere_ecran.js:em-moneda", "").startswith("fapt fiscal fără")


def test_CALIBRARE_select_fiscal_necerut_de_handler_e_prins():
    p = "static/js/ecrane/emitere_ecran.js"
    s = _js(p)
    a = '["#em-moneda", "#em-tara", "#em-tipop", "#em-tip"]'
    assert s.count(a) == 1
    rele = dict(S.masoara([(p, s.replace(a, '["#em-tara", "#em-tipop", "#em-tip"]'))]))
    assert rele.get("emitere_ecran.js:em-moneda", "").startswith("fapt fiscal pe care handlerul nu-l cere")


def test_CALIBRARE_select_nou_neclasificat_e_prins():
    rele = S.masoara([("static/js/ecrane/nou.js", '<select id="x-cota" class="camp-input"><option value="21">21</option></select>')])
    assert [k for k, _ce in rele] == ["nou.js:x-cota"]


def test_starea_initiala_a_formularelor_panou_porneste_nealeasa():
    """MUTAȚIE: `valabilitate_distribuire: 1` pus la loc în starea D230 -> pică (proba de browser arăta „Un an” deși markup-ul avea
    „— alege —”)."""
    assert S.stare_initiala_incalcata(_js("static/js/ecrane/declaratii.js")) == []


def test_CALIBRARE_stare_initiala():
    js = _js("static/js/ecrane/declaratii.js")
    a = 'procent: "", valabilitate_distribuire: null }'
    assert js.count(a) == 1
    assert S.stare_initiala_incalcata(js.replace(a, 'procent: "", valabilitate_distribuire: 1 }')) == [("d230", "valabilitate_distribuire")]
