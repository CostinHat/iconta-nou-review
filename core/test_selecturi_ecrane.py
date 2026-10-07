# -*- coding: utf-8 -*-
"""GARD — FAPT_FISCAL_NECERUT în ecranele scrise de mână (comanda Costin 07.10.2026: „Extinde regula la ecranele scrise de mână, cu
clasificarea celor 82”; DS cap.17).

Instanța: în afara registrului Operațiunilor, 82 de selecturi veneau cu prima opțiune aleasă. 59 erau fapte fiscale (declarații manuale,
moneda / țara / tipul operației la emitere, tipul firmei, S1005/S1003, categoria dispoziției de casă, codul CM, RIP, eTransport …):
acum pornesc cu „— alege —” și handlerul refuză trimiterea fără alegere, lângă câmp. Celelalte 23 sunt clasificate, fiecare cu
motivul (ne-fiscale, valoare existentă, opțiune goală în builder, un conflict DS). Instrumentul: `scripts/scan_selecturi_ecrane.py`
(același cu regula din verificator).

[lotul 07.10 B, comanda Costin A] Regula CORECTATĂ: preselecția e permisă când valoarea e uzuală sau dedusă, vizibilă și schimbabilă
(`PRESELECTAT_PERMIS`, criteriile scrise în motiv); interzisă pentru faptul situațional. Plus trei clase noi ale aceluiași implicit:
căsuța de bifat (nebifată = „Nu” ales de ecran) -> `selectDaNu`; input-ul precompletat -> `INPUTURI`; faptul din Date firmă fără
implicit în schemă -> cerut la prima folosire.
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
    """MUTAȚIE: „— alege —” scos de la forma de organizare D204 -> pică; `#d208-mod` scos din `cereAlegerile` -> pică."""
    assert S.masoara() == []


def test_clasificarea_acopera_cele_82_si_fiecare_are_motiv():
    toate = S.selecturi()
    assert len(toate) >= 100                                   # premisă: selecturile chiar se văd (108 măsurate)
    clase = collections.Counter(c for c, _m in S.CLASIFICARE.values())
    # 82 de selecturi (81 de chei: `je-centru` de două ori) + lotul 07.10 B: D204 forma, D208 modalitatea, helperul `selectDaNu`;
    # 6 fapte trecute la PRESELECTAT_PERMIS (emiterea ×4, factura recurentă, D318 tipul cererii) + destinația pe linie (fost CONFLICT)
    assert clase[S.FISCAL] == 55 and clase[S.PRESELECTAT] == 7 and sum(clase.values()) == 84
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
    p = "static/js/ecrane/firme.js"
    s = _js(p)
    a = '<select class="camp-input" id="fn-tip">${ALEGE}'
    assert s.count(a) == 1
    rele = dict(S.masoara([(p, s.replace(a, '<select class="camp-input" id="fn-tip">'))]))
    assert rele.get("firme.js:fn-tip", "").startswith("fapt fiscal fără")


def test_CALIBRARE_select_fiscal_necerut_de_handler_e_prins():
    p = "static/js/ecrane/declaratii.js"
    s = _js(p)
    a = 'cereAlegerile(zona, ["#d208-mod", "#d208-tip"])'
    assert s.count(a) == 1
    rele = dict(S.masoara([(p, s.replace(a, 'cereAlegerile(zona, ["#d208-tip"])'))]))
    assert rele.get("declaratii.js:d208-mod", "").startswith("fapt fiscal pe care handlerul nu-l cere")


def test_preselectiile_permise_isi_scriu_criteriile():
    """DS cap.17 corectat: o preselecție e permisă numai cu (a) uzual/dedus, (b) vizibil, (c) schimbabil — scrise în motiv."""
    pres = {k: m for k, (c, m) in S.CLASIFICARE.items() if c == S.PRESELECTAT}
    assert sorted(pres) == ["declaratii.js:d318-drec", "emitere_ecran.js:em-moneda", "emitere_ecran.js:em-tara", "emitere_ecran.js:em-tip",
                            "emitere_ecran.js:em-tipop", "facturi_ecran.js:fr-moneda", "facturi_ecran.js:pr-dest"]
    assert [k for k, m in pres.items() if not all(x in m for x in ("(a)", "(b)", "(c)"))] == []


def test_CALIBRARE_preselectat_cu_alege_e_prins():
    p = "static/js/ecrane/emitere_ecran.js"
    s = _js(p)
    a = '<select class="camp-input" id="em-moneda">'
    assert s.count(a) == 1
    rele = dict(S.masoara([(p, s.replace(a, a + "${ALEGE}"))]))
    assert rele.get("emitere_ecran.js:em-moneda", "").startswith("clasificat preselectat permis")


def test_tara_la_emitere_e_dedusa_din_cui():
    """(a) „se deduce din date (țara din CUI-ul partenerului)”: schimbarea CUI-ului pune țara, vizibil."""
    s = _js("static/js/ecrane/emitere_ecran.js")
    assert re.search(r'const taraDinCui = \(cui\) =>', s) and re.search(r'querySelector\("#em-cui"\)\.addEventListener\("change"', s)


def test_CALIBRARE_casuta_noua_neclasificata_e_prinsa():
    """Un DA/NU situațional pus ca o căsuță (nebifată = „Nu” ales de ecran) pică; MUTAȚIE: `cm-spital` înapoi la căsuță -> pică."""
    assert [k for k, _l in S.casute([("static/js/ecrane/nou.js", '<input type="checkbox" id="x-imputabil">')])] == ["nou.js:x-imputabil"]
    assert S.CASUTE.get("nou.js:x-imputabil") is None


def test_casutele_ramase_sunt_toate_clasificate():
    gasite = {k for k, _l in S.casute()}
    assert len(gasite) >= 25                                    # premisă: căsuțele chiar se văd (31 măsurate)
    assert sorted(gasite - set(S.CASUTE)) == [] and sorted(set(S.CASUTE) - gasite) == []


def test_CALIBRARE_danu_necerut_e_prins():
    p = "static/js/ecrane/flux_concediu.js"
    s = _js(p)
    a = '["#cm-cod", "#cm-continuare", "#cm-spital", "#cm-program-national"]'
    assert s.count(a) == 1
    rele = dict(S.danu_necerute([(p, s.replace(a, '["#cm-cod", "#cm-continuare", "#cm-program-national"]'))]))
    assert rele.get("flux_concediu.js:cm-spital", "").startswith("DA/NU situațional pe care handlerul nu-l cere")


def test_inputurile_precompletate_sunt_clasificate():
    gasite = {k for k, _l in S.inputuri_precompletate()}
    assert len(gasite) >= 5 and sorted(gasite ^ set(S.INPUTURI)) == []


def test_CALIBRARE_input_precompletat_neclasificat_e_prins():
    """MUTAȚIE: D204 categoria înapoi la `|| 1` -> apare (ca la D216 cota „0.3”, care era cota impozitului în câmpul cotei de deținere)."""
    gasite = S.inputuri_precompletate([("static/js/ecrane/nou.js",
                                        """'<input id="x-categ" type="number" class="camp-input" value="' + esc(String(ac.categ || 1)) + '">'""")])
    assert [k for k, _l in gasite if k.startswith("nou.js")] == ["nou.js:x-categ"]


def test_d398_moneda_e_fixa_prin_lege():
    """CF art.314 alin.(10) / art.315 alin.(12) / art.315^2 alin.(22): „Declarația specială de TVA se întocmește în euro.”"""
    from core import d398
    assert d398.MONEDA_OSS == "EUR"                                    # CF art.314 alin.(10)
    js = _js("static/js/ecrane/declaratii.js")
    assert re.search(r'id="d398-cur" type="text" class="camp-input" value="EUR" readonly', js)


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
