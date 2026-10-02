# -*- coding: utf-8 -*-
"""GARD — D205 împarte dividendele după cotele de la DATA DISTRIBUIRII, nu după cotele de azi (lot 19 pct.4e, 02.10.2026).

Defectul: `d205` lua totalul anului din contul 457 și îl înmulțea cu cotele ACTUALE din `asociati` (fără istoric). La
o cesiune în cursul anului, asociatul ieșit nu mai apărea deloc în D205 pentru dividendul care i se distribuise, iar
cesionarul îl declara ca venit al lui. Importul asociaților ștergea structura veche fără urmă.

Temei (Legea 31/1990, corpus `anaf_surse/legea_31_1990_societatile.txt`):
  · art.67 alin.(2): „Dividendele se distribuie asociaților proporțional cu cota de participare la capitalul social
    vărsat”;
  · art.67 alin.(6): „Dividendele care se cuvin după data transmiterii acțiunilor aparțin cesionarului, în afară de
    cazul în care părțile au convenit altfel.”
Impozitul: CF art.97 alin.(7) — 16% din 01.01.2026 (rata de la data distribuirii, A6 — neschimbat aici).

Scenariu 2026: A deține 100% până la cesiune; din 01.04.2026, B deține 100%. Distribuire 15.02 (10.000, a lui A),
plătită 10.05; distribuire 20.06 (5.000, a lui B), plătită 01.07.
"""
import xml.etree.ElementTree as ET

import pytest

from core import db as _db, tenant_provisioning as _tp
from core import asociati_import_api, d205
from core.common import Perioada

_SCHEMA = "test_d205_cesiune"
# CNP-uri cu cifra de control VERIFICATĂ (algoritmul din CLAUDE.md)
_A, _B = "1900101410011", "2900202410026"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _nota(cur, data, debit, credit, suma):
    cur.execute("INSERT INTO inregistrari (data, descriere, status) VALUES (%s,'dividende','validata') RETURNING id", (data,))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)",
                (nid, debit, credit, suma))


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,declarant_nume,declarant_prenume,"
                            "declarant_functie) VALUES (1,'DIVIDEND SRL','14399840','Str 1','Buc','B','POP','ION','ADMINISTRATOR')")
                _nota(cur, "2026-02-15", "117", "457", 10000)
                _nota(cur, "2026-05-10", "457", "5121", 10000)
                _nota(cur, "2026-06-20", "117", "457", 5000)
                _nota(cur, "2026-07-01", "457", "5121", 5000)
            # structura inițială, apoi cesiunea cu data ei — prin importul REAL al asociaților
            asociati_import_api.importa(c, [{"nume": "ASOCIAT A", "cnp": _A, "cota": 100}])
            r = asociati_import_api.importa(c, [{"nume": "ASOCIAT B", "cnp": _B, "cota": 100}], data_cesiune="2026-04-01")
            assert r == {"importati": 1, "arhivati": 1}
            yield c
        finally:
            c.rollback()


def _benef(xml):
    return {el.get("cifR"): el.attrib for el in ET.fromstring(xml).iter() if el.tag.split("}")[-1] == "benef"}


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_dividendul_distribuit_inainte_de_cesiune_ramane_al_cedentului(conn):
    xml, res = d205.genereaza(conn, _SCHEMA, Perioada(2026))
    b = _benef(xml)
    # Legea 31/1990 art.67 alin.(2)+(6): distribuirea din 15.02 (structura A 100%) e a lui A; cea din 20.06 a lui B
    assert set(b) == {_A, _B}
    assert (b[_A]["baza1"], b[_A]["divid_P"], b[_A]["divid_D"]) == ("10000", "10000", "10000")
    assert (b[_B]["baza1"], b[_B]["divid_P"], b[_B]["divid_D"]) == ("5000", "5000", "5000")
    # CF art.97 alin.(7): 16% pe dividendele distribuite din 2026
    assert (b[_A]["imp1"], b[_B]["imp1"]) == ("1600", "800")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_calea_a_doua_si_verificarea_incrucisata_vad_aceeasi_impartire(conn):
    from core.d205_reconciliere import reconciliaza
    from core import control_incrucisat
    _xml, res = d205.genereaza(conn, _SCHEMA, Perioada(2026))      # poarta (calea a doua) e cablată: ar fi ridicat
    assert reconciliaza(conn, _SCHEMA, Perioada(2026), res)["divergente"] == []
    # verificarea încrucișată folosește ACEEAȘI derivare (sursă unică), nu o replică pe cotele de azi
    assert control_incrucisat._thunk_d205(conn, _SCHEMA, 2026, 12)()["divergente"] == []


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fara_cesiune_impartirea_ramane_cea_de_dinainte(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM asociati_istoric")
        cur.execute("DELETE FROM asociati")
        cur.execute("INSERT INTO asociati (nume, cnp, cota) VALUES ('ASOCIAT A',%s,60),('ASOCIAT B',%s,40)", (_A, _B))
    b = _benef(d205.genereaza(conn, _SCHEMA, Perioada(2026))[0])
    # o singură structură pe tot anul -> total plătit (15.000) × cotă, ca înainte
    assert (b[_A]["baza1"], b[_B]["baza1"]) == ("9000", "6000")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cesiunea_refuza_data_din_viitor_si_ordinea_inversa(conn):
    with pytest.raises(ValueError, match="viitor"):
        asociati_import_api.importa(conn, [{"nume": "ASOCIAT A", "cnp": _A, "cota": 100}], data_cesiune="2099-01-01")
    with pytest.raises(ValueError, match="după ultima cesiune"):
        asociati_import_api.importa(conn, [{"nume": "ASOCIAT A", "cnp": _A, "cota": 100}], data_cesiune="2026-03-01")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d205_cu_cesiune_e_valid_la_duk(conn):
    from core import duk
    if not duk.poate_valida("d205"):
        pytest.skip("DUK d205 indisponibil")
    xml, _res = d205.genereaza(conn, _SCHEMA, Perioada(2026))
    r = duk.valideaza(xml, "d205", an=2026)
    assert r["stare"] == "valid", r.get("erori")
