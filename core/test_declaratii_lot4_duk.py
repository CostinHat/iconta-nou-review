# -*- coding: utf-8 -*-
"""Lot 4 de declaratii noi (6): proba DUK pe fiecare, cu validatorul OFICIAL ANAF.

D213 (instrainare pachet control terenuri agricole extravilan, OPANAF 216/2023, root D213), D214 (instrainare
teren agricol prin hotarare judecatoreasca, OPANAF 216/2023, root D214), D119 (declaratie speciala BNR, root
D119), D169n (neconcordante beneficiar real fiducie/AML, OPANAF 2175/2025, root D169n), D401 (proprietati
imobiliare DAC, root declaratie401), D402 (venituri salariale nerezidenti DAC1, OMFP 2727/2015, root declaratie402).
Toate manuale (conn=None). Structura din validator (arbitru).
"""
import pytest
from core.common import Perioada
from core import duk, d119, d169n, d213, d214, d401, d402

CAZURI = [
    ("d213", d213, Perioada(2025, luna=12), {
        "cif_c": "1960603410012", "nume_c": "SC Agro SRL", "adresa_c": "Bucuresti Str A 1",
        "nume_d": "Popescu Ion", "functie_d": "Administrator",
        "act_instrainare": "Contract vanzare 123/2025", "data_act": "10.03.2025",
        "terenuri": [{"judet": 23, "cif_uat": "4364359", "uat": 12, "valoare": 1200}]}),

    ("d214", d214, Perioada(2026, luna=12), {
        "nume_c": "Popescu Ion", "cif_c": "1800101400016", "adresa_c": "Bucuresti Str A 1",
        "dataAct": "15.06.2026", "actInstrainare": "1234/2026", "optiuneInstrainare": "1",
        "numeD": "Popescu Ion", "functieD": "Titular"}),

    ("d119", d119, Perioada(2026, luna=6), {
        "cif": "361684", "den": "BANCA NATIONALA A ROMANIEI", "adresaS": "Bucuresti Str Lipscani 25",
        "banca": "BNR", "Cont": "RO49AAAA1B31007593840000", "nume": "Popescu", "prenume": "Ion",
        "functie": "Director", "suma_dat": 1000, "suma_ded": 0}),

    ("d402", d402, Perioada(2025, luna=12), {
        "cif": "14399840", "den_p": "TEST SRL", "adresa_p": "Bucuresti Str A 1", "tip_p": 2,
        "forma_jurid_p": 1, "nume_declar": "Ion", "prenume_declar": "Pop", "functie_declar": "Administrator",
        "d_rec": 0, "beneficiari": [{
            "nume": "MUELLER HANS", "stat_r": "DE", "localitate_r": "Berlin", "cif_rom": "1800101221144",
            "calitate_b": 1, "tip_adr": 2, "categ_b": 2, "impozit_venit": 0,
            "venituri": [{"tip_venit": 1, "da_nu": 2, "data_i": "01.01.2025", "per_venit": 4,
                          "regim_fisc": 1, "suma_venit": 5000, "moneda_venit": "EUR"}]}]}),

    ("d401", d401, Perioada(2025, luna=12), {
        "an": 2025, "luna": 12, "d_rec": 0, "cif": "4267117",
        "den_primarie": "Primaria Municipiului Cluj-Napoca", "judet_primarie": "12",
        "localitate_primarie": "Cluj-Napoca", "adresa_primarie": "Str. Motilor nr. 3",
        "nume_declar": "Popescu", "prenume_declar": "Ion", "functie_declar": "Inspector",
        "detinatori": [
            {"tip_detinator": 1, "den_detinator": "Muller Hans", "stat_detinator": "DE",
             "nationalitate": "DE", "data_nasterii": "10.05.1970", "localitate_sr": "Berlin",
             "strada_sr": "Hauptstrasse", "nr_sr": "10",
             "proprietati": [
                 {"tip_proprietate": 1, "data_d": "15.03.2010", "data_i": "20.06.2025",
                  "act_nr_d": "1234", "act_emitent_d": "Notar public X", "act_nr_i": "5678",
                  "act_emitent_i": "Notar public Y", "mod_d": 2, "mod_i": 2, "judet_prop": "12",
                  "localitate_prop": "Cluj-Napoca", "strada_prop": "Str. Memorandumului", "nr_prop": "5",
                  "suprafata_cladire": "120", "destinatie_cladire": "1", "val1": "350000", "moneda1": "RON",
                  "tip_unic_coprop": 1, "cota_proprietar": "100"}]}]}),

    ("d169n", d169n, Perioada(2025, luna=12), {
        "nume": "Popescu Ion", "functie": "Director general",
        "den_E": "Autoritatea de Supraveghere Financiara", "cif": "16054368",
        "judet_E": "40", "sector_E": "1", "localit_E": "Bucuresti",
        "adresa_E": "Splaiul Independentei nr. 15", "codp_E": "050092",
        "tel_E": "0211234567", "email_E": "office@asf.ro",
        "den_R": "Popescu Ion", "calit_R": "Presedinte",
        "den_F": "Ionescu Maria", "cif_F": "18547290", "judet_F": "40", "sector_F": "2",
        "localit_F": "Bucuresti", "adresa_F": "Str. Fiduciarului nr. 2", "codp_F": "020202",
        "nr_contract": "12", "data_contract": "01.06.2025",
        "beneficiari": [
            {"den_B": "Georgescu Vasile", "cif_B": "1800101221144", "data_nasterii_B": "01.01.1980",
             "actId_B": "RX 123456", "stat_cetatenie_B": "RO", "adresa_B": "Str. Beneficiarului nr. 3, Bucuresti",
             "mod_control_B": "Control direct prin drept de proprietate 100%", "calitati": [1],
             "natura": "Interes de 100% asupra fiduciei",
             "mentiuni": "Neconcordanta la adresa beneficiarului real fata de Registrul central"},
            {"den_B": "Smith John", "cif_B": "X9999", "data_nasterii_B": "1975-05-20", "actId_B": "P 7654321",
             "stat_cetatenie_B": "US", "stat_resedinta_B": "US", "adresa_B": "1 Main Street, New York, USA",
             "mod_control_B": "Control indirect", "calitati": [2, 4], "natura": "Beneficiar rezidual",
             "mentiuni": "Neconcordanta cetatenie"}]}),
]


@pytest.mark.parametrize("tip,mod,per,manual", CAZURI, ids=[c[0] for c in CAZURI])
def test_lot4_duk_valid(tip, mod, per, manual):
    xml, _res = mod.genereaza(None, None, per, manual)
    v = duk.valideaza(xml, tip, an=per.an, luna=per.luna, timeout=120)
    if v.get("stare") == "gri":
        pytest.skip("validator %s indisponibil: %s" % (tip, v.get("temei")))
    assert v.get("stare") == "valid", "%s DUK nu e valid: %s" % (tip, v)
