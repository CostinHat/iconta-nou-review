# -*- coding: utf-8 -*-
"""429 — AJUSTAREA MANUALĂ ÎN ACELAȘI FORMULAR (lotul 11, comanda Costin 11.1 pct.11, verbatim în DECIZII „Comanda 11.1”: „429:
reevaluarea în valută e neschimbată pe producție (formular manual, fără propunere, fără curs BNR, nimic la închiderea lunii)”; sarcina:
„un singur formular de reevaluare, întotdeauna cu propunerea, cursul BNR, diferența pe 665/765 [...] Fără formular manual paralel
(dacă rămâne o ajustare manuală, e în același formular, marcată)”).

Până la lotul 11 formularul manual era o rută separată (`POST /tenants/{id}/reevaluare-valuta`, Operațiuni → „Reevaluare lunară solduri
valută”): soldul, moneda și cursul din evidență scrise de mână, fără propunere. Acum ruta nu mai există; un cont pe care aplicația nu-l
propune se adaugă în propunere (`manuale`), cu moneda și soldul în valută; soldul în lei vine din evidență, nu se scrie.

Temei: OMFP 1802/2014 pct.325 alin.(1) (creanțele și datoriile în valută, lunar, la cursul BNR din ultima zi bancară) și alin.(3)
(„creanțelor și datoriilor exprimate în lei, a căror decontare se face în funcție de cursul unei valute [...] alte venituri financiare
sau alte cheltuieli financiare”: 768 / 668); pct.316 alin.(2): avansurile (409, 419) „nu mai fac obiectul evaluării în funcție de cursul
valutar, la finele lunii”. Fixtura și perioadele sintetice 2099: `core/test_lot10_reevaluare.py`.
"""
import pytest

from core.test_lot10_reevaluare import CTX, SCH, _db_ok, _el, _linii, _nota, _valideaza, firma   # noqa: F401 — fixtura, refolosită

pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def cu_imprumut(firma):   # noqa: F811
    """Un credit bancar în EUR, 1.000 EUR primiți la 4,97 (5121 = 1621 4.970,00), și o creanță în lei cu clauză în EUR (461 = 5121
    1.000,00) — conturi pe care propunerea nu le știe (n-au factură, nu sunt disponibilități)."""
    from core import db
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        _nota(cur, "2099-09-03", [("5121", "1621", 4970)], doc="Contract credit 1")
        _nota(cur, "2099-09-04", [("461", "5121", 1000)], doc="Contract 461")
        c.commit()
    return firma


def test_ruta_formularului_manual_nu_mai_exista():
    """Un singur formular: ruta veche (POST pe `/reevaluare-valuta`) și use-case-ul ei au plecat. MUTAȚIE: ruta pusă la loc în main.py."""
    import io
    import os
    import re
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main = io.open(os.path.join(rad, "main.py"), encoding="utf-8").read()
    assert not re.search(r'@app\.post\("/tenants/\{tenant_id\}/reevaluare-valuta"\)', main)
    from core import uc_tenants
    assert not hasattr(uc_tenants, "reevaluare_valuta")
    ops = io.open(os.path.join(rad, "static", "js", "ecrane", "operatiuni_ecran.js"), encoding="utf-8").read()
    assert 'ruta: "reevaluare-valuta"' not in ops, "Operațiuni are încă formularul manual al reevaluării"


def test_contul_adaugat_manual_intra_in_propunere_cu_soldul_in_lei_din_evidenta(cu_imprumut):
    """MUTAȚIE: în `_elemente_conturi`, `manuale_conturi = sorted(...)` -> `[]` -> rândul manual nu mai intră -> pică."""
    from core import uc_reevaluare
    p = uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 9, CTX, manuale='[{"cont": "1621", "moneda": "EUR", "sold_valuta": "1000"}]')
    m = _el(p, "m1621")
    # OMFP 1802/2014 pct.325 alin.(1): datoria de 1.000 EUR, în evidență 4.970,00 lei, la BNR 5,00 = 5.000,00 -> crește -> 665
    assert (m["manual"], m["fel"], m["lei_evidenta"], m["curs_evidenta"], m["lei_bnr"], m["diferenta"], m["cont_diferenta"]) == (
        True, "datorie", "4970.00", "4.9700", "5000.00", "30.00", "665"), m
    assert m["rand_manual"] == 0


def test_toate_refuzurile_randurilor_manuale_vin_deodata_langa_camp(cu_imprumut):
    """Contul de avansuri (pct.316 alin.(2)), contul unui partener, o disponibilitate deja propusă, un cont fără sold, un cont lipsă —
    cinci rânduri, cinci refuzuri, fiecare pe câmpul lui. MUTAȚIE: `_e_avans` scos din `_refuz_rand_manual` -> 409 trece -> pică."""
    import json
    from core import erori, uc_reevaluare
    randuri = [{"cont": "409", "moneda": "EUR", "sold_valuta": "10"}, {"cont": "4111", "moneda": "EUR", "sold_valuta": "10"},
               {"cont": "5124.EUR", "moneda": "EUR", "sold_valuta": "10"}, {"cont": "167", "moneda": "EUR", "sold_valuta": "10"},
               {"cont": "", "moneda": "EUR", "sold_valuta": "10"}]
    with pytest.raises(erori.DateInvalide) as e:
        uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 9, CTX, manuale=json.dumps(randuri))
    d = e.value.detaliu
    assert [x["camp"] for x in d["erori_campuri"]] == ["rv-m%d-cont" % i for i in range(5)], d
    # OMFP 1802/2014 pct.316 alin.(2): avansurile „nu mai fac obiectul evaluării în funcție de cursul valutar, la finele lunii”
    assert d["erori_campuri"][0] == {"camp": "rv-m0-cont", "mesaj": "Contul 409 e de avansuri: avansurile nu se reevaluează la curs la "
                                     "sfârșitul lunii (OMFP 1802/2014 pct.316 alin.(2))."}, d   # câmpul întreg (core/test_garzi_pe_text.py)


def test_clauza_in_lei_merge_pe_768_si_luna_urmatoare_contul_revine(cu_imprumut):
    """OMFP 1802/2014 pct.325 alin.(3): creanța în lei cu clauză valutară -> „alte venituri financiare” (768). Luna următoare contul revine
    singur, cu moneda știută și soldul în valută cerut din nou. MUTAȚIE: `in_lei_cu_clauza=bool(el.get("clauza"))` -> `False` -> 765."""
    from core import uc_reevaluare
    man = [{"cont": "461", "moneda": "EUR", "sold_valuta": "210", "clauza": True}]
    r = uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9, "manuale": man,
                                                     "completari": {"c5124.EUR": {"sold_valuta": "990"}}}, CTX)
    # 210 EUR x 5,00 = 1.050,00; în evidență 1.000,00 -> +50,00 -> 461 = 768 (pct.325 alin.(3))
    assert ("461", "768", "50.00") in _linii(r["inregistrare_id"]), _linii(r["inregistrare_id"])
    _valideaza(r["inregistrare_id"])
    p = uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 10, CTX)
    m = _el(p, "m461")
    assert (m["manual"], m["moneda"], m["sold_valuta"], m["sold_anterior"], m["clauza"], m["de_completat"]) == (
        True, "EUR", None, "210.00", True, ["sold_valuta"]), m


def test_clauza_neleasa_la_contul_adaugat_acum_opreste_generarea_langa_camp(cu_imprumut):
    """[lotul 11, K — DS cap.17 v2.79, FAPT_FISCAL_NECERUT] Clauza valutară a unui cont adăugat acum e un DA/NU situațional: 765/665 sau
    768/668 (OMFP 1802/2014 pct.325 alin.(3)) nu se alege în locul omului. Propunerea îl arată „de completat”, iar generarea se refuză
    lângă câmpul rândului. MUTAȚIE: `el["clauza"] = None` scos din `_elemente_conturi` -> clauza devine „Nu” implicit -> pică."""
    from core import erori, uc_reevaluare
    p = uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 9, CTX, manuale='[{"cont": "461", "moneda": "EUR", "sold_valuta": "210"}]')
    assert _el(p, "m461")["de_completat"] == ["clauza"], _el(p, "m461")
    with pytest.raises(erori.DateInvalide) as e:
        uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9, "manuale": [{"cont": "461", "moneda": "EUR", "sold_valuta": "210"}],
                                                     "completari": {"c5124.EUR": {"sold_valuta": "990"}}}, CTX)
    d = e.value.detaliu
    assert [x["camp"] for x in d["erori_campuri"]] == ["rv-m0-clauza"], d
    assert d["erori_campuri"][0]["mesaj"].startswith("completează dacă soldul e în lei cu clauză valutară (Da / Nu) pe contul 461"), d
    # ales „Nu” explicit: nu mai e de completat
    p = uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 9, CTX, manuale='[{"cont": "461", "moneda": "EUR", "sold_valuta": "210", '
                                                                         '"clauza": false}]')
    assert _el(p, "m461")["de_completat"] == [], _el(p, "m461")
