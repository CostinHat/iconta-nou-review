"""[696.1, comanda 14.3] Fișa de magazie: ieșirea scrisă are valoarea ei din notă; soldul fișei = intrări − ieșiri, exact (fără 0,36 lei de rotunjire)."""
from decimal import Decimal as D

from core import stocuri_cv as cv


def test_iesirea_scrisa_intra_in_fisa_cu_valoarea_din_nota_nu_la_cmp_nerotunjit():
    # 3 intrări cu CMP 51,19047... ; iesirile sunt scrise la valorile notelor (rotunjite la ban)
    m = [{"id": 1, "tip": "intrare", "cantitate": D("210"), "pret_unitar": D("51.19"), "valoare": D("10749.90"), "data": "2026-10-01"},
         {"id": 2, "tip": "iesire", "cantitate": D("88"), "valoare": D("4505.00"), "data": "2026-10-05"}]
    f = cv.fisa_magazie(m)
    assert f[-1]["sold_valoare"] == D("10749.90") - D("4505.00") == D("6244.90")
    assert f[-1]["sold_cantitate"] == D("122")


def test_iesirea_ipotetica_fara_id_se_evalueaza_la_cmp_ca_inainte():
    m = [{"id": 1, "tip": "intrare", "cantitate": D("10"), "pret_unitar": D("10"), "valoare": D("100.00"), "data": "2026-10-01"},
         {"tip": "iesire", "cantitate": D("5"), "data": "2026-10-02"}]
    assert cv.fisa_magazie(m)[-1]["sold_valoare"] == D("50.00")
