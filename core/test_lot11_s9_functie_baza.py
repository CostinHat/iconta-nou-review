# -*- coding: utf-8 -*-
"""[lotul 11, C90] D112: salariatul fără funcție de bază la angajator se declară cu E3_3 = 2 și în secțiunea E2, nu cu E3_3 = 1 / E1.

SURSA. Structura D112 (`anaf_surse/d112_struct_anaf.txt`), E3_3 „Funcţie de baza”: „=1, pentru functia de baza / =2, pentru venit in
afara functiei de baza / =3, nu e cazul”; E3_11 / E3_12 / E3_1221 / E3_1222 / E3_13: „Daca E3_3=1 atunci … >=0 / Altfel … =0 / ERR-
campul … se completeaza doar pentru functia de baza”; E1 (funcția de bază) = Σ E3 „pentru E3_3=1”, E2 („Alte venituri din salarii”) = Σ
E3 „pentru E3_3=2”; „ERR- Aveti o sectiune asiguratE3 completata pentru venituri in afara functiei de baza si sectiune asiguratE2
lipsa”. OPANAF 605/2026 anexa 1.2, E.3 rândul 3: „se completează cu valorile "1 - da", "2 - nu" sau "3 - nu e cazul". Valorile "1 - da"
şi "2 - nu" se completează pentru veniturile din salarii”; E.2: „Se completează pentru beneficiarul de venit care realizează venituri
din salarii şi asimilate salariilor, în afara funcţiei de bază”. CF art.77 alin.(1): deducerea personală se acordă „numai pentru
veniturile din salarii la locul unde se află funcția de bază”; CF art.78 alin.(2) lit.b: în celelalte cazuri baza = venitul brut minus
contribuțiile.

CNP-urile de test sunt verificate cu algoritmul cifrei de control (CLAUDE.md): 1800101410013, 1800202410011.
"""
import pytest

from core import d112, db as _db, stat_plata_api
from core.common import Perioada
from core.test_lot11_s9_deducere_plafon import _int, _setup as _setup_ded, structura

_SCHEMA = "test_lot11_s9_fb"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _setup(cur, salariati):
    _setup_ded(cur, salariati, schema=_SCHEMA)


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c90_fara_functie_de_baza_e3_3_doi_si_sectiunea_e2(conn):
    """Doi salariați, brut 5.000 fiecare, 10/2026: MATUR cu funcție de bază (E3_3=1, E1, deducere 562) și SECUNDAR fără funcție de bază
    (E3_3=2, E2, fără E1, fără deducere, E3_11 = E3_12 = 0, baza = 5.000 − 1.750 = 3.250, impozit 325). ROȘU pe codul vechi: E3_3="1"
    și E1 la ambii."""
    with conn.cursor() as cur:
        _setup(cur, [{"cnp": "1800101410013", "nume": "MATUR", "dn": "1980-06-01", "brut": 5000},
                     {"cnp": "1800202410011", "nume": "SECUNDAR", "dn": "1980-06-01", "brut": 5000, "fb": False, "pers": 2}])
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
    stat = {r["nume_ed"]: r for r in stat_plata_api.stat_plata(conn, _SCHEMA, 2026, 10)}
    assert (stat["SECUNDAR"]["deducere"], stat["SECUNDAR"]["impozit"]) == (0.0, 325.0), stat["SECUNDAR"]   # CF art.77 alin.(1), art.78(2)b
    xml = d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=10))[0]
    a = structura(xml)
    m, s = a["1800101410013"], a["1800202410011"]
    # structura D112, E3_3: „=1, pentru functia de baza / =2, pentru venit in afara functiei de baza”; E1 = Σ „pentru E3_3=1”, E2 = Σ
    # „pentru E3_3=2” -> fiecare asigurat are exact una dintre cele două secțiuni
    assert _int(m, "asiguratE3", "E3_3") == (1,) and len(m.get("asiguratE1", [])) == 1 and len(m.get("asiguratE2", [])) == 0, m
    assert _int(s, "asiguratE3", "E3_3") == (2,) and len(s.get("asiguratE2", [])) == 1 and len(s.get("asiguratE1", [])) == 0, s
    # E3_11 / E3_12: „Altfel … =0 … se completeaza doar pentru functia de baza”
    assert _int(s, "asiguratE3", "E3_11", "E3_12", "E3_121") == (0, 0, 0)
    # E2_1..E2_4 = Σ E3_8 / E3_9 / E3_14 / E3_15 „pentru E3_3=2”
    assert _int(s, "asiguratE2", "E2_1", "E2_2", "E2_3", "E2_4") == (5000, 1750, 3250, 325)
    assert _int(s, "asiguratE3", "E3_14", "E3_15") == (3250, 325)
    assert _int(m, "asiguratE1", "E1_4") == (562,)
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    rez = duk.valideaza(xml, "d112", an=2026, luna=10)
    assert rez["stare"] == "valid", rez


def test_c90_garda_sectiunea_e_dupa_functia_de_baza():
    """Garda, pe câmpurile din calcul (fără bază): `_sectiunea_e` dă E3_3 = 2 și deducerea / persoanele 0 pentru salariatul fără funcție de
    bază, chiar dacă dicționarul lui poartă o deducere (un apelant direct al lui `calcul_d112`); cu funcția de bază, E3_3 = 1 și deducerea
    lui. CF art.77 alin.(1): deducerea „numai pentru veniturile din salarii la locul unde se află funcția de bază”."""
    s = {"deducere": 562, "deducere_baza": 562, "deducere_tineri": 0, "deducere_copii": 0, "persoane_intretinere": 2,
         "baza_impozabila": 2688}
    da = d112._sectiunea_e({**s, "functie_baza": True}, None, 5000, 1250, 500, 1250, 500)
    nu = d112._sectiunea_e({**s, "functie_baza": False}, None, 5000, 1250, 500, 1250, 500)
    assert (da["e3_3"], da["ded"], da["ded_baza"], da["persoane"]) == (1, 562, 562, 2), da
    assert (nu["e3_3"], nu["ded"], nu["ded_baza"], nu["ded_supl"], nu["persoane"]) == (2, 0, 0, 0, 0), nu
