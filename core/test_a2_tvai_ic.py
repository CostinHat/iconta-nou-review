# -*- coding: utf-8 -*-
"""[A2, 17.09.2026] TVA la încasare: o achiziție IC decontată ajunge la rd.5/rd.18, nu la rd.26.

Constatarea A2: pe calea `tva_la_incasare`, `_pull_incasare` întorcea doar `{directie, decontari}` —
fără `tert_tara`/`cui`/`axa_ic` —, iar `calcul_d300` trata orice decontare drept RO internă. O
achiziție IC de la un furnizor UE, plătită în lună, cădea la rd.26 (neimpozabil) în loc de rd.5
(achiziție IC, autolichidare) + rd.18. Proba construiește o firmă cu TVA la încasare, o factură IC
primită și decontarea ei (401 plătit), apoi generează D300. PICĂ pe codul de dinainte (rd.26), TRECE
după (rd.5). Firma efemeră, rollback la final.
"""
from __future__ import annotations

import contextlib

import pytest

from core import declaratii_api
from core import db as _db

SCH = "ztest_a2_tvai"
AN, LUNA = 2026, 9


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


@pytest.fixture
def firma_tvai(monkeypatch):
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
            # firma cu TVA LA INCASARE
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,"
                        "tva_la_incasare,tip_decont,banca,iban,declarant_nume,declarant_prenume,"
                        "declarant_functie,telefon) VALUES (1,'ZT TVAI SRL','14399840','Str 1',"
                        "'Cluj-Napoca','CJ','6202',true,true,'L','BT','RO49AAAA1B31007593840000',"
                        "'Popescu','Ion','admin','0700000000')")
            # factura PRIMITA IC (furnizor DE), cota 0, axa bunuri, in lei (RON)
            cur.execute("INSERT INTO facturi (numar,data_emitere,directie,status,total,tva,moneda,"
                        "curs_bnr,total_lei,tva_lei,tert_nume,tert_cui,tert_tara,axa_ic) "
                        "VALUES ('F-IC-1','2026-09-03','primita','emisa',5000,0,'RON',1,5000,0,"
                        "'LIEFERANT GMBH','DE811569869','DE','bunuri') RETURNING id")
            fid = cur.fetchone()[0]
            cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                        "VALUES (%s,'Marfa','buc',1,5000,0)", (fid,))
            # DECONTAREA: nota validata in luna, cont_debit 401 (plata furnizorului) legata de factura
            cur.execute("INSERT INTO inregistrari (data,descriere,sursa,status,factura_id) "
                        "VALUES ('2026-09-20','Plata furnizor','banca','validata',%s) RETURNING id", (fid,))
            nid = cur.fetchone()[0]
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) "
                        "VALUES (%s,'401','5121',5000)", (nid,))

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


def _R(res, cheie, implicit=0):
    return (getattr(res, "R", None) or {}).get(cheie, implicit)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_achizitie_ic_decontata_ajunge_la_rd5_nu_rd26(firma_tvai):
    with firma_tvai["conn"].cursor() as c:
        c.execute('SET search_path TO "%s", public' % SCH)
    _xml, res = declaratii_api.genereaza(_ConnProxy(firma_tvai["conn"]), SCH, "d300",
                                         {"an": AN, "luna": LUNA})
    # achizitie IC (autolichidare): rd.5 baza 5000 + rd.18 (oglinda), NU rd.26.
    assert _R(res, "R5_1") == 5000, "R5_1=%r (achiziție IC, autolichidare) — a căzut la rd.26?" % _R(res, "R5_1")
    assert _R(res, "R26_1", 0) == 0, "R26_1=%r — achiziția IC nu e neimpozabilă" % _R(res, "R26_1")
