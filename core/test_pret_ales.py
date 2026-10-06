# -*- coding: utf-8 -*-
"""GARD — „un preț pe care nu l-a ales nimeni nu se propune: câmp gol și obligatoriu” (comanda Costin 06.10.2026, pct.1b).

Instanța (retestul F1 ca Ana): pe factură, prețul 100 al articolului „Marfa A” rămânea pe rândul rescris „Carte – Ghid contabil
2026”; un câmp de preț golit pleca drept 0; linia fără preț intra la server cu 0 (`LinieEmitereIn.pret_unitar = 0`). Clasa:
emiterea, factura recurentă, intrarea în stoc. Ce face IMPOSIBIL: o linie de factură / o intrare în stoc fără preț scris ajunge
în evidență cu o valoare. LIMITA: 0 SCRIS de om rămâne permis — nu se poate deosebi de aici un 0 scris de unul trimis de un
integrator care l-a pus implicit (API v1); refuzul prinde doar LIPSA. Partea din ecran: verificator `PRET_SAU_ARTICOL_NEALES`.
"""
import ast
import os

from core import facturi_api, stocuri_cv_api

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _campuri(linii, prefix="em-l"):
    return {x["camp"] for x in facturi_api.linii_campuri_lipsa(linii, prefix=prefix)}


def test_linia_fara_pret_se_refuza_langa_camp():
    """MUTAȚIE: verificarea prețului scoasă din `linii_campuri_lipsa` -> pică."""
    # Temei: CF art.319 alin.(20) lit.i — factura cuprinde obligatoriu „prețul unitar, exclusiv taxa”.
    for fara in ({}, {"pret_unitar": None}, {"pret_unitar": ""}, {"pret_unitar": "  "}):
        assert "em-l0-pret_unitar" in _campuri([dict({"descriere": "Carte – Ghid contabil 2026", "cantitate": 2}, **fara)])


def test_pretul_zero_scris_de_om_ramane_permis():
    assert "em-l0-pret_unitar" not in _campuri([{"descriere": "Mostră", "cantitate": 1, "pret_unitar": 0}])
    assert "em-l0-pret_unitar" not in _campuri([{"descriere": "Mostră", "cantitate": 1, "pret_unitar": "0"}])


def test_factura_recurenta_fara_pret_se_refuza_pe_campul_ei():
    """Același contract pe șablonul facturii recurente (prefixul `fr-l`)."""
    assert "fr-l0-pret_unitar" in _campuri([{"descriere": "Abonament", "cantitate": 1}], prefix="fr-l")


def _implicit(clasa, camp):
    arbore = ast.parse(open(os.path.join(RAD, "main.py"), encoding="utf-8").read())
    for n in ast.walk(arbore):
        if isinstance(n, ast.ClassDef) and n.name == clasa:
            for st in n.body:
                if isinstance(st, ast.AnnAssign) and getattr(st.target, "id", None) == camp:
                    return ast.unparse(st.annotation), (ast.unparse(st.value) if st.value is not None else "<obligatoriu>")
    raise AssertionError("%s.%s negăsit" % (clasa, camp))


def test_modelele_nu_pun_un_pret_implicit():
    """MUTAȚIE: `pret_unitar: float = 0` repus în `LinieEmitereIn` -> pică."""
    assert _implicit("LinieEmitereIn", "pret_unitar") == ("Optional[float]", "None")
    assert _implicit("ProdusCreeazaIn", "pret_unitar") == ("Optional[float]", "None")


def test_intrarea_in_stoc_fara_pret_se_refuza_inainte_de_a_crea_articolul():
    """`conn=None`: refuzul vine ÎNAINTE de orice interogare (înainte, articolul nou se crea și abia apoi se valida prețul,
    iar `Decimal(str(None))` ieșea 500). MUTAȚIE: verificarea scoasă -> `None.cursor` -> AttributeError -> pică."""
    for fara in ({}, {"pret_unitar": None}, {"pret_unitar": ""}):
        r = stocuri_cv_api.intrare(None, "tenant_x", dict({"denumire": "Articol nou", "cantitate": 1, "data": "2099-01-01"}, **fara))
        assert "Prețul unitar al intrării lipsește" in r["eroare"]
