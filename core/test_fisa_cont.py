# -*- coding: utf-8 -*-
"""GARD: Fișa de cont pentru operațiuni diverse produce ce cere norma, nu o balanță deghizată.

CE FACE IMPOSIBIL: ca artefactul care **înlocuiește Cartea mare** (OMFP 2634/2015, Anexa 2, cod
14-1-3 și 14-1-3/a: *„Registrul Cartea mare poate fi înlocuit cu Fișa de cont pentru operațiuni
diverse"*) să piardă exact ce pierdea `motor.carte_mare` — **contul corespondent** și **cronologia**.
Aia a fost greșeala de la poziția 1 a triajului: o agregare care arată ca un registru.

CE NU FACE, declarat: nu verifică dacă cifrele din evidență sunt corecte — verifică **forma** fișei și
**invarianții** ei aritmetici. Corectitudinea sumelor e treaba reconcilierii.
"""
from datetime import date
from decimal import Decimal

import pytest

from core import fisa_cont


class _Cur:
    """Cursor fals: întoarce rândurile date, indiferent de SQL. Testul e despre TRANSFORMARE."""

    def __init__(self, randuri):
        self._r = randuri

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, *a, **k):
        pass

    def fetchall(self):
        return self._r


class _Conn:
    def __init__(self, randuri):
        self._r = randuri

    def cursor(self, **k):
        return _Cur(self._r)


def _linie(zi, numar, desc, cd, cc, suma, sursa="casa"):
    return {"data": date(2026, 8, zi), "numar": numar, "descriere": desc, "sursa": sursa,
            "cont_debit": cd, "cont_credit": cc, "suma": Decimal(str(suma))}


# 5311 (casă) primește 1000 de la 4111, apoi plătește 300 către 401.
_NOTE = [_linie(3, "NC-1", "încasare client", "5311", "4111", 1000),
         _linie(7, "NC-2", "plată furnizor", "401", "5311", 300)]


def _fisa(**k):
    return fisa_cont.fisa_cont(_Conn(_NOTE), "t", "5311", 2026, luna=8, **k)


def test_fiecare_rand_poarta_CONTUL_CORESPONDENT():
    """Miezul, și chiar diferența față de o balanță: perechea debit↔credit se păstrează pe rând."""
    f = _fisa()
    assert [r.cont_corespondent for r in f["randuri"]] == ["4111", "401"], f["randuri"]


def test_sensul_randului_e_dat_de_capatul_pe_care_sta_contul():
    f = _fisa()
    assert (f["randuri"][0].debit, f["randuri"][0].credit) == (Decimal("1000.00"), Decimal("0.00"))
    assert (f["randuri"][1].debit, f["randuri"][1].credit) == (Decimal("0.00"), Decimal("300.00"))


def test_soldul_se_poarta_din_rand_in_rand_si_are_SENS():
    """Un sold fără sens (D/C) nu se poate citi: 700 debitor și 700 creditor sunt lucruri opuse."""
    f = _fisa()
    assert [(r.sold, r.sens_sold) for r in f["randuri"]] == \
        [(Decimal("1000.00"), "D"), (Decimal("700.00"), "D")]
    assert (f["sold_final"], f["sens_sold_final"]) == (Decimal("700.00"), "D")


def test_soldul_creditor_nu_se_arata_ca_negativ():
    """Contabilul citește «700 C», nu «−700». Semnul trăiește în `sens_sold`, nu în cifră."""
    f = fisa_cont.fisa_cont(_Conn([_linie(3, "NC-1", "aport", "5121", "455", 500)]),
                            "t", "455", 2026, luna=8)
    assert (f["sold_final"], f["sens_sold_final"]) == (Decimal("500.00"), "C")
    assert f["randuri"][0].sold > 0


def test_INVARIANT_soldul_final_e_soldul_initial_plus_debit_minus_credit():
    f = _fisa(sold_initial=Decimal("250"))
    calc = f["sold_initial"] + f["total_debit"] - f["total_credit"]
    assert abs(calc) == f["sold_final"]
    assert f["sold_final"] == Decimal("950.00")


def test_soldul_initial_NEDAT_se_declara_nu_se_presupune():
    """O fișă care pornește tăcut de la zero afirmă că înainte n-a fost nimic."""
    assert _fisa()["sold_initial_declarat"] is False
    assert _fisa(sold_initial=Decimal("0"))["sold_initial_declarat"] is True


def test_cronologia_se_pastreaza():
    f = _fisa()
    assert [r.data.day for r in f["randuri"]] == [3, 7]


def test_formularul_se_numeste_cu_codul_din_norma():
    assert fisa_cont.COD_FORMULAR == "14-6-22"


@pytest.mark.parametrize("rau", ["", "   ", None])
def test_contul_lipsa_e_refuzat_nu_produce_fisa_goala(rau):
    """O fișă goală pe un cont nenumit arată ca «acest cont n-a avut mișcare» — afirmație falsă."""
    with pytest.raises(ValueError):
        fisa_cont.fisa_cont(_Conn([]), "t", rau, 2026, luna=8)


def test_luna_invalida_e_refuzata():
    with pytest.raises(ValueError):
        fisa_cont.fisa_cont(_Conn([]), "t", "5311", 2026, luna=13)


def test_sensul_SE_SCHIMBA_pe_parcurs_daca_soldul_trece_prin_zero():
    """Calibrare pe propriul mod de eșec, adăugată după ce o mutație a trecut: prima formă a gardului
    verifica sensul doar pe rânduri unde soldul era debitor pe amândouă, deci `sens_sold = "D"` fix ar
    fi trecut. Aici soldul trece D → C în interiorul fișei, iar un sens înghețat pică."""
    note = [_linie(2, "NC-1", "încasare", "5311", "4111", 100),
            _linie(5, "NC-2", "plată mare", "401", "5311", 400)]
    f = fisa_cont.fisa_cont(_Conn(note), "t", "5311", 2026, luna=8)
    assert [(r.sold, r.sens_sold) for r in f["randuri"]] ==         [(Decimal("100.00"), "D"), (Decimal("300.00"), "C")]
    assert (f["sold_final"], f["sens_sold_final"]) == (Decimal("300.00"), "C")


def test_soldul_zero_nu_e_nici_debitor_nici_creditor():
    note = [_linie(2, "NC-1", "încasare", "5311", "4111", 100),
            _linie(5, "NC-2", "plată", "401", "5311", 100)]
    f = fisa_cont.fisa_cont(_Conn(note), "t", "5311", 2026, luna=8)
    assert f["randuri"][-1].sens_sold == "0" and f["sens_sold_final"] == "0"


def test_fisa_e_o_AFIRMATIE_TIPATA_nu_un_dict_de_proza():
    """P3 (21.08.2026): o afirmație despre datele firmei e un OBIECT cu atribute. Prima formă a fișei
    întorcea un dict simplu, iar poarta a respins-o — corect. La un control, `temei_completitudine` e
    chiar ce face fișa apărabilă: spune DE CE credem că am văzut tot."""
    f = _fisa()
    assert f["fel"] == "fapt" and f["tip"] == "fisa_cont"
    assert f["motiv"] and "14-6-22" in f["motiv"]
    tc = f["temei_completitudine"]
    assert tc and "validata" in tc and "ciornele" in tc.lower(), tc
    assert f["an"] == 2026 and f["luna"] == 8, "faptul trebuie să poarte domeniul"


def test_randul_e_OBIECT_cu_atribute_nu_dict():
    """A doua respingere a porții, în aceeași tură: rândul era tot un dict de proză. Un rând care
    spune «contul 5311 a primit 1000 de la 4111, sold 1000 D» e o afirmație despre datele firmei.
    Conversia la dict se face la MARGINE (`ca_dict`), pentru randare, nu în interior."""
    r = _fisa()["randuri"][0]
    assert isinstance(r, fisa_cont.RandFisa), type(r)
    assert not isinstance(r, dict)
    d = r.ca_dict()
    assert d["cont_corespondent"] == "4111" and d["sens_sold"] == "D"


def test_ANTIVACUU_gardul_chiar_vede_randuri():
    """Dacă transformarea s-ar goli, toate testele de mai sus ar trece pe liste vide."""
    assert len(_fisa()["randuri"]) == 2
    assert _fisa()["total_debit"] > 0 and _fisa()["total_credit"] > 0
