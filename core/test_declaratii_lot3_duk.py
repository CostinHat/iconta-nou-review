# -*- coding: utf-8 -*-
"""Lot 3 de declaratii noi (6): proba DUK pe fiecare, cu validatorul OFICIAL ANAF.

D106 (informativa dividende, root declaratie106, OPANAF 1292/2014), D108 (impozit reprezentanta, root D108,
Cod fiscal Titlul VI), D130 (decont titei, root declaratie130, OPANAF 1950/2012), D318 (rambursare TVA alt
stat UE, root D318, art.302 CF/Directiva 2008/9), D603 (exceptare CASS, root d603, art.154 CF), D114 (CAM,
root D114, CF Titlul V). Structura din validator (arbitru); generatoare manuale. D106 trage header-ul din
firma_profil -> conn mock in test.
"""
from types import SimpleNamespace

import pytest

from core.common import Perioada
from core import duk, d106, d108, d114, d130, d318, d603


class _ConnD106:
    """Mock conn pentru d106.pull: firma_profil.id=1 -> (den,cui,adresa,declar_nume,prenume,functie,tel,email)."""
    def cursor(self):
        return self
    def __enter__(self):
        return self
    def __exit__(self, *a):
        pass
    def execute(self, *a):
        pass
    def fetchone(self):
        return ("TEST DE STAT SRL", "4221306", "Bucuresti", "Popescu", "Ion", "Administrator", "0211", "t@t.ro")


_MANUAL = {
    "d108": {"cif": "14399840", "den": "ACME LTD - Reprezentanta Bucuresti",
             "adresaS": "Bucuresti sector 1 Calea Victoriei nr 1 cod 010071",
             "nume": "POPESCU", "prenume": "ION", "functie": "Reprezentant legal"},
    "d130": {"cui": "1590082", "denumire": "OMV PETROM SA", "nume_declar": "Popescu",
             "prenume_declar": "Ion", "functie_declar": "Administrator",
             "cantitate_titei": 1500, "impozit_datorat": 54000},
    "d603": {"cif": "1800101221144", "numeContrib": "Popescu Ion", "judetContrib": "CJ",
             "exceptare": 2, "statAsigurare": "AT", "dataInceput": "2026-03-01",
             "dataSfarsit": "2026-09-30", "dataExceptare": "2026-02-15",
             "documente": "Adeverinta asigurare + formular A1"},
    "d114": {"cif_declarant": "13548146", "den_declarant": "TEST SRL", "adresa_declarant": "BUCURESTI",
             "functia_intocmit": "ADMINISTRATOR", "den_intocmit": "POPESCU ION",
             "contracte": [{"cui_lucrator": "13548146", "den_lucrator": "A", "nui_lucrator": "1",
                            "nr_contract": "10", "data_contract": "01.01.2026",
                            "venit_lucrator": 10000, "contributie_lucrator": 100}]},
    "d318": {"an": 2024, "luna_inceput": 1, "luna_sfarsit": 12, "annual": 1, "cui": "12345674", "d_rec": 0,
             "refunding_country": "DE", "language": "RO", "owner_name": "SC TEST SRL", "owner_type": "A",
             "iban": "DE89370400440532013000", "bic": "DEUTDEFF", "currency": "EUR",
             "declarant": "Popescu Ion", "functie": "Administrator",
             "solicitant": {"denumire": "SC TEST SRL", "strada": "Str. Exemplu 1", "email": "test@test.ro"},
             "activitati": [{"activitate": "4711"}],
             "achizitii": [{"reference_number": "F123", "issuing_date": "2024-05-10",
                            "taxable_amount": "1000", "vat_amount": "190", "deductible_vat": "190",
                            "furnizor": {"denumire": "Muster GmbH", "strada": "Hauptstr 1",
                                         "vat_id": "DE123456789", "tara": "DE"},
                            "bunuri": [{"code": "6"}]}]},
    "d106": {"d_rec": 0, "actionari": [
        {"cif": "4221306", "denumire": "Ministerul Finantelor", "cota": 70, "dividend": 105000},
        {"cif": "12345674", "denumire": "AAAS", "cota": 30, "dividend": 45000}]},
}

CAZURI = [
    ("d108", d108, None, Perioada(2025, luna=12)),
    ("d130", d130, None, Perioada(2025, luna=12)),
    ("d603", d603, None, Perioada(2026, luna=12)),
    ("d114", d114, None, Perioada(2026, luna=6)),
    ("d318", d318, None, Perioada(2024, luna=12)),
    ("d106", d106, _ConnD106(), Perioada(2025, luna=12)),
]


@pytest.mark.parametrize("tip,mod,conn,per", CAZURI, ids=[c[0] for c in CAZURI])
def test_lot3_duk_valid(tip, mod, conn, per):
    xml, _res = mod.genereaza(conn, "tenant_013", per, _MANUAL[tip])
    v = duk.valideaza(xml, tip, an=per.an, luna=per.luna, timeout=120)
    if v.get("stare") == "gri":
        pytest.skip("validator %s indisponibil: %s" % (tip, v.get("temei")))
    assert v.get("stare") == "valid", "%s DUK nu e valid: %s" % (tip, v)
