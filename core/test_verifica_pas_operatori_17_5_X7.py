# -*- coding: utf-8 -*-
"""17.5-X7 — operatorii NOI ai oracolului (scripts/verifica_pas.py): `text_vizibil` și `rand_propriu`, folosiți numai la a.10, a.15, a.17, și compatibilitatea operatorilor VECHI,
inclusiv `text_contine` (citește `textContent`, semantica neschimbată). Părțile pure nu cer Chromium; citirea din pagină se probează pe pagini mici cu martori: text ascuns, aria-hidden,
detaliu închis, text sub linia de derulare, text în alt rând, rând duplicat, selector lipsă, text vizibil / rând corect."""
import os
import sys

import pytest

_SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")


@pytest.fixture
def VP(monkeypatch):
    monkeypatch.syspath_prepend(_SCRIPTS)
    import verifica_pas
    return verifica_pas


@pytest.fixture(scope="module")
def pagina():
    pw = pytest.importorskip("playwright.sync_api")
    with pw.sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1366, "height": 768})
        yield pg
        b.close()


def _citeste(VP, pagina, html, cheie, operator):
    pagina.set_content(html)
    return VP.observa_pagina(pagina, cheie, "/tmp", operator)[1]


# ---- părțile pure ---------------------------------------------------------------------------------------------------------------------------------------------------------------
def test_operatorii_noi_sunt_cunoscuti_iar_cei_vechi_au_ramas(VP):
    for o in ("egal", "contine", "nr_randuri", "lipseste", "interval_px", "activ", "text_contine"):
        assert o in VP.OPERATORI
    assert VP.OPERATORI_NOI_17_5_X7 == ("text_vizibil", "rand_propriu")
    assert all(o in VP.OPERATORI for o in VP.OPERATORI_NOI_17_5_X7)


def test_text_contine_ramane_pe_textContent_chiar_cu_text_ascuns(VP):
    # semantica veche: un șir aflat într-un element ascuns TRECE la text_contine; operatorul nou îl respinge (vezi mai jos)
    assert VP.compara_asertiune("text_contine", "ascuns", "text ascuns aici")[0] == "trece"
    assert VP.compara_asertiune("text_vizibil", "ascuns", "alt text")[0] == "pica"


@pytest.mark.parametrize("operator,valoare,observat,asteptat", [
    ("egal", "1210.00", "1210.0", "trece"), ("egal", "a", "b", "pica"), ("contine", "b", "a,b", "trece"), ("lipseste", "x", "abc", "trece"), ("lipseste", "a", "abc", "pica"),
    ("nr_randuri", "2", ["a", "b"], "trece"), ("nr_randuri", "3", ["a", "b"], "pica"), ("activ", "true", True, "trece"), ("activ", "true", False, "pica"),
    ("interval_px", "40-40", [40.0], "trece"), ("interval_px", "40-40", [30.0], "pica")])
def test_operatorii_vechi_dau_acelasi_verdict(VP, operator, valoare, observat, asteptat):
    assert VP.compara_asertiune(operator, valoare, observat)[0] == asteptat


def test_rand_propriu_un_singur_rand_care_incepe_cu_A_si_contine_B(VP):
    v = "TVA de plată && Diferență neexplicată: 1.341,00 lei"
    assert VP.compara_asertiune("rand_propriu", v, ["TVA de plată · rezultat Diferență neexplicată: 1.341,00 lei", "Alt rând"])[0] == "trece"
    assert VP.compara_asertiune("rand_propriu", v, ["Alt rând Diferență neexplicată: 1.341,00 lei", "TVA de plată"])[0] == "pica"   # A și B în rânduri diferite / alt început
    assert VP.compara_asertiune("rand_propriu", v, ["TVA de plată x", "Diferență neexplicată: 1.341,00 lei"])[0] == "pica"
    assert VP.compara_asertiune("rand_propriu", v, ["TVA de plată Diferență neexplicată: 1.341,00 lei"] * 2)[0] == "pica"   # duplicat
    assert VP.compara_asertiune("rand_propriu", v, [])[0] == "pica"
    assert VP.compara_asertiune("rand_propriu", "fără separator", ["fără separator"])[0] == "pica"


# ---- citirea din pagină ---------------------------------------------------------------------------------------------------------------------------------------------------------
_RANDURI = '<div id="c"><div class="r">Stocuri în regulă<div class="sub">Ciorne de stoc 3.251,90 lei</div></div><div class="r">Ciorne de stoc 3.251,90 lei</div></div>'


def test_rand_propriu_pe_pagina_randul_propriu_trece_iar_sub_randul_altuia_pica(VP, pagina):
    obs = _citeste(VP, pagina, _RANDURI, "dom:#c|randuri:.r", "rand_propriu")
    assert VP.compara_asertiune("rand_propriu", "Ciorne de stoc && 3.251,90 lei", obs)[0] == "trece"
    comb = '<div id="c"><div class="r">Stocuri în regulă<div class="sub">Ciorne de stoc 3.251,90 lei</div></div></div>'
    obs = _citeste(VP, pagina, comb, "dom:#c|randuri:.r", "rand_propriu")
    assert VP.compara_asertiune("rand_propriu", "Ciorne de stoc && 3.251,90 lei", obs)[0] == "pica"


def test_rand_propriu_ignora_randul_ascuns_si_pica_pe_selector_lipsa_sau_duplicat(VP, pagina):
    for ascuns in ('style="display:none"', "hidden", 'aria-hidden="true"', 'style="visibility:hidden"'):
        html = '<div id="c"><div class="r" %s>Ciorne de stoc 3.251,90 lei</div></div>' % ascuns
        obs = _citeste(VP, pagina, html, "dom:#c|randuri:.r", "rand_propriu")
        assert VP.compara_asertiune("rand_propriu", "Ciorne de stoc && 3.251,90 lei", obs)[0] == "pica", ascuns
    obs = _citeste(VP, pagina, _RANDURI, "dom:#nu_exista|randuri:.r", "rand_propriu")
    assert VP.compara_asertiune("rand_propriu", "Ciorne de stoc && 3.251,90 lei", obs)[0] == "pica"
    dub = '<div id="c"><div class="r">Ciorne de stoc 3.251,90 lei</div><div class="r">Ciorne de stoc 3.251,90 lei</div></div>'
    obs = _citeste(VP, pagina, dub, "dom:#c|randuri:.r", "rand_propriu")
    assert VP.compara_asertiune("rand_propriu", "Ciorne de stoc && 3.251,90 lei", obs)[0] == "pica"


_TEXT = "Nota e deja validată: nu se mai validează."


def test_text_vizibil_trece_pe_text_vizibil_in_fereastra(VP, pagina):
    obs = _citeste(VP, pagina, '<div class="f"><p id="jn-validata">%s</p><table><tr><td>x</td></tr></table></div>' % _TEXT, "dom:.f|text", "text_vizibil")
    assert VP.compara_asertiune("text_vizibil", _TEXT, obs)[0] == "trece"


@pytest.mark.parametrize("ascuns", ['<p style="display:none">%s</p>', '<p hidden>%s</p>', '<p style="visibility:hidden">%s</p>', '<div aria-hidden="true"><p>%s</p></div>',
                                    '<details><summary>Detalii</summary><p>%s</p></details>'])
def test_text_vizibil_pica_pe_text_ascuns_sau_in_detaliu_inchis(VP, pagina, ascuns):
    obs = _citeste(VP, pagina, '<div class="f">%s</div>' % (ascuns % _TEXT), "dom:.f|text", "text_vizibil")
    assert VP.compara_asertiune("text_vizibil", _TEXT, obs)[0] == "pica"
    # același text rămâne «găsit» de operatorul vechi pe textContent (semantică neschimbată)
    vechi = _citeste(VP, pagina, '<div class="f">%s</div>' % (ascuns % _TEXT), "dom:.f|text", "text_contine")
    assert VP.compara_asertiune("text_contine", _TEXT, vechi)[0] == "trece"


def test_text_vizibil_pica_pe_text_sub_linia_de_derulare(VP, pagina):
    html = '<div class="f"><div style="height:1500px">tabel</div><p>%s</p></div>' % _TEXT
    obs = _citeste(VP, pagina, html, "dom:.f|text", "text_vizibil")
    assert VP.compara_asertiune("text_vizibil", _TEXT, obs)[0] == "pica"
    sus = '<div class="f"><p>%s</p><div style="height:1500px">tabel</div></div>' % _TEXT
    obs = _citeste(VP, pagina, sus, "dom:.f|text", "text_vizibil")
    assert VP.compara_asertiune("text_vizibil", _TEXT, obs)[0] == "trece"


def test_text_vizibil_pica_pe_text_taiat_de_un_container_cu_derulare(VP, pagina):
    html = '<div class="f" style="height:50px;overflow:auto"><div style="height:400px">tabel</div><p>%s</p></div>' % _TEXT
    obs = _citeste(VP, pagina, html, "dom:.f|text", "text_vizibil")
    assert VP.compara_asertiune("text_vizibil", _TEXT, obs)[0] == "pica"


def test_text_vizibil_selector_lipsa_pica(VP, pagina):
    obs = _citeste(VP, pagina, '<div class="f"><p>%s</p></div>' % _TEXT, "dom:.nu_exista|text", "text_vizibil")
    assert VP.compara_asertiune("text_vizibil", _TEXT, obs)[0] == "pica"


def test_masura_text_a_celorlalti_operatori_citeste_neschimbat_textContent(VP, pagina):
    pagina.set_content('<div class="f"><p hidden>ascuns</p><p>vizibil</p></div>')
    assert VP.observa_pagina(pagina, "dom:.f|text", "/tmp")[1] == "ascunsvizibil"
    assert VP.observa_pagina(pagina, "dom:.f|text", "/tmp", "text_contine")[1] == "ascunsvizibil"
