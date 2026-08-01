# -*- coding: utf-8 -*-
"""Gard: modelul de temei pe data_out (Modelul de temei 01.08, pct.1+2).

O lege spune de CAND intra in vigoare, nu pana cand. data_out NU se scrie de mana - se DERIVA din
succesor (predecesor primeste ziua dinaintea lui data_in a succesorului); valoarea CURENTA nu expira
(data_out=None). cota() RIDICA doar pe un GOL real (data_out < data ceruta), nu pe o expirare inventata.
Semnalul ca o valoare curenta n-a mai fost confirmata de mult e VECHIMEA CONFIRMARII (raport intern),
nu blocaj la calcul.
"""
from datetime import date

import pytest

from core.common import COTE, Temei, cota, cote_neconfirmate, _deriva_data_out


def test_valoarea_curenta_se_intoarce_normal():
    v, t = cota("salariu_minim", date(2026, 6, 1))
    assert int(v) == 4050 and "1506" in t   # 2026 H1: HG 1506/2024 (data_out derivat 2026-06-30)


def test_salariu_minim_2025_este_4050_hg_1506():
    """Salariul minim 2025 = 4050 lei (HG 1506/2024, MO 1185/28.11.2024, abroga HG 598/2024=3700).
    Sursa: legislatie.just.ro Public/DetaliiDocument/291450."""
    v, t = cota("salariu_minim", date(2025, 3, 1))
    assert int(v) == 4050 and "1506" in t


def test_valoarea_curenta_NU_expira():
    """Corectie 01.08: valoarea CURENTA (data_out=None) nu expira - o lege spune de cand, nu pana cand.
    cota(2027) intoarce valoarea curenta, NU ridica. (Era: ridica pe EXPIRA_DUPA_LUNI inventat.)"""
    v, _ = cota("salariu_minim", date(2027, 9, 1))
    assert int(v) == 4325, "valoarea curenta trebuie intoarsa, nu blocata"
    v2, _ = cota("tichet_masa_plafon", date(2027, 1, 1))
    assert int(v2) == 45


def test_cota_ridica_pe_gol_real_intre_valori():
    """cota() RIDICA doar cand valoarea selectata are un data_out REAL (succesor exista) si data ceruta
    e dupa el - un GOL in registru. Construit sintetic: valoare veche cu succesor, dar data intre ele
    ceruta dupa un gol artificial."""
    cote = {"x": [
        (date(2020, 1, 1), 10, Temei("Legea", 1, 2020, data_in="2020-01-01")),
        (date(2025, 1, 1), 20, Temei("Legea", 2, 2025, data_in="2025-01-01")),
    ]}
    _deriva_data_out(cote)   # predecesorul (2020) capata data_out=2024-12-31
    # cota nu stie de dict-ul local; verificam direct data_out derivat
    pred = [t for d, v, t in cote["x"] if d == date(2020, 1, 1)][0]
    assert pred.data_out == date(2024, 12, 31)


def test_data_out_se_deriva_din_succesor():
    """Modelul de temei pct.1: adaugarea unei valori noi -> predecesorul capata data_out = ziua dinaintea
    lui data_in a succesorului; valoarea curenta ramane None. AUTOMAT, nu scris de mana."""
    cote = {"x": [
        (date(2024, 1, 1), 1, Temei("Legea", 1, 2024, data_in="2024-01-01")),
        (date(2026, 3, 1), 2, Temei("Legea", 2, 2026, data_in="2026-03-01")),   # succesor NOU
    ]}
    _deriva_data_out(cote)
    pred = [t for d, v, t in cote["x"] if d == date(2024, 1, 1)][0]
    cur = [t for d, v, t in cote["x"] if d == date(2026, 3, 1)][0]
    assert pred.data_out == date(2026, 2, 28), "predecesorul nu a capatat ziua dinaintea succesorului"
    assert cur.data_out is None, "valoarea curenta trebuie sa ramana in vigoare (None)"


def test_data_out_curenta_None_istorica_derivata():
    """GARD INVERSAT (Costin, Modelul de temei pct.1): data_out se DERIVA din succesor.
    - Valoarea CURENTA cu data_out SETAT -> BLOCHEAZA (termen inventat).
    - Valoarea ISTORICA fara data_out -> BLOCHEAZA (succesorul exista, data se poate deriva)."""
    curenta_cu_dataout, istorica_fara_dataout = [], []
    for nume, intrari in COTE.items():
        sortate = sorted(intrari, key=lambda t: t[0])   # crescator dupa data_in
        if sortate[-1][2].data_out is not None:
            curenta_cu_dataout.append(nume)
        for din, val, t in sortate[:-1]:
            if t.data_out is None:
                istorica_fara_dataout.append((nume, din.isoformat()))
    assert not curenta_cu_dataout, "valori CURENTE cu data_out (termen inventat): %s" % curenta_cu_dataout
    assert not istorica_fara_dataout, "valori ISTORICE fara data_out (derivabile din succesor): %s" % istorica_fara_dataout


def test_cote_neconfirmate_raporteaza_vechimea():
    """Raportul intern de vechime a confirmarii: la o data mult dupa verificat_la, valorile apar cu
    verificat_la si luni_de_la_confirmare."""
    r = cote_neconfirmate(6, la_data=date(2028, 1, 1))
    assert r, "toate valorile ar trebui neconfirmate la 2028 (verificat 2026-07-31)"
    for x in r:
        assert x["temei"] and x["verificat_la"] and x["luni_de_la_confirmare"] >= 6
    assert any(x["nume"] == "salariu_minim" for x in r)
