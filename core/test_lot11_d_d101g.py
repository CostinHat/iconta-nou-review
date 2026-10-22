# -*- coding: utf-8 -*-
"""[lotul 11, deficiența C70] D101G refăcut pe validatorul v2 — decizia Costin 10.3: „C70: refaci D101G pe validatorul v2.”

Ce era: XML-ul D101G generat nu trecea DUK deloc. Runda 0 (generatorul vechi, profil minim complet):
„eroare structura: sectiune necunoscuta ('declaratie')”. Rundele 1–5, câte o corecție, pe validatorul instalat
(~/duk/dist/lib/D101GValidator.jar J2.0.0, `d101gvalidator/v1`, namespace `mfp:anaf:dgti:d101g:declaratie:v2`), coroborat cu
structura ANAF `anaf_surse/d101g_structura_2025_050526.txt`:
  1. rădăcina `<D101G>` (DUK `DECTag("D101G")`; structura nr.1)            -> rămân: d_recN / cod_obligatie / totalPlata_A / CAEN
  2. fără `d_recN="0"` (DUK interval [1,1], opțional; structura „d_recN =1,null”)
  3. `cod_obligatie="100"` (DUK `Parameters_v1.nomenclat_cod_obl` = {"100"})
  4. `CAEN` (majuscule; DUK `nextAttributeInList(nomenclat_caen, "CAEN")`; structura nr.26)
  5. `totalPlata_A="0"` (DUK interval [0,0]; structura nr.20 „totalPlata_A =0”)  -> stare valid.
Fiecare test apără o regresie; testele cu DUK se sar numai dacă validatorul nu e instalat (stare gri), nu trec fals.
"""
import os
import xml.etree.ElementTree as ET

import pytest

from core import d101g, duk
from core.common import Perioada

NS = "{mfp:anaf:dgti:d101g:declaratie:v2}"
# CUI 14399840: cifra de control verificată cu algoritmul din CLAUDE.md (cui_valid -> True)
PROF = {"cui": "14399840", "nume": "GRUP RESPONSABIL SRL", "adresa": "Str. Probei 9, Cluj-Napoca, CJ", "caen": "6920",
        "telefon": "0264123456", "email": "contact@exemplu.ro",
        "declarant_nume": "POPESCU", "declarant_prenume": "ION", "declarant_functie": "ADMINISTRATOR"}
COMPLET = dict(P01=1000000, P02=300000, P02a=200000, P051=1000, P0521=2000, P0522=500, P0531=300, P061=1500, P062=500,
               P06a=200, P07=100, P08=50, P10=3000, P12=1000, P13=40000, P14=10)


def _rad(an=2025, **m):
    xml, res = d101g.genereaza(None, None, Perioada(an), dict(PROF, cota=16, **m))
    return ET.fromstring(xml.encode("utf-8")), xml, res


def _duk(xml):
    v = duk.valideaza(xml, "d101g", timeout=120)
    if v.get("stare") == "gri":
        pytest.skip("validator D101G indisponibil: %s" % v.get("temei"))
    return v


def test_radacina_e_D101G_in_namespace_v2():
    rad, _x, _r = _rad(P01=1000)
    assert rad.tag == NS + "D101G"          # DUK DECTag("D101G"); structura nr.1 <D101G> (era <declaratie>: „sectiune necunoscuta”)


def test_d_recN_numai_cand_e_1():
    rad, _x, _r = _rad(P01=1000)
    assert rad.get("d_recN") is None        # DUK d_recN interval [1,1], opțional — „d_recN =1,null”; „0” era respins
    rad, _x, _r = _rad(P01=1000, d_recN=1)
    assert (rad.get("d_recN"), rad.get("d_rec")) == ("1", "2")   # DUK R2a: d_rec=2 daca d_recN=1


def test_cod_obligatie_100_si_altul_refuzat():
    rad, _x, _r = _rad(P01=1000)
    assert rad.get("cod_obligatie") == "100"                    # DUK nomenclat_cod_obl = {"100"}
    assert rad.get("nr_evid")[2:5] == "100"                     # structura nr.19: „Poz.3-5 : cod_obligatie”
    with pytest.raises(ValueError, match="nu e acceptat"):
        d101g.genereaza(None, None, Perioada(2025), dict(PROF, cota=16, P01=1000, cod_obligatie="103"))


def test_atributul_CAEN_cu_majuscule():
    rad, _x, _r = _rad(P01=1000)
    assert rad.get("CAEN") == "6920" and rad.get("caen") is None   # DUK „CAEN”; „caen” = atribut necunoscut


def test_totalPlata_A_e_zero_diferenta_ramane_la_rd15():
    rad, _x, res = _rad(P01=1000)
    assert rad.get("totalPlata_A") == "0"   # DUK totalPlata_A interval [0,0]; structura nr.20 „totalPlata_A =0”
    assert rad.get("P15") == "160"          # rd.15 = (rd.11 + rd.14) - (rd.12 + rd.13) = 160 (16% din 1.000, cota din registru)
    assert res.total_plata_a == 0


def test_temei_anulare_numeric_1_sau_2():
    rad, _x, _r = _rad(P01=1000, d_anulare=1, temei=2)
    assert rad.get("temei") == "2"          # structura 4b: „2-art.105 alin(6) lit.b) din Legea nr.207/2015”; DUK interval [1,2]
    with pytest.raises(ValueError, match="temeiul"):
        d101g.genereaza(None, None, Perioada(2025), dict(PROF, cota=16, P01=1000, d_anulare=1))
    with pytest.raises(ValueError, match="temeiul"):
        d101g.genereaza(None, None, Perioada(2025), dict(PROF, cota=16, P01=1000, d_anulare=1, temei="art.105"))


def test_lungimile_DUK_se_opresc_nu_se_taie():
    p = dict(PROF, declarant_functie="F" * 51)
    # DUK functie_declar lungime 50 (structura C(50)): EXACT o eroare, cea a funcției (o listă goală pică)
    assert d101g.erori_generare(p) == ["D101G: funcția declarantului are 51 de caractere; formularul ANAF primește cel mult 50 de "
                                       "caractere. Scurtează-l în Date firmă."], d101g.erori_generare(p)
    with pytest.raises(ValueError, match="cel mult 50"):
        d101g.genereaza(None, None, Perioada(2025), dict(p, cota=16, P01=1000))
    rad, _x, _r = _rad(P01=1000, email="a" * 70 + "@exemplu.ro")
    assert rad.get("email") == "a" * 70 + "@exemplu.ro"               # DUK email lungime 200: înainte era tăiat la 60


def test_anii_dinainte_de_2024_refuzati_cu_motiv():
    with pytest.raises(ValueError, match="altă structură"):           # D101GValidator: „2024-01 J2.0.0”; 2022-2023 = J1.0.1
        d101g.genereaza(None, None, Perioada(2023), dict(PROF, cota=16, P01=1000))


@pytest.mark.parametrize("an,m", [
    (2025, dict(P01=1000)),
    (2025, COMPLET),
    (2024, dict(P01a=5000, P02=1000, P13=2000)),
    (2026, dict(P01=10000, P10=5000)),
    (2025, dict(P01=1000, d_recN=1)),
    (2025, dict(P01=1000, d_anulare=1, temei=1)),
    (2025, dict(P01=1000, d_reglem=1)),
], ids=["minim", "complet", "pierdere-2024", "imca-2026", "rect-notificare", "anulare-temei1", "bnr-asf"])
def test_duk_valid_izolat(an, m):
    _rad_, xml, _r = _rad(an=an, **m)
    v = _duk(xml)
    assert v["stare"] == "valid", v         # validatorul oficial D101GValidator J2.0.0: „stare valid, fara erori”


def test_duk_valid_pe_firma_din_baza():
    """Firma vine din `firma_profil` (schemă efemeră din tenant_template, în ROLLBACK), nu din `manual`: `pull` + adresa compusă."""
    from core import db as _db
    from core import tenant_provisioning as _tp
    _db.init_pool()
    conn = _db.pool().getconn()
    s = "ztest_lot11_d101g"
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % s)
            cur.execute(_tp.parametrizeaza_template(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                                       "tenant_template.sql"), encoding="utf-8").read(), s))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, adresa, oras, judet, caen, declarant_nume, declarant_prenume, "
                        "declarant_functie) VALUES (1, 'PROBA D101G SRL', '14399840', 'Str. Probei 9', 'Cluj-Napoca', 'CJ', '6920', "
                        "'Popescu', 'Ion', 'ADMINISTRATOR')" % s)
            cur.execute("SET LOCAL search_path TO %s, public" % s)
        xml, _res = d101g.genereaza(conn, s, Perioada(2025), {"P01": 250000, "P02": 10000, "P02a": 10000, "P13": 30000})
    finally:
        conn.rollback()
        _db.pool().putconn(conn)
    rad = ET.fromstring(xml.encode("utf-8"))
    assert rad.get("cif") == "14399840" and rad.get("adresa") == "Str. Probei 9 Cluj-Napoca CJ" and rad.get("CAEN") == "6920"
    # rd.3 = rd.1 - rd.21 = 240.000; rd.4 = 16% x 240.000 = 38.400 (cota din registru, CF art.17); rd.15 = 38.400 - rd.13 30.000
    assert (rad.get("P03"), rad.get("P04"), rad.get("P15")) == ("240000", "38400", "8400")
    v = _duk(xml)
    assert v["stare"] == "valid", v


def test_garda_niciun_xfail_de_validator_in_afara_registrului_datoriei():
    """GARDĂ (clasa C70: „generator ascuns după un xfail de infrastructură”). D101G a stat două luni în spatele unui
    `xfail(strict=True)` local („schema v2 nedeployata”, core/test_declaratii_lot5_duk.py) — validatorul v2 era de fapt instalat, iar
    XML-ul era greșit; un xfail strict pe o probă DUK picată din altă cauză rămânea „verde”. Datoria verificabilă stă într-un singur loc,
    `core/test_datorie.py` (CLAUDE.md „DE_FACUT.md nu mai există”), unde motivul se citește și se recapitulează. Orice alt fișier de teste
    cu un xfail care pomenește validatorul / DUK pică aici. MUTAȚIE: xfail-ul vechi pus înapoi pe cazul D101G -> roșu."""
    import glob
    import re
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rele = []
    for f in sorted(glob.glob(os.path.join(rad, "core", "test_*.py"))):
        if os.path.basename(f) in ("test_datorie.py", os.path.basename(__file__)):
            continue
        s = open(f, encoding="utf-8").read()
        for m in re.finditer(r"mark\.xfail\((.{0,600}?)\)\)?", s, re.S):
            if re.search(r"DUK|validator", m.group(1), re.I):
                rele.append("%s:%d" % (os.path.basename(f), s.count("\n", 0, m.start()) + 1))
    assert not rele, "xfail de validator în afara core/test_datorie.py: %s" % rele
