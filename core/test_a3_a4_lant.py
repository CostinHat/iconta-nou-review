# -*- coding: utf-8 -*-
"""[A3, A4 — 17.09.2026] De la caz până în declarație, prin lanțul real.

A4: storno-ul unei livrări IC trebuie să SCADĂ rd.1 (D300) — copiază clasificarea originalului.
A3: o factură `anulata` NU intră în D394 și NU primește notă contabilă.

Fixtura oglindește `core/test_a1_valuta_pana_in_declaratie.py`. Probele PICĂ pe codul de dinainte
(storno neclasificabil nu scade rd.1; anulata intră în D394 + primește notă) și TREC după.
"""
from __future__ import annotations

import contextlib

import pytest

from core import auth_api, declaratii_api
from core import db as _db

SCH = "ztest_a3a4"
AN, LUNA = 2026, 9
ZI = "2026-09-05"


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
def firma(monkeypatch):
    from core import tenant_provisioning as _tp
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT A3A4') RETURNING id")
            firm = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('zt_a3a4@invalid','x','N','N','admin_firma',%s,true) RETURNING id", (firm,))
            uid = cur.fetchone()[0]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,"
                        "tip_decont,banca,iban,declarant_nume,declarant_prenume,declarant_functie,telefon) "
                        "VALUES (1,'ZT A3A4 SRL','14399840','Str Probei 1','Cluj-Napoca','CJ',"
                        "'6202',true,'L','BT','RO49AAAA1B31007593840000','Popescu','Ion','admin',"
                        "'0700000000')")
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'ZT A3A4','14399840',%s,true) RETURNING id", (SCH, firm))
            tid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)", (uid, tid))

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema
                          else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)
        yield {"tid": tid, "conn": conn,
               "tok": auth_api.emite_token({"id": uid, "rol": "admin_firma",
                                            "accounting_firm_id": firm})}
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback()
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _H(env):
    return {"Authorization": "Bearer " + env["tok"]}


def _U(env, sablon, **param):
    cale = sablon.replace("{tenant_id}", str(env["tid"]))
    for k, v in param.items():
        cale = cale.replace("{%s}" % k, str(v))
    assert "{" not in cale, cale
    return cale


def declaratie(env, tip):
    with env["conn"].cursor() as c:
        c.execute('SET search_path TO "%s", public' % SCH)
    _xml, res = declaratii_api.genereaza(_ConnProxy(env["conn"]), SCH, tip, {"an": AN, "luna": LUNA})
    return res


def _R(res, cheie, implicit=0):
    return (getattr(res, "R", None) or {}).get(cheie, implicit)


def _numar(env, sql):
    with env["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute(sql)
        return cur.fetchone()[0]


# ── A4: storno IC scade rd.1 ─────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_storno_livrare_ic_scade_rd1(firma):
    cl = _client()
    # livrare IC de bunuri catre un partener DE, cota 0
    r = cl.post(_U(firma, "/tenants/{tenant_id}/facturi/emite"), headers=_H(firma), json={
        "linii": [{"descriere": "Marfa", "cantitate": 1, "pret_unitar": 5000, "cota_tva": 0}],
        "tert_nume": "KUNDE GMBH", "tert_cui": "DE811569869", "tert_tara": "DE",
        "data_emitere": ZI, "moneda": "RON", "tip_operatiune": "normal"})
    assert r.status_code == 200, r.text
    fid = r.json()["factura_id"]
    d = declaratie(firma, "d300")
    assert _R(d, "R1_1") == 5000, "înainte de storno R1_1=%r (livrare IC bunuri)" % _R(d, "R1_1")
    # storno
    rs = cl.post(_U(firma, "/tenants/{tenant_id}/facturi/{fid}/storno", fid=fid), headers=_H(firma), json={})
    assert rs.status_code == 200, rs.text
    d2 = declaratie(firma, "d300")
    assert _R(d2, "R1_1") == 0, "storno IC n-a scăzut rd.1: R1_1=%r (așteptat 0)" % _R(d2, "R1_1")


# ── A3: factura anulata nu intra in D394 si nu primeste nota ──────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_anulata_nu_intra_in_d394_si_nu_e_contata(firma):
    cl = _client()
    r = cl.post(_U(firma, "/tenants/{tenant_id}/facturi"), headers=_H(firma), json={
        "numar": "X-9", "data_emitere": ZI, "directie": "emisa", "status": "anulata",
        "tert_nume": "BETA SRL", "tert_cui": "RO1234581",
        "linii": [{"descriere": "Marfa", "cantitate": 1, "pret_unitar": 2000, "cota_tva": 21}]})
    assert r.status_code == 200, r.text
    fid = r.json()["factura_id"]
    # nu are notă de contare (document void)
    note = _numar(firma, "SELECT count(*) FROM inregistrari WHERE factura_id=%d" % fid)
    assert note == 0, "factura anulată a primit %d note contabile (așteptat 0)" % note
    # nu intră în D394
    d394 = declaratie(firma, "d394")
    r2 = getattr(d394, "rezumat2", {})
    bazaL = sum(float(v.get("bazaL", 0)) for v in r2.values())
    assert bazaL == 0, "factura anulată a intrat în D394: bazaL=%r (așteptat 0)" % bazaL
