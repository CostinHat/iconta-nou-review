# -*- coding: utf-8 -*-
"""[lotul 11, C96] D112: tipul contractului după timpul de lucru (B1_3) și orele lucrate (B1_6) / suspendate (B1_7) după norma salariatului.

SURSE (locale):
- OPANAF 605/2026 anexa 2 (`anaf_surse/opanaf_605_2026_d112.txt`), B.1: rândul 3 „se completează cu N (norma întreagă 6, 7, 8) sau Pn
  (parţial P1, P2, ..., P7), unde "N" reprezintă numărul de ore zilnice de contract parţial”; rândul 4 „programul normal de lucru
  specific locului de muncă […] art. 112 alin. (1) din Legea nr. 53/2003 […] Norma zilnică poate să fie de 8, 7 sau 6 ore”; rândul 5 „Ore
  lucrate efectiv în lună […] perioada suportată de angajator potrivit legii se consideră perioadă lucrată”.
- Structura D112 (`anaf_surse/d112_struct_anaf.txt`): „B1_3 … Valori : N,P1,P2,P3,P4,P5,P6,P7 unde i<B1_4”, „daca B1_3 = ‘N’ atunci B1_6
  <= NZL * B1_4 / daca B1_3= ‘Pi ‘atunci B1_6 <= NZL* i”, „daca B1_3= ‘Pi ‘ atunci B1_7<= NZL* i - B1_6”; nomenclatorul 12 „P4 - cu timp
  de lucru partial de 4 ore”.

Până la 22.10.2026: B1_3 = „N” fix, iar B1_6 / B1_7 se socoteau cu 8 ore pe zi și la normă parțială; zilele de concediu medical plătite
de angajator nu intrau în orele lucrate.

CNP-urile de test sunt verificate cu algoritmul cifrei de control (CLAUDE.md): 1800101410013, 1800202410011.
"""
import pytest

from core import d112, db as _db
from core.common import Perioada
from core.test_lot11_s9_deducere_plafon import _setup, structura, unic

_SCHEMA = "test_lot11_s9_norma"
_PARTIAL = {"cnp": "1800101410013", "nume": "PARTIAL", "dn": "1980-06-01", "brut": 2500, "pt": True, "ore": 4}
_INTREG = {"cnp": "1800202410011", "nume": "INTREG", "dn": "1980-06-01", "brut": 5000}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


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


def _genereaza(conn, salariati, sql_pornire=()):
    with conn.cursor() as cur:
        _setup(cur, salariati, schema=_SCHEMA)
        for q in sql_pornire:
            cur.execute(q)
    conn.commit()
    return d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=10))[0]


def _duk_valid(xml):
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    rez = duk.valideaza(xml, "d112", an=2026, luna=10)
    assert rez["stare"] == "valid", rez


def _b1(xml, cnp):
    el = unic(structura(xml)[cnp], "asiguratB1")
    return (el["B1_3"], int(el["B1_4"]), int(el["B1_6"]), int(el.get("B1_7", 0)), int(el["B1_15"]))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c96_norma_partiala_de_4_ore_si_norma_intreaga(conn):
    """10/2026 (22 de zile lucrătoare): normă parțială de 4 ore -> B1_3 = P4, B1_4 = 8, B1_6 = 22 × 4 = 88; normă întreagă -> N, 8, 176.
    ROȘU pe codul vechi: P4 era „N”, iar B1_6 = 176 și la normă parțială. DUK valid."""
    xml = _genereaza(conn, [_PARTIAL, _INTREG])
    # rândul 3: „Pn (parţial P1, P2, ..., P7)”; rândul 4: programul normal al locului de muncă (Codul muncii art.112 alin.(1)); B1_6 <= NZL × i
    assert _b1(xml, "1800101410013") == ("P4", 8, 88, 0, 22)
    assert _b1(xml, "1800202410011") == ("N", 8, 176, 0, 22)
    _duk_valid(xml)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c96_orele_cm_platite_de_angajator_sunt_ore_lucrate(conn):
    """Normă parțială de 4 ore cu un certificat de 5 zile (4 plătite de angajator, ziua de diminuare neplătită): B1_15 = 22 − 5 = 17 zile
    lucrate, B1_6 = (17 + 4) × 4 = 84 (rândul 5: „perioada suportată de angajator potrivit legii se consideră perioadă lucrată”). DUK valid."""
    cm = ("INSERT INTO concedii_medicale (salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,brut_fnuass,baza,media_zilnica,"
          "serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere) SELECT id,2026,10,'01',5,4,0,250,0,2500,0,'AB','1',"
          "'2026-10-05','2026-10-05','2026-10-09',1 FROM salariati WHERE nume='PARTIAL'")
    xml = _genereaza(conn, [_PARTIAL, _INTREG], [cm])
    assert _b1(xml, "1800101410013") == ("P4", 8, 84, 0, 17)
    _duk_valid(xml)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c96_orele_suspendate_cu_orele_contractului(conn):
    """Normă parțială de 4 ore, suspendare de 5 zile lucrătoare (12–16.10.2026): B1_7 = 5 × 4 = 20, B1_6 = 17 × 4 = 68 (structura: „daca B1_3=
    ‘Pi ‘ atunci B1_7<= NZL* i - B1_6”). ROȘU pe codul vechi: B1_7 = 40, B1_6 = 136. DUK valid."""
    susp = ("INSERT INTO suspendari_contract (salariat_id, data_inceput, data_sfarsit, tip, temei) SELECT id, '2026-10-12', '2026-10-16', "
            "'suspendare', 'proba' FROM salariati WHERE nume='PARTIAL'")
    xml = _genereaza(conn, [_PARTIAL, _INTREG], [susp])
    assert _b1(xml, "1800101410013") == ("P4", 8, 68, 20, 17)
    _duk_valid(xml)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.parametrize("ore", [4.5, 8])
def test_c96_norma_partiala_fara_ore_intregi_1_7_se_refuza_numit(conn, ore):
    """Normă parțială cu 4,5 sau 8 ore pe zi: D112 n-o poate declara (P1–P7, „i<B1_4”) -> generarea se oprește, numind salariatul și
    orele, în loc să declare o normă inventată."""
    with pytest.raises(ValueError, match=r"^D112: salariatul PARTIAL \(CNP 1800101410013\) are normă parțială cu (4,5|8) ore pe zi, dar "
                                         r"D112 declară norma parțială în ore întregi, de la 1 la 7 \(tipul de contract P1–P7\)\."):
        _genereaza(conn, [{**_PARTIAL, "ore": ore}])
