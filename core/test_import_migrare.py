# -*- coding: utf-8 -*-
"""Teste gardian pentru importurile de migrare care nu aveau NICIUNA.

Toate bugurile de mai jos au fost gasite prin migrare reala (pachet cu greseli
intentionate, incarcat prin interfata ca un cabinet adevarat), nu de teste.
Tiparul comun: modulele calculau validari si le trimiteau in raspuns, ecranul le
afisa, iar importa() scria oricum. Migrarea marca stratul "gata" VERDE.
"""
import datetime as d
import pytest

from core.salariati_import_api import verifica_randuri as v_sal, JUDETE_CASA
from core.asociati_import_api import verifica_randuri as v_asoc, importa as imp_asoc
from core.mijloace_fixe_import_api import verifica_randuri as v_mf, importa as imp_mf
from core.istoric_declaratii_import_api import (verifica_randuri as v_ist,
                                                importa as imp_ist, TIPURI_CUNOSCUTE)

AZI = d.date(2026, 7, 15)


# ---------------- SALARIATI ----------------
def _s(**kw):
    b = {"nume": "X", "prenume": "Y", "cnp_valid": True, "data_angajare": "2024-01-08",
         "ore_zi": 8, "judet_casa": "B", "tip_norma": "intreaga",  # [Q11] salariat complet are norma
         "salariu_brut": 5000}  # [salariu_import] ... si salariu de baza > 0
    b.update(kw)
    return b


def test_salariat_corect_trece():
    assert v_sal([_s()], azi=AZI) == []


def test_cnp_invalid_e_respins():
    er = v_sal([_s(cnp_valid=False, cnp_motiv="cifra de control")], azi=AZI)
    assert er and er[0]["motiv"] == "cnp_invalid"


def test_angajare_in_viitor():
    er = v_sal([_s(data_angajare="2027-09-15")], azi=AZI)
    assert er and er[0]["motiv"] == "data_viitor"


def test_peste_8_ore_pe_zi():
    er = v_sal([_s(ore_zi=15)], azi=AZI)
    assert er and er[0]["motiv"] == "ore_invalide"


def test_judet_inexistent():
    er = v_sal([_s(judet_casa="ZZ")], azi=AZI)
    assert er and er[0]["motiv"] == "judet_invalid"
    assert "ZZ" not in JUDETE_CASA and "B" in JUDETE_CASA


def test_salariu_brut_lipsa_e_respins():
    # [salariu_import] fisier fara coloana de salariu -> parser 0.0 / None; NU intra tacit cu baza 0
    er = v_sal([_s(salariu_brut=None)], azi=AZI)
    assert er and er[0]["motiv"] == "salariu_lipsa"
    er2 = v_sal([_s(salariu_brut=0.0)], azi=AZI)
    assert er2 and er2[0]["motiv"] == "salariu_lipsa"


def test_salariu_brut_negativ_e_respins():
    er = v_sal([_s(salariu_brut=-100)], azi=AZI)
    assert er and er[0]["motiv"] == "salariu_lipsa"


# ---------------- ASOCIATI ----------------
def test_cotele_trebuie_sa_dea_100():
    """coerenta_cote() exista de la inceput, dar importa() n-o chema."""
    er = v_asoc([{"nume": "A", "cnp": "1700826400183", "cota": 60},
                 {"nume": "B", "cnp": "2751126400229", "cota": 30}])
    assert any(x["motiv"] == "cote" for x in er)


def test_cotele_de_100_trec():
    assert v_asoc([{"nume": "A", "cnp": "1700826400183", "cota": 60},
                   {"nume": "B", "cnp": "2751126400229", "cota": 40}]) == []


def test_importa_asociati_REFUZA():
    with pytest.raises(ValueError) as e:
        imp_asoc(None, [{"nume": "A", "cnp": "1700826400183", "cota": 115}])
    assert "D205" in str(e.value)


# ---------------- MIJLOACE FIXE ----------------
def _m(**kw):
    b = {"cod": "MF-1", "denumire": "Laptop", "valoare": 7000, "rezidual": 3500, "durata": 36}
    b.update(kw)
    return b


def test_mijloc_fix_corect_trece():
    assert v_mf([_m()]) == []


def test_durata_zero_opreste_amortizarea():
    er = v_mf([_m(durata=0)])
    assert er and er[0]["motiv"] == "durata"


def test_ramasa_nu_poate_depasi_intrarea():
    er = v_mf([_m(valoare=5000, rezidual=6000)])
    assert er and er[0]["motiv"] == "rezidual"


def test_cod_inventar_duplicat():
    er = v_mf([_m(cod="MF-1"), _m(cod="MF-1", denumire="Altul")])
    assert any(x["motiv"] == "cod_duplicat" for x in er)


def test_importa_mijloace_REFUZA():
    with pytest.raises(ValueError) as e:
        imp_mf(None, [_m(durata=0)])
    assert "D406" in str(e.value) or "amortizare" in str(e.value)


# ---------------- ISTORIC DECLARATII ----------------
def _i(**kw):
    b = {"tip": "D100", "an": 2026, "luna": 3, "data_depunere": "2026-04-24"}
    b.update(kw)
    return b


def test_declaratie_corecta_trece():
    assert v_ist([_i()], azi=AZI) == []


def test_tip_inexistent():
    er = v_ist([_i(tip="D999")], azi=AZI)
    assert er and er[0]["motiv"] == "tip"
    assert "D999" not in TIPURI_CUNOSCUTE and "D406" in TIPURI_CUNOSCUTE


def test_luna_13():
    er = v_ist([_i(luna=13)], azi=AZI)
    assert er and er[0]["motiv"] == "luna"


def test_depusa_inainte_de_perioada():
    """D112 pentru mai, depusa in ianuarie - imposibil."""
    er = v_ist([_i(tip="D112", luna=5, data_depunere="2026-01-10")], azi=AZI)
    assert er and er[0]["motiv"] == "data_inainte"


def test_importa_istoric_REFUZA():
    with pytest.raises(ValueError) as e:
        imp_ist(None, 1, [_i(tip="D999")])
    assert "termene" in str(e.value) or "control fiscal" in str(e.value)


# ---------------- regula comuna ----------------
def test_numarul_randului_e_cel_din_fisier():
    """Antetul e randul 1 - omul trebuie sa gaseasca randul in Excel."""
    assert v_sal([_s(ore_zi=15)], azi=AZI)[0]["rand"] == 2
    assert v_mf([_m(durata=0)])[0]["rand"] == 2
    assert v_ist([_i(luna=13)], azi=AZI)[0]["rand"] == 2
