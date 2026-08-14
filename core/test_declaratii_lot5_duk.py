# -*- coding: utf-8 -*-
"""Lot 5 de declaratii noi (6): proba DUK pe fiecare (validator OFICIAL ANAF).

D169 (inregistrare fiducie, L.129/2019, root D169, generatie noua), D398 (OSS TVA UE/non-UE, root d398,
generatie noua), D399 (IOSS TVA import, root declaratie399), D403 (DAC2/CRS asigurari viata, root declaratie403),
D407 (institutii financiare raportoare, root D407). Toate manuale (conn=None).

D101G (grup fiscal impozit profit) e xfail: DATORIE de infrastructura - schema de structura v2 (P01-P16,
OPANAF 206/2025, ns d101g:declaratie:v2) NU e deployata in DUK pe server (DecValidation vechi nu cunoaste d101g,
cel nou cere v1 hardwired). Modulul e construit corect pe v2 (bytecode + act in corpus); se probeaza cand se
instaleaza DecValidation care cunoaste d101g v2. Vezi DECIZII.md.
"""
import pytest
from core.common import Perioada
from core import duk, d101g, d169, d398, d399, d403, d407

CAZURI = [
    ("d169", d169, Perioada(2026, luna=12), {
        "nume": "P", "functie": "A", "cif": "18547290", "nr_contract_I": "1",
        "data_contract_I": "15.01.2026", "data1_I": "15.01.2026", "scop_fiducie": "X",
        "fiduciari": [{"den_F": "F", "cif_F": "18547290", "localit_F": "A", "adresa_F": "B"}],
        "constituitori": [{"den_Ct": "C", "cif_Ct": "1800101221144", "judet_Ct": "1", "localit_Ct": "A", "adresa_Ct": "B"}],
        "beneficiari": [{"den_B1": "D", "cif_B1": "18547290", "judet_B1": "1", "localit_B1": "A", "adresa_B1": "B"}],
        "beneficiari_reali": [{"den_B": "C", "cif_B": "1800101221144", "data_nasterii_B": "01.01.1980",
                               "actId_B": "AX1", "adresa_B": "B", "mod_control_B": "M", "calitati": [1], "natura": "N"}]}),

    ("d398", d398, Perioada(2024, luna=3), {
        "an_r": 2024, "luna_r": 3, "moes_voes_imp": 1, "e_int": 0, "vat_id_no": "RO14399840", "name": "TEST SRL"}),

    ("d399", d399, Perioada(2025, luna=12), {
        "moss_voes": "RO", "vat_id_num": "14247702", "name": "TEST SRL", "address": "Bucuresti",
        "family_name": "Popescu", "first_name": "Ion", "title": "Administrator"}),

    ("d403", d403, Perioada(2025, luna=12), {
        "cif": "13548146", "den_rap": "BANCA TEST SA", "judet_rap": "01", "localitate_rap": "Alba Iulia",
        "adresa_rap": "Str. Exemplu nr. 1", "tara_rap": "RO", "forma_juridica": "1", "tip_adresa1": 1,
        "sediu_dn1": 1, "nume_declar": "Popescu", "prenume_declar": "Ion", "functie_declar": "Administrator", "d_rec": 0,
        "polite": [{"id_polita": "P1", "tip_polita": 2, "trat_fisc_polita": 1, "tip_benef_polita": 1,
                    "persoane": [{"id_pers": "1", "calit_pers": 1, "tip_pers": 2, "den_pers": "MUSTERMANN GMBH",
                                  "stat_sr": "DE", "localitate_sr": "Berlin", "tip_pj": 1, "sediu_dn2": 1,
                                  "tip_ben_plat_contr": 1, "unic_mm": 1, "cota_parte": "100.00", "stare_ben": 1}],
                    "evenimente": [{"id_eveniment": "1", "tip_ev": 1, "periodicitate": 1, "regim_ev": 1,
                                    "mod_imp1": 1, "mod_imp2": 1}]}]}),

    ("d407", d407, Perioada(2025, luna=12), {
        "tip_doc": 2, "luna": 12, "d_rec": 0, "cif": "13548146", "den": "Banca Test SA", "adresa": "Str Test 1",
        "localitate": "Bucuresti", "judet": 40, "tara_rap": "RO", "forma_j": "SA", "nume": "Popescu Ion",
        "functia": "Director", "persoane": [{"den_d": "Ionescu Maria", "cif_d": "1800101221144",
            "isin": "US0378331005", "simbol": "AAPL", "cantitatea": "10", "tip_instrument": 1,
            "den_emitent": "Apple Inc", "adresa_d": "New York"}]}),

    pytest.param("d101g", d101g, Perioada(2024, luna=12), {
        "cui": "RO12345678", "nume": "GRUP RESPONSABIL SRL", "adresa": "Bucuresti, Str. Exemplu nr. 1",
        "caen": "6201", "declarant_nume": "POPESCU", "declarant_prenume": "ION",
        "declarant_functie": "ADMINISTRATOR", "P01": 1000000},
        marks=pytest.mark.xfail(strict=True, reason="DATORIE 14.08.2026: schema de structura D101G v2 (P01-P16, "
              "OPANAF 206/2025, ns d101g:declaratie:v2) NU e deployata in DUK pe server (DecValidation vechi nu "
              "cunoaste d101g; cel nou cere v1 hardwired). Modulul e corect pe v2. Se probeaza cand se instaleaza "
              "DecValidation cu d101g v2. Vezi DECIZII.md.")),
]


@pytest.mark.parametrize("tip,mod,per,manual", CAZURI, ids=lambda x: x if isinstance(x, str) else None)
def test_lot5_duk_valid(tip, mod, per, manual):
    xml, _res = mod.genereaza(None, None, per, manual)
    v = duk.valideaza(xml, tip, an=per.an, luna=per.luna, timeout=120)
    if v.get("stare") == "gri":
        pytest.skip("validator %s indisponibil: %s" % (tip, v.get("temei")))
    assert v.get("stare") == "valid", "%s DUK nu e valid: %s" % (tip, v)
