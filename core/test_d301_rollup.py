# -*- coding: utf-8 -*-
"""Regresie D301: serviciile intracomunitare (tip 5 = sectiunea 4.1) se preiau DIN sectiunea 4.

OPANAF 592/2016, instructiunile formularului 301: "In sectiunea 4.1 se preiau DIN sectiunea 4
doar achizitiile de servicii intracomunitare pentru care beneficiarul e obligat la plata TVA cf.
art. 307 alin. (2)". Deci S4.1 e SUBSET al S4. Fara rollup, baza4=0 cand exista servicii, iar
DUKIntegrator respinge (R32: "4.1 fara 4"; R24/R25: baza4 != suma sectiunilor tip 4). Testul ar
fi prins regresia care a scapat validarii initiale (validata pe un caz FARA tip 5).
"""
from core.common import Perioada
from core import d301

PROF = {"nume": "TEST SRL", "cui": "RO12345678", "banca": "BCR",
        "iban": "RO49AAAA1B31007593840000", "adresa": "Str 1", "oras": "Buc", "judet": "B",
        "declarant_nume": "POP", "declarant_prenume": "ION", "declarant_functie": "ADMIN"}


def _op(tip, val, curs, tva):
    return {"tip": tip, "nr_doc": "DOC1", "data_doc": "15.06.2026",
            "val_valuta": val, "tip_valuta": "EUR", "curs": curs, "tva": tva}


def test_tip5_se_preia_in_sectiunea_4():
    # 1000 x 4.9770 = 4977 baza; TVA 1045 (cota 21%)
    res = d301.calcul_d301(PROF, Perioada(2026, luna=6), [_op(5, 1000, 4.9770, 1045)])
    assert res.totaluri[5] == (4977, 1045)          # S4.1
    assert res.totaluri[4] == (4977, 1045)          # REGRESIA: S4 CONTINE S4.1 (era (0, 0))


def test_tip5_emite_sectiune_4_si_4_1_in_xml():
    res = d301.calcul_d301(PROF, Perioada(2026, luna=6), [_op(5, 1000, 4.9770, 1045)])
    xml = d301.build_xml(res)
    assert 'baza4="4977"' in xml and 'baza5="4977"' in xml
    # o operatiune tip 5 emite AMBELE randuri (sectiune 4 membership + 4.1 detaliu)
    assert xml.count('tip_operatie="4"') == 1
    assert xml.count('tip_operatie="5"') == 1
    # totalPlata_A = formula oficiala baza1..5 + tva1..5 (suma de control)
    assert 'totalPlata_A="12044"' in xml


def test_tva_datorat_o_singura_data_desi_checksum_include_4_1():
    # Grija fiscala corecta: TVA-ul DATORAT nu se dubleaza. tva4 (sectiunea 4, serviciul o
    # SINGURA data prin rollup) = 1045, NU 2090. In schimb totalPlata_A e SUMA DE CONTROL
    # (checksum ANAF: baza1..5 + tva1..5, structura poz.28), impusa de DUK regula R28 -
    # include 4.1 PRIN DEFINITIE (dovedit numeric: DUK respinge un total pe sectiunile 1-4).
    res = d301.calcul_d301(PROF, Perioada(2026, luna=6), [_op(5, 1000, 4.9770, 1045)])
    assert res.totaluri[4][1] == 1045               # TVA DATORAT (S4) - serviciul o data
    assert res.totaluri[5][1] == 1045               # detaliul 4.1 (aceeasi suma, nu in plus)
    assert res.total_plata_a == 12044               # checksum ANAF = baza4+baza5+tva4+tva5


def test_tip5_plus_tip4_cumuleaza_in_sectiunea_4():
    # S4 = S4.2 (tip 4) + S4.1 (tip 5)
    res = d301.calcul_d301(PROF, Perioada(2026, luna=6), [_op(4, 2000, 5.0, 2100), _op(5, 1000, 5.0, 1050)])
    assert res.totaluri[5][0] == 5000               # tip 5: 1000 x 5
    assert res.totaluri[4][0] == 15000              # tip 4 (10000) + tip 5 (5000)


def test_fara_tip5_sectiunea_4_ramane_pe_tip4():
    # fara servicii, nu se inventeaza rollup: baza4 = doar tip 4
    res = d301.calcul_d301(PROF, Perioada(2026, luna=6), [_op(4, 1000, 5.0, 1050)])
    assert res.totaluri[4] == (5000, 1050)
    assert res.totaluri[5] == (0, 0)


# ============================================================
#  Tipuri operatiune 1-5 | d301 (OPANAF 592/2016). Maparea tip->sectiune, verificata la sursa
#  (anaf_surse/d301_struct_anaf.txt): 1=S1 achizitii intracom bunuri; 2=S2 mijloace transport noi;
#  3=S3 produse accizabile; 4=S4 servicii (total); 5=S4.1 servicii art.150 (subset din S4).
# ============================================================
import pytest
from core import duk as _duk301


def test_tipuri_1_2_3_pe_sectiuni_proprii():
    res = d301.calcul_d301(PROF, Perioada(2026, luna=6),
                           [_op(1, 1000, 5.0, 1050), _op(2, 2000, 5.0, 2100), _op(3, 500, 5.0, 525)])
    assert res.totaluri[1] == (5000, 1050)    # S1 achizitii intracom bunuri
    assert res.totaluri[2] == (10000, 2100)   # S2 mijloace de transport noi
    assert res.totaluri[3] == (2500, 525)     # S3 produse accizabile
    assert res.mij_transp == 1                # tip 2 -> bifa mijloc de transport (art.324)
    # tipurile 1-3 NU se preiau in S4 (doar tip 5 e subset al S4):
    assert res.totaluri[4] == (0, 0)


@pytest.mark.skipif(not _duk301.poate_valida("d301"), reason="DUK d301 indisponibil")
def test_toate_tipurile_1_5_proba_duk_valid():
    # Proba pana la declaratie: un decont cu toate cele 5 tipuri trece DUKIntegrator (inclusiv
    # rollup-ul S4.1->S4 si checksum-ul totalPlata_A). Confirma maparea tip->sectiune.
    ops = [_op(1, 1000, 5.0, 1050), _op(2, 2000, 5.0, 2100), _op(3, 500, 5.0, 525),
           _op(4, 800, 5.0, 840), _op(5, 300, 5.0, 315)]
    res = d301.calcul_d301(dict(PROF, cui="14399840"), Perioada(2026, luna=6), ops)
    rez = _duk301.valideaza(d301.build_xml(res), "d301", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins D301 cu toate tipurile: %s" % rez.get("erori")
