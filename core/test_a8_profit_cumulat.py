# -*- coding: utf-8 -*-
"""[A8-profit, 18.09.2026] Impozitul pe profit (cod 103) e CUMULAT de la 01.01 (art.41 CF); plata
trimestrială = diferența față de ce s-a impozitat deja, iar pierderea unui trimestru scade cumulatul.

Constatarea A8 (profit): `d100.pull` întorcea veniturile/cheltuielile TRIMESTRULUI izolat, iar
`deriva_obligatii` impozita profitul trimestrului. Un trimestru cu profit după unul cu pierdere plătea
16% pe TOT profitul lui, nu pe cumulat -> supra-declarare. Caz contabil, de la factură în jos:

  Q1 2026: venit 704 = 30.000; cheltuieli 6xx = 80.000  -> profit trimestru = -50.000 (PIERDERE)
  Q2 2026: venit 704 = 130.000; cheltuieli 6xx = 50.000 -> profit trimestru = +80.000

  Cumulat la sfârșitul Q2 = -50.000 + 80.000 = +30.000. Impozit datorat CUMULAT = 30.000 x 16% = 4.800,
  minus 0 impozitat în Q1 (pierdere) = 4.800 DE PLATĂ în Q2.

  BUG (trimestru izolat): Q2 = 80.000 x 16% = 12.800. PICĂ pe codul de dinainte (12.800), TRECE după
  (4.800). Și reconcilierea (a doua cale, d100_reconciliere) recalculează CUMULAT la fel -> 0 divergențe.

  Q1 izolat: profit trimestru -50.000 -> D100 se refuză pe zero (pierdere, fără avans), la fel cumulat.
"""
from __future__ import annotations

import contextlib

import pytest

from core import declaratii_api
from core import d100_reconciliere as _rec
from core.common import Perioada
from core import db as _db

SCH = "ztest_a8_profit"
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
def firma_profit(monkeypatch):
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
                        "VALUES (1,'ZT PROFIT SRL','14399840','Str 1','Cluj-Napoca','CJ','6202',"
                        "'profit','Popescu','Ion','admin')")
            # Q1 2026: venit 30.000, cheltuieli 80.000 -> pierdere trimestru -50.000.
            _nota(cur, '2026-02-10', '4111', '704', 30000)
            _nota(cur, '2026-03-05', '628', '401', 80000)
            # Q2 2026: venit 130.000, cheltuieli 50.000 -> profit trimestru +80.000; cumulat +30.000.
            _nota(cur, '2026-05-10', '4111', '704', 130000)
            _nota(cur, '2026-06-05', '628', '401', 50000)

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


def _cod(o):
    return str(o["cod_oblig"] if isinstance(o, dict) else getattr(o, "cod_oblig", ""))


def _suma(o):
    return int(o["suma_dat"] if isinstance(o, dict) else getattr(o, "suma_dat"))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_profit_trim2_pe_cumulat_nu_pe_trimestru(firma_profit):
    with firma_profit["conn"].cursor() as c:
        c.execute('SET search_path TO "%s", public' % SCH)
    _xml, res = declaratii_api.genereaza(_ConnProxy(firma_profit["conn"]), SCH, "d100",
                                         {"an": AN, "trim": 2})
    suma103 = None
    for o in getattr(res, "obligatii", []) or []:
        if _cod(o) == "103":
            suma103 = _suma(o)
    # cumulat +30.000 x 16% - 0 (Q1 pierdere) = 4.800; izolat ar fi 80.000 x 16% = 12.800.
    assert suma103 == 4800, (
        "cod 103 Q2 = %r (așteptat 4.800 = 16%% x profit CUMULAT 30.000; 12.800 = bug pe trimestru izolat)"
        % suma103)

    # A doua cale (reconcilierea) recalculează CUMULAT la fel -> nicio divergență (sincron generator<->cale2).
    per2 = Perioada(AN, trim=2)
    with firma_profit["conn"].cursor() as c:
        c.execute('SET search_path TO "%s", public' % SCH)
    rap = _rec.reconciliaza(_ConnProxy(firma_profit["conn"]), per2, res, None)
    assert rap["divergente"] == [], "reconcilierea profit trebuie să fie cumulativă și fără divergențe: %r" % rap


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_profit_trim1_pierdere_se_refuza(firma_profit):
    with firma_profit["conn"].cursor() as c:
        c.execute('SET search_path TO "%s", public' % SCH)
    # Q1 cumulat = -50.000 (pierdere) -> fără avans de impozit; D100 se refuză pe zero (structural:
    # genereaza ridică ValueError). Formularea mesajului e testată în test_d100_profit_baza.
    with pytest.raises(ValueError):
        declaratii_api.genereaza(_ConnProxy(firma_profit["conn"]), SCH, "d100", {"an": AN, "trim": 1})
