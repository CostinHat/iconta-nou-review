# -*- coding: utf-8 -*-
"""Lot 2 de declaratii noi (10): proba DUK pe fiecare, cu validatorul OFICIAL ANAF.

Structura fiecarui generator = citita din DXXXValidator.jar (arbitru); semantica = generator
MANUAL (valorile din input, ca d230/d104), pentru ca actele OPANAF nu sunt in corpus (just.ro
blocat). DUK verifica STRUCTURA. Dict-urile `manual` = cazurile minime valide probate la constructie.

D216 e validator de generatie noua (cere DecValidation 2024); core.duk.valideaza reincearca automat
pe classpath cu DecValidation nou (vezi core/duk.py).
"""
from core.common import Perioada
from core import duk, d393, d395, d397, d200, d201, d204, d208, d216, d120, d600

import pytest

CAZURI = [
    ("d393", d393, Perioada(2025, luna=12), {
        "cif": "12345674", "nume1": "TRANS INTERNATIONAL SRL",
        "adresa1": "Str. Garii nr. 1, Bucuresti", "nume_declarant": "Popescu",
        "prenume_declarant": "Ion", "functia_declarant": "Administrator", "venituri_bilete": 150000}),

    ("d395", d395, Perioada(2026, luna=7), {
        "cif": "13548146", "den": "POSTA RAPIDA SRL", "adresa": "Bucuresti sector 1",
        "telefon": "0211234567", "mail": "office@postarapida.ro",
        "cifR": "13548146", "denR": "CONTEXPERT SRL", "adresaR": "Bucuresti",
        "telefonR": "0217654321", "mailR": "declaratii@contexpert.ro",
        "declarant": "Ionescu Maria", "functie": "Administrator",
        "trimiteri": [{"nr_doc": "1001", "data_doc": "15.07.2026", "val_ramb": "250.50",
                       "den_expeditor": "MAGAZIN ONLINE SRL", "cif_expeditor": "13548146",
                       "jud_preluare": 1, "adresa_preluare": "Alba Iulia str Comert 5",
                       "iban": "RO49AAAA1B31007593840000", "den_destinatar": "Popescu Ana"}]}),

    ("d397", d397, Perioada(2026, luna=8), {
        "den": "PLATFORMA TRANSPORT SRL", "cif": "12345674",
        "adresa": "Bucuresti, Sector 1, Str. Exemplu nr.1",
        "numeIntocmit": "Popescu Ion", "functiaIntocmit": "Administrator",
        "operatori": [{"cif_O": "87654329", "den_O": "OPERATOR ALFA SRL", "data_accept": "01.01.2026",
                       "auto": [{"nr_auto": "B123ABC", "data_acceptA": "15.01.2026", "nr_km": 1000,
                                 "durata": 100, "venituri": 5000, "sume_n": 2000, "nume": "Ionescu Vasile",
                                 "cnp": "1800101221144", "data_accept_CA": "15.01.2026", "statut": "1"}]}]}),

    ("d200", d200, Perioada(2025, luna=12), {
        "cif_i": "1800101221144", "nume_c": "POPESCU", "prenume_c": "ION", "den_i": "POPESCU ION",
        "adresa_i": "Bucuresti Sector 1",
        "sectiuni": [{"categ_venit": "1", "caen": "6201", "venit_brut": 10000, "chelt": 4000}]}),

    ("d201", d201, Perioada(2025, luna=12), {
        "nume_c": "ION", "initiala_c": "V", "prenume_c": "DAN", "cif_c": "1800101221144",
        "sectiuni": [{"categ_venit": 3, "statul": 276, "venit_B": 1000, "chlt_D": 0}]}),

    ("d204", d204, Perioada(2025, luna=12), {
        "asociere": {"den": "ASOCIERE X", "cif": "23456783", "adresa": "Cluj-Napoca, Str. A nr.1"},
        "reprezentant": {"nume": "POPESCU ION", "cif": "1900101123457", "adresa": "Cluj-Napoca, Str. B nr.2"},
        "activitate": {"categ_venit": 1, "det_ven_net": 1, "caen": "4711", "forma_org": 1,
                       "judet": "12", "sediu": "Cluj-Napoca, Str. A nr.1", "nr_contr": "1",
                       "data_contr": "01.01.2020", "venit3": 5000, "chelt3": 2000},
        "asociati": [{"cif": "1900101123457", "nume": "POPESCU ION", "cota": 100, "venit": 3000, "pierd": 0}]}),

    ("d208", d208, Perioada(2026, luna=12), {
        "nume": "BIROU INDIVIDUAL NOTARIAL POPESCU ION", "cif": "12345674",
        "domiciliu": "Bucuresti, Str. Exemplu nr. 1", "nume_intocmit": "POPESCU ION",
        "functia_intocmit": "Notar public", "dRec": "0",
        "tranzactii": [{"nr_act_notarial": "1024/2026", "mod_transfer": "1", "taxa_notar": 1500,
            "imobile": [{"judet": "40", "localitate": "MUNICIPIUL BUCURESTI SECTOR 1",
                         "codSIRUTA": "179141", "tip_nr_cadastral": "1", "nr_cadastral": "200145",
                         "tip_imobil": "teren", "val_tranzactie_imobil": 300000, "val_piata_imobil": 300000,
                         "beneficiari": [{"cui": "1800101410013", "nume": "IONESCU MARIA", "cota": 100,
                                          "cotaImpozit": 3, "baza_calcul": 300000, "impozit": 9000, "impozit_scutit": 0}],
                         "parti": [{"cui": "1750202410022", "nume": "GEORGESCU VASILE", "cota": 100}]}]}]}),

    ("d216", d216, Perioada(2025, luna=12), {
        "nume": "POPESCU ION", "cif": "1960101410019", "domiciliuFiscal": "JUD BOTOSANI MUN BOTOSANI",
        "nume_intocmit": "IONESCU MARIA", "functia_intocmit": "CONTABIL", "d_rec": 0,
        "imobile": [{"judet_imobil": "BOTOSANI", "cod_judet_imobil": "7", "localitate_imobil": "BOTOSANI",
                     "cod_localitate_imobil": "1", "strada_imobil": "STR PRIMAVERII", "cod_strada_imobil": "1",
                     "nr_cadastral": "12345", "valoare_impozabila_imobil": 3000000, "cota": 0.3,
                     "plafon_imobil": 2500000}]}),

    ("d120", d120, Perioada(2025, luna=12), {
        "cif": "13548146", "den": "SC MIN SRL", "adresa": "Bucuresti", "caen": "1101",
        "nume_declar": "Ionescu", "prenume_declar": "Ana", "functie_declar": "Contabil"}),

    ("d600", d600, Perioada(2025, luna=12), {
        "nume_c": "POPESCU", "initiala_c": "I", "prenume_c": "ION", "cif_c": "1960501122231",
        "adresa_c": "Bucuresti, sector 1", "cass_opt": "1"}),
]


@pytest.mark.parametrize("tip,mod,per,manual", CAZURI, ids=[c[0] for c in CAZURI])
def test_lot2_duk_valid(tip, mod, per, manual):
    xml, _res = mod.genereaza(None, None, per, manual)
    v = duk.valideaza(xml, tip, an=per.an, luna=per.luna, timeout=120)
    if v.get("stare") == "gri":
        pytest.skip("validator %s indisponibil: %s" % (tip, v.get("temei")))
    assert v.get("stare") == "valid", "%s DUK nu e valid: %s" % (tip, v)
