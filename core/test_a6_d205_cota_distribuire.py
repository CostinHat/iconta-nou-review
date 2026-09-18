# -*- coding: utf-8 -*-
"""[A6, 18.09.2026] D205: cota impozitului pe dividende se ia după DATA DISTRIBUIRII (creditul 457),
nu după 31.12 al anului declarației.

Legea 141/2025 art. VII: 16% pe dividendele DISTRIBUITE începând cu 01.01.2026; alin.(2): dividendele
interimare distribuite în 2025 rămân 10% chiar plătite/regularizate în 2026 (fără recalculare).

Caz contabil, de la nota de distribuire în jos:
  2025-12-20  distribuire: 117 = 457, 100.000  (credit 457 -> datoria de dividend, în 2025)
  2026-01-15  plată:       457 = 5121, 100.000 (debit 457 -> se stinge, în 2026)

D205/2026 include plata (100.000). Cota corectă = 10% (distribuit în 2025) -> imp1 = 10.000.
BUG (`d205.py:363` folosea cota la 31.12.2026 = 16%): imp1 = 16.000. PICĂ pe codul de dinainte (16.000),
TRECE după (10.000). Reconcilierea recalculează FIFO INDEPENDENT aceeași atribuire -> 0 divergențe.
"""
from __future__ import annotations

import contextlib

import pytest

from core import declaratii_api
from core import d205_reconciliere as _rec
from core.common import Perioada
from core import db as _db

SCH = "ztest_a6_d205"
AN = 2026


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
def firma_div(monkeypatch):
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
                        "VALUES (1,'ZT DIV SRL','14399840','Str 1','Cluj-Napoca','CJ','6202',"
                        "'micro','Popescu','Ion','admin')")
            cur.execute("INSERT INTO asociati (nume, cnp, cota) VALUES ('ASOCIAT UNU','1900101410011',100)")
            # Distribuire în 2025 (credit 457), plată în 2026 (debit 457).
            _nota(cur, '2025-12-20', '117', '457', 100000)
            _nota(cur, '2026-01-15', '457', '5121', 100000)

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
def test_cota_dupa_data_distribuirii_nu_anul_declaratiei(firma_div):
    with firma_div["conn"].cursor() as c:
        c.execute('SET search_path TO "%s", public' % SCH)
    _xml, res = declaratii_api.genereaza(_ConnProxy(firma_div["conn"]), SCH, "d205", {"an": AN})
    assert len(res.beneficiari) == 1, "un beneficiar (asociatul cu cota 100%%)"
    b = res.beneficiari[0]
    # distribuit 2025 -> 10%; 100.000 x 10% = 10.000 (nu 16.000 = cota 2026 pe anul declarației).
    assert int(b.baza1) == 100000, "baza1 = dividendul plătit 100.000; găsit %r" % int(b.baza1)
    assert int(b.imp1) == 10000, (
        "imp1 = %r (așteptat 10.000 = 10%% cota DISTRIBUIRII 2025; 16.000 = bug pe anul declarației 2026)"
        % int(b.imp1))

    # A doua cale recalculează FIFO INDEPENDENT -> aceeași atribuire, fără divergențe.
    with firma_div["conn"].cursor() as c:
        c.execute('SET search_path TO "%s", public' % SCH)
    rap = _rec.reconciliaza(_ConnProxy(firma_div["conn"]), SCH, Perioada(AN), res, None)
    assert rap["divergente"] == [], "reconcilierea D205 trebuie să fie FIFO pe distribuire, fără divergențe: %r" % rap
