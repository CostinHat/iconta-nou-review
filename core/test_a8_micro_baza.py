# -*- coding: utf-8 -*-
"""[A8, 17.09.2026] Baza micro = venituri din ORICE sursă (70x+75x+76x) minus 709, nu doar 70x.

Constatarea A8 (micro): `repo_d100.select_inregistrari_linii` lua venituri = `cont_credit LIKE '70%'`.
Art. 53(1) CF: venituri din orice sursă (75x/76x intră); 709 (reduceri comerciale) se scade. Un venit
financiar 766 nu intra în baza micro, iar reducerile 709 nu se scădeau. PICĂ pe codul de dinainte
(baza = doar 70x), TRECE după.

Partea de PROFIT a lui A8 (calcul cumulat de la începutul anului) e restanță deschisă cu motiv în
CONFORMITATE.md — cere sincronizarea celor trei căi (generator + thunk + reconciliere) și e specificată
acolo cu algoritmul.
"""
from __future__ import annotations

import contextlib

import pytest

from core import declaratii_api
from core import db as _db

SCH = "ztest_a8_micro"
AN, TRIM = 2026, 1


class _ConnProxy:
    def __init__(self, real):
        object.__setattr__(self, "_real", real)

    def __getattr__(self, n):
        return getattr(self._real, n)

    def commit(self):
        pass

    def rollback(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _nota(cur, data, debit, credit, suma):
    cur.execute("INSERT INTO inregistrari (data,descriere,sursa,status) "
                "VALUES (%s,'test','manual','validata') RETURNING id", (data,))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) "
                "VALUES (%s,%s,%s,%s)", (nid, debit, credit, suma))


@pytest.fixture
def firma_micro(monkeypatch):
    from core import tenant_provisioning as _tp
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,regim_fiscal,"
                        "declarant_nume,declarant_prenume,declarant_functie) "
                        "VALUES (1,'ZT MICRO SRL','14399840','Str 1','Cluj-Napoca','CJ','6202',"
                        "'micro','Popescu','Ion','admin')")
            # T1 2026: venit din exploatare 704=10.000; venit financiar 766=2.000; reducere 709 debit 500.
            _nota(cur, '2026-02-10', '4111', '704', 10000)
            _nota(cur, '2026-02-15', '5121', '766', 2000)
            _nota(cur, '2026-03-01', '709', '4111', 500)

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema
                          else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)
        yield {"conn": conn}
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback()
        p.putconn(conn)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_baza_micro_include_766_si_scade_709(firma_micro):
    with firma_micro["conn"].cursor() as c:
        c.execute('SET search_path TO "%s", public' % SCH)
    _xml, res = declaratii_api.genereaza(_ConnProxy(firma_micro["conn"]), SCH, "d100",
                                         {"an": AN, "trim": TRIM})
    # baza = 10.000 (704) + 2.000 (766) - 500 (709) = 11.500; cod 121 = 1% x 11.500 = 115.
    def _cod(o):
        return str(o["cod_oblig"] if isinstance(o, dict) else getattr(o, "cod_oblig", ""))
    def _suma(o):
        return int(o["suma_dat"] if isinstance(o, dict) else getattr(o, "suma_dat"))
    suma121 = None
    for o in getattr(res, "obligatii", []) or []:
        if _cod(o) == "121":
            suma121 = _suma(o)
    assert suma121 == 115, "cod 121 = %r (așteptat 115 = 1%% x 11.500: 704+766-709)" % suma121
