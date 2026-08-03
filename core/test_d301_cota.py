# -*- coding: utf-8 -*-
"""
Gard period-aware pe cota de TVA oferita la introducerea operatiunilor D301.

TEMEI: CF art.291 — cota standard alin.(1) = 21% (de la 01.08.2025, Legea 141/2025;
19% intre 2017 si 31.07.2025); cota redusa alin.(2) = 11% (de la 01.08.2025). INAINTE de
01.08.2025 reducerile erau 9% si 5% (comasate in 11% de Legea 141/2025, pct.42-43).
art.291 alin.(8): cota achizitiei intracomunitare = cota livrarii interne a aceluiasi bun,
deci cota redusa CHIAR se poate aplica in D301.

DEFECT reparat: cote_perioada oferea cota redusa ca literal fix 11, indiferent de perioada,
in timp ce standardul era period-aware. Pentru o luna D301 dinainte de 08.2025 (rectificativa)
optiunea '11% redusa' era gresita legal. Fix: redusa din common.cota('tva_redusa', data);
daca nu e configurata pt perioada -> se omite (nu se ofera un 11% fals). Cele doua cote reduse
istorice coexistente (9%/5%) cer remodelare COTE = decizie de produs (nesolutionata aici).
"""
from core import d301_operatiuni_api as api


def test_cote_2026_standard_21_redusa_11_scutit_0():
    # Perioada curenta (post Legea 141/2025): 21% standard, 11% redusa, 0% scutit. NESCHIMBAT.
    vals = [c["val"] for c in api.cote_perioada(2026, 8)]
    assert vals == [21, 11, 0], vals


def test_cote_redusa_period_aware_nu_ofera_11_pe_perioada_veche():
    # 2025-06: standardul e 19%, iar reducerile de ATUNCI erau 9%/5% - NU 11%.
    # cote_perioada nu trebuie sa ofere '11% redusa' pt o luna dinainte de 01.08.2025.
    vals = [c["val"] for c in api.cote_perioada(2025, 6)]
    assert 19 in vals, "standardul 2025-06 trebuie sa fie 19%%: %r" % (vals,)
    assert 11 not in vals, "ofera 11%% redusa gresit pt 2025-06 (atunci: 9%%/5%%): %r" % (vals,)
    assert 0 in vals, "scutit 0%% trebuie sa ramana: %r" % (vals,)


def test_adauga_respinge_cota_11_pe_perioada_veche():
    # Consecinta de poarta: o cota 11% pe o luna pre-08.2025 e respinsa (nu se persista un tva gresit).
    class _Cur:
        def __enter__(self): return self
        def __exit__(self,*a): return False
        def execute(self,*a,**k): pass
        def fetchone(self): return [1]
    class _Conn:
        def cursor(self,*a,**k): return _Cur()
        def commit(self): pass
    r = api.adauga(_Conn(), "public", 2025, 6,
                   {"tip":1,"tip_valuta":"EUR","val_valuta":"100","curs":"4.97",
                    "cota":11,"nr_doc":"F1","data_doc":"10.06.2025"})
    assert "eroare" in r and "cota" in r["eroare"].lower(), r
