# -*- coding: utf-8 -*-
"""[lotul 13, deficiența 683 — a lui Code] „Casă › Avans spre decontare nu pune salariatul pe rândul notei: 542 nu se urmărește pe
persoană.” Pe drumul Operațiunilor (670 a) 542 poartă salariatul; pe Casă nu. Acum `casa_api.adauga` cere salariatul (`salariat_id`,
refuz lângă `c-salariat`), îl verifică ca Operațiunile (`core.salariat_decont.alege`: în evidență, angajat la data dispoziției) și scrie
rândul 542 cu numele și CNP-ul lui; stornarea păstrează partenerul rândului inversat; previzualizarea spune refuzul înainte de „Adaugă”.

Temei: CF art.76 alin.(2) lit.k (decontul de deplasare e al unui salariat); „542 trebuie urmărit pe persoană” — comanda Costin 13.1.
OMFP 1802/2014, funcțiunea contului 542 „Avansuri de trezorerie”: contul „se debitează cu sumele acordate [...] pentru decontare”,
pe persoana care le-a primit (evidența analitică pe salariat).

Schemă efemeră din template, ștearsă la ieșire. Datele de PORNIRE (salariații) scrise direct — salariații sunt scrierea altui modul."""
import io
import pathlib

import pytest

from core import casa_api as _ca, db as _db, tenant_provisioning as _tprov
from core.identitate import valideaza_cnp

_SCH = "efemer_lot13_val6_casa"
_RAD = pathlib.Path(__file__).resolve().parent.parent
_CNP = "1900101400012"   # S=1, 90-01-01, județ 40, nr. 001; cifra de control verificată în `test_cnp_de_proba_e_valid`


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open(_RAD / "tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % _SCH)
        c.commit()
    with _db.get_conn(_SCH) as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO salariati (id, cnp, nume, prenume, data_angajare) OVERRIDING SYSTEM VALUE VALUES (1, %s, 'Popescu', 'Ion', '2026-03-01')", (_CNP,))
            cur.execute("INSERT INTO salariati (id, cnp, nume, prenume, data_angajare) OVERRIDING SYSTEM VALUE VALUES (2, '1900101400020', 'Nou', 'Venit', '2026-11-01')")
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _avans(**kw):
    return dict({"data": "2026-10-12", "categorie": "avans_decontare", "suma": 300, "document": "DP1"}, **kw)


def _incarca_casa(conn):
    assert _ca.adauga(conn, _SCH, {"data": "2026-10-01", "categorie": "ridicare_banca", "suma": 1000, "document": "DI1"}).get("eroare") is None


def _linii(conn, iid):
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma, partener_cui, partener_nume FROM inregistrari_linii WHERE inregistrare_id=%s ORDER BY id", (iid,))
        return cur.fetchall()


def test_cnp_de_proba_e_valid():
    assert valideaza_cnp(_CNP)[0], _CNP


def test_fara_salariat_refuz_lang_camp(conn):
    _incarca_casa(conn)
    r = _ca.adauga(conn, _SCH, _avans())
    assert "eroare" in r and [c["camp"] for c in r["erori_campuri"]] == ["c-salariat"], r


def test_salariat_necunoscut_refuz(conn):
    _incarca_casa(conn)
    r = _ca.adauga(conn, _SCH, _avans(salariat_id=999))
    assert [c["camp"] for c in r["erori_campuri"]] == ["c-salariat"] and "evidența" in r["eroare"], r


def test_salariat_neangajat_la_data_refuz(conn):
    _incarca_casa(conn)
    r = _ca.adauga(conn, _SCH, _avans(salariat_id=2))   # angajat de la 01.11.2026, dispoziția e din 12.10
    assert [c["camp"] for c in r["erori_campuri"]] == ["c-salariat"] and "nu era salariat" in r["eroare"], r


def test_salariat_angajat_nota_are_542_pe_persoana(conn):
    _incarca_casa(conn)
    r = _ca.adauga(conn, _SCH, _avans(salariat_id=1, partener="Scris de mână SRL", cui="14399840"))
    assert r.get("eroare") is None, r
    assert _linii(conn, r["inregistrare_id"]) == [("542", "5311", 300, _CNP, "Popescu Ion")]
    with conn.cursor() as cur:
        cur.execute("SELECT partener, cui FROM casa_operatiuni WHERE id=%s", (r["id"],))
        assert cur.fetchone() == ("Popescu Ion", _CNP)   # partenerul scris de mână nu mai contează: operațiunea poartă salariatul


def test_alte_categorii_nu_cer_salariat(conn):
    r = _ca.adauga(conn, _SCH, {"data": "2026-10-01", "categorie": "ridicare_banca", "suma": 50, "document": "DI9"})
    assert r.get("eroare") is None, r


def test_previzualizarea_spune_refuzul_salariatului(conn):
    _incarca_casa(conn)
    p = _ca.previzualizare(conn, _SCH, _avans(salariat_id=2))
    assert p["refuz"] and "nu era salariat" in p["refuz"], p["refuz"]
    assert _ca.previzualizare(conn, _SCH, _avans(salariat_id=1))["refuz"] is None


def test_storno_pastreaza_salariatul_pe_randul_inversat(conn):
    _incarca_casa(conn)
    r = _ca.adauga(conn, _SCH, _avans(salariat_id=1))
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status='validata' WHERE id=%s", (r["inregistrare_id"],))
    s = _ca.storneaza(conn, _SCH, r["id"], "2026-10-13")
    assert s.get("eroare") is None, s
    assert _linii(conn, s["inregistrare_id"]) == [("542", "5311", -300, _CNP, "Popescu Ion")]
