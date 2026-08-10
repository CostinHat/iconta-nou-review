# -*- coding: utf-8 -*-
"""GARD: D301 data_doc emis in formatul OFICIAL ANAF ZZ.LL.AAAA (anaf_surse/d301_struct_anaf.txt poz.35, C(10)).
Generatorul normalizeaza din orice sursa (date/ISO/canonic). DUK respinge ISO ('AAAA-LL-ZZ').
Mutatie: cod vechi emitea data_doc brut (ISO) -> assert pica.
"""
import datetime
from core.d301 import calcul_d301
from core.common import Perioada

_PROF = {"nume": "X SRL", "cui": "14399840", "adresa": "Str 1"}


def _op(data_doc):
    return {"tip": 1, "nr_doc": "1", "data_doc": data_doc, "val_valuta": 100.0,
            "tip_valuta": "EUR", "curs": 5.0, "tva": 0}


def test_data_doc_iso_normalizat():
    res = calcul_d301(_PROF, Perioada(2026, luna=8), [_op("2026-08-12")])
    assert res.operatiuni[0].data_doc == "12.08.2026", res.operatiuni[0].data_doc


def test_data_doc_date_obiect_normalizat():
    res = calcul_d301(_PROF, Perioada(2026, luna=8), [_op(datetime.date(2026, 8, 12))])
    assert res.operatiuni[0].data_doc == "12.08.2026", res.operatiuni[0].data_doc


def test_data_doc_deja_canonic_pastrat():
    res = calcul_d301(_PROF, Perioada(2026, luna=8), [_op("12.08.2026")])
    assert res.operatiuni[0].data_doc == "12.08.2026", res.operatiuni[0].data_doc
