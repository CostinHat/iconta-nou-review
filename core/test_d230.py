"""Teste D230 (redirectionare pana la 3,5% din impozit catre ONG).
Structura CITITA din validatorul oficial ANAF (D230Validator.jar, schema in vigoare namespace v5) si probata
camp cu camp pe DUKIntegrator. Proba finala pe validatorul oficial (DUKIntegrator -v D230)."""
import os
import pytest
from core import d230

_JAR_D230 = "/home/costin/duk/dist/lib/D230Validator.jar"


def _cnp(body12):
    w = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(body12[i]) * w[i] for i in range(12)) % 11
    return body12 + str(1 if c == 10 else c)


def _prof():
    return {}


def _manual(**ov):
    m = {"nume_c": "POPESCU", "initiala_c": "I", "prenume_c": "ANA MARIA", "cif_c": _cnp("196022915094"),
         "adresa_c": "Str Test 1 Bucuresti", "den_entitate": "Asociatia Binele", "cif_entitate": "12345678",
         "cont_entitate": "RO49AAAA1B31007593840000", "procent": 3.5, "valabilitate_distribuire": 2}
    m.update(ov)
    return m


def test_d230_build_xml_structura_v5():
    xml = d230.build_xml(_prof(), 2025, 12, _manual())
    assert 'xmlns="mfp:anaf:dgti:d230:declaratie:v5"' in xml
    assert 'luna="12"' in xml                       # perioada de raportare fixa
    assert 'bifa_entitate="1"' in xml and 'valabilitate_distribuire="2"' in xml
    assert 'procent="3.5"' in xml
    assert 'totalPlata_A="0"' in xml                # fara suma -> ANAF determina (R31 calc=0)
    # v5 NU are bifa_sal/bifa_pens/e_sectiune (interne / versiune veche)
    assert 'bifa_sal' not in xml and 'e_sectiune' not in xml


def test_d230_procent_plafonat_la_3_5():
    """R_procent: procent <= 3,5. O valoare mai mare se plafoneaza, nu se emite gresit."""
    xml = d230.build_xml(_prof(), 2025, 12, _manual(procent=10))
    assert 'procent="3.5"' in xml
    xml2 = d230.build_xml(_prof(), 2025, 12, _manual(procent=2))
    assert 'procent="2"' in xml2


def test_d230_erori_camp():
    prof = _prof()
    assert any("CNP" in e for e in d230.erori_generare(prof, _manual(cif_c="123")))         # CNP invalid
    assert any("valabilitate" in e for e in d230.erori_generare(prof, _manual(valabilitate_distribuire=None)))
    assert any("IBAN" in e for e in d230.erori_generare(prof, _manual(cont_entitate="XX")))
    assert any("den_entitate" in e for e in d230.erori_generare(prof, _manual(den_entitate="")))


@pytest.mark.skipif(not os.path.exists(_JAR_D230), reason="Validatorul D230 nu e instalat in DUK.")
def test_d230_valid_pe_validatorul_oficial():
    """Proba pe validatorul OFICIAL ANAF (DUKIntegrator -v D230), pe structura in vigoare (v5)."""
    from core import duk
    xml = d230.build_xml(_prof(), 2025, 12, _manual())
    rez = duk.valideaza(xml, "d230", an=2025, luna=12)
    assert rez["stare"] == "valid", rez.get("erori")
