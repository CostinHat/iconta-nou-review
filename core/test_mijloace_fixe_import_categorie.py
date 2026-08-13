# -*- coding: utf-8 -*-
"""Import mijloace fixe: cont_imobilizare lipsa NU se mai completeaza tacit cu 2131.

Inainte, un activ fara cont primea 2131 (echipamente = categoria cea mai permisiva, lit.b) ->
i se permitea accelerat/superaccelerat desi categoria era necunoscuta. Acum: cont lipsa ramane
gol + avertisment; gol -> categoria lit.c la calc_asset (doar liniar/degresiv), deci metodele
ne-permise sunt refuzate pana se completeaza contul. (CF art.28 alin.5.)
"""
from datetime import date

from core.mijloace_fixe_import_api import extrage
from core import d406_active as m


def _dupa_db(r):
    """Simuleaza round-trip-ul prin DB: data_pif ajunge la calc_asset ca obiect date
    (extrage() intoarce isoformat pt stratul de preview; endpoint-ul citeste date din DB)."""
    r = dict(r)
    if isinstance(r.get("data_pif"), str):
        r["data_pif"] = date.fromisoformat(r["data_pif"])
    return r

_CU_CONT = b"cod;denumire;valoare;durata;pif;metoda;cont imobilizare\nMF1;Strung;100000;60;2025-12-20;accelerata;2131"
_FARA_CONT = b"cod;denumire;valoare;durata;pif;metoda\nMF1;Ceva;100000;60;2025-12-20;accelerata"


def test_cont_prezent_se_pastreaza():
    r = extrage(_CU_CONT, "mf.csv")[0]
    assert r["cont_imobilizare"] == "2131"
    assert not any("cont_imobilizare lipsa" in a for a in r["avertismente"])


def test_cont_lipsa_ramane_gol_nu_2131():
    r = extrage(_FARA_CONT, "mf.csv")[0]
    assert r["cont_imobilizare"] == "", "cont completat tacit: %r" % r["cont_imobilizare"]
    assert r["cont_imobilizare"] != "2131"


def test_cont_lipsa_da_avertisment_si_ok_false():
    r = extrage(_FARA_CONT, "mf.csv")[0]
    assert any("cont_imobilizare lipsa" in a for a in r["avertismente"]), r["avertismente"]
    assert r["ok"] is False


def test_activ_neclasificat_refuza_accelerat_la_d406():
    """Consecinta ceruta: fara cont, metoda accelerata (din fisier) e refuzata (lit.c), nu permisa."""
    r = _dupa_db(extrage(_FARA_CONT, "mf.csv")[0])
    assert r["metoda"] == "accelerata"     # metoda vine din fisier, neschimbata
    try:
        m.calc_asset(r, 2026)
        assert False, "activ neclasificat cu accelerata trebuia refuzat"
    except ValueError as e:
        assert "nu e permisa de lege" in str(e)


def test_activ_neclasificat_permite_liniar():
    """Liniarul e permis pentru orice categorie -> un activ neclasificat NU e refuzat la liniar."""
    r = _dupa_db(extrage(_FARA_CONT, "mf.csv")[0])
    r["metoda"] = "liniara"
    r["rezidual"] = 0                      # fisierul n-avea coloana rezidual (default = valoare)
    v = m.calc_asset(r, 2026)              # nu ridica -> liniarul e permis pentru categoria lit.c
    assert v["depr_period"] > 0
