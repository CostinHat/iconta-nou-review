# -*- coding: utf-8 -*-
"""Lotul 13, comanda 13.1, zona `fact` — 542: „Seria F2T stabilită la prima factură a pornit de la nr. 2 (contorul vechi), deci F2T1
lipsește și seria are o gaură. Seria nouă pornește de la 1 sau de la numărul ales de contabil.”

Temei: CF art.319 alin.(20) lit.a) — factura cuprinde „numărul de ordine, în baza uneia sau a mai multor serii, care identifică în mod unic
factura”: contorul e al seriei. Schemă efemeră din template, în tranzacție anulată (fixtura lui 417; seria de pornire „F1A”)."""
import pytest

from core import facturi_api
from core.test_417_storno_trimitere import _db_ok, conn  # noqa: F401 — fixtura

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _contor(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT serie_factura, urmator_numar_factura FROM firma_profil WHERE id = 1")
        return tuple(cur.fetchone())


def _emisa(conn, numar, serie):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, serie, data_emitere, total, tva, directie, status, tip) "
                    "VALUES (%s, %s, '2099-01-05', 100, 0, 'emisa', 'de_preluat', 'factura')", (numar, serie))


@DB
def test_def_542_seria_noua_porneste_de_la_1_nu_de_la_contorul_vechi(conn):
    """F1A a ajuns la 2 (o factură „1” emisă înainte, fără serie) -> seria se schimbă în F2T -> următorul număr e 1 (F2T1), nu 2.
    MUTAȚIE: fără rândul care pune contorul seriei noi -> rămâne 2 -> pică."""
    _emisa(conn, "1", None)
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET urmator_numar_factura = 2 WHERE id = 1")
    assert facturi_api.seteaza_numerotare(conn, serie="F2T") == {"ok": True}
    assert _contor(conn) == ("F2T", 1)


@DB
def test_def_542_intoarcerea_la_o_serie_folosita_continua_dupa_ultima_factura_ei(conn):
    """Seria F1A are emise F1A4 și F1A5; contorul firmei e pe altă serie -> întoarcerea la F1A continuă cu 6 (nu 1: F1A1 ar fi a doua
    factură cu un număr deja emis)."""
    _emisa(conn, "F1A4", "F1A")
    _emisa(conn, "F1A5", "F1A")
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET serie_factura = 'ALT', urmator_numar_factura = 9 WHERE id = 1")
    assert facturi_api.seteaza_numerotare(conn, serie="F1A") == {"ok": True}
    assert _contor(conn) == ("F1A", 6)


@DB
def test_def_542_seria_noua_cu_numarul_ales_de_contabil(conn):
    """Seria nouă cu numărul de start ales (ex. continuarea unui chitanțier / program vechi) -> contorul e numărul ales; sub primul număr
    liber al seriei -> refuzul lângă câmp."""
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET urmator_numar_factura = 7 WHERE id = 1")
    assert facturi_api.seteaza_numerotare(conn, serie="NOU", numar_start=40) == {"ok": True}
    assert _contor(conn) == ("NOU", 40)
    _emisa(conn, "NOU40", "NOU")
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET serie_factura = 'ALT' WHERE id = 1")
    r = facturi_api.seteaza_numerotare(conn, serie="NOU", numar_start=3)
    assert r["ok"] is False and r["erori_campuri"][0]["camp"] == "numar_start", r


def test_def_542_primul_numar_liber_din_serie_e_pur_pe_numere():
    """`urmatorul_in_serie` ia numai numerele „<serie><cifre>” ale seriei (o factură „F2TX” sau din altă serie nu contează)."""
    class _C:
        def __init__(self, r): self.r = r
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def execute(self, *a): pass
        def fetchall(self): return self.r

    class _Conn:
        def __init__(self, r): self.r = r
        def cursor(self): return _C(self.r)

    assert facturi_api.urmatorul_in_serie(_Conn([("F2T2",), ("F2T3",), ("F2TX",)]), "F2T") == 4
    assert facturi_api.urmatorul_in_serie(_Conn([]), "F2T") == 1
