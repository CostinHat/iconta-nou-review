# -*- coding: utf-8 -*-
"""[A1, 17.09.2026] Factura în VALUTĂ, de la caz până în decont — prin lanțul real.

Constatarea A1: o factură în EUR intra în D300/D394 și în nota contabilă (4111/4427) cu sumele ÎN
VALUTĂ. Aici emitem o factură de 1.000 EUR la curs 5 prin ruta reală și verificăm, pas cu pas:
  1. răspunsul rutei poartă `total_lei=6050`, `tva_lei=1050` (nu 1210/210);
  2. NOTA automată e în LEI: 4111=704 pe 5000, 4111=4427 pe 1050 (nu 1000/210);
  3. D300 rd.9: R9_1=5000, R9_2=1050;
  4. D394: bazaL/tvaL = 5000/1050.

Fixtura oglindește `core/test_scrieri_pana_in_declaratie.py` (firmă efemeră, conexiune din pool,
rollback la final). PICA pe codul de dinainte de A1 (generatoarele citeau valuta) și TRECE după.
"""
from __future__ import annotations

import contextlib

import pytest

from core import auth_api, declaratii_api
from core import db as _db

SCH = "ztest_a1_valuta"
AN, LUNA = 2026, 8
ZI = "2026-08-10"


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
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT A1') RETURNING id")
            firm = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('zt_a1@invalid','x','N','N','admin_firma',%s,true) RETURNING id", (firm,))
            uid = cur.fetchone()[0]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,"
                        "tip_decont,banca,iban,declarant_nume,declarant_prenume,declarant_functie,telefon) "
                        "VALUES (1,'ZT A1 SRL','14399840','Str Probei 1','Cluj-Napoca','CJ',"
                        "'6202',true,'L','BT','RO49AAAA1B31007593840000','Popescu','Ion','admin',"
                        "'0700000000')")
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'ZT A1','14399840',%s,true) RETURNING id", (SCH, firm))
            tid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)",
                        (uid, tid))

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
    assert "{" not in cale, "au rămas parametri necompletați în %r" % cale
    return cale


def _emite_eur(cl, env):
    return cl.post(_U(env, "/tenants/{tenant_id}/facturi/emite"), headers=_H(env), json={
        "linii": [{"descriere": "Servicii", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21}],
        "tert_nume": "CLIENT RO SRL", "tert_cui": "RO1234573", "tert_tara": "RO",
        "data_emitere": ZI, "moneda": "EUR", "curs_manual": 5, "data_curs_manual": ZI})


def _nota_factura(env, factura_id):
    with env["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute("SELECT l.cont_debit, l.cont_credit, l.suma "
                    "FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                    "WHERE i.factura_id = %s ORDER BY l.id", (factura_id,))
        return [(d, c, s) for (d, c, s) in cur.fetchall()]


def declaratie(env, tip):
    with env["conn"].cursor() as c:
        c.execute('SET search_path TO "%s", public' % SCH)
    _xml, res = declaratii_api.genereaza(_ConnProxy(env["conn"]), SCH, tip,
                                         {"an": AN, "luna": LUNA})
    return res


def _R(res, cheie, implicit=0):
    return (getattr(res, "R", None) or {}).get(cheie, implicit)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_eur_raspunsul_rutei_e_in_lei(firma):
    cl = _client()
    r = _emite_eur(cl, firma)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j.get("ok") is True, j
    assert float(j["total_lei"]) == 6050.0, "total_lei=%r (asteptat 6050 = 1210 EUR x 5)" % j.get("total_lei")
    assert float(j["tva_lei"]) == 1050.0, "tva_lei=%r (asteptat 1050 = 210 EUR x 5)" % j.get("tva_lei")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_eur_nota_e_in_lei(firma, monkeypatch):
    # Probă DETERMINISTĂ, independentă de cheia AI: contul de venit al liniei se deduce
    # din denumire NUMAI prin AI (cote_tva.potriveste_cota); fără cheie cade pe default-ul
    # firmei (707). Stubăm clasificatorul pe rezultatul corect pentru "Servicii" (704,
    # OMFP 1802/2014). Lipsa unei reguli deterministe non-AI = restanță de decizie (v. raport),
    # nu se repară aici.
    from core import cote_tva as _ct
    monkeypatch.setattr(_ct, "potriveste_cota", lambda denumire, platitor_tva=True: {
        "ok": True, "cota": 21, "tip": "servicii", "categorie": "standard",
        "justificare": "stub test", "incredere": "mare", "sursa": "regula"})
    cl = _client()
    fid = _emite_eur(cl, firma).json()["factura_id"]
    note = _nota_factura(firma, fid)
    assert note, "factura EUR n-a produs nicio notă"
    # 4111 = 704 pe baza (5000 lei; serviciu, OMFP 1802/2014), 4111 = 4427 pe TVA (1050 lei) — NU 1000/210 (valuta).
    baza = [s for (d, c, s) in note if c == "704" and d == "4111"]
    tvac = [s for (d, c, s) in note if c == "4427" and d == "4111"]
    assert baza and float(baza[0]) == 5000.0, "baza notei = %r (asteptat 5000 lei); nota=%r" % (baza, note)
    assert tvac and float(tvac[0]) == 1050.0, "TVA notei = %r (asteptat 1050 lei); nota=%r" % (tvac, note)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_eur_intra_in_d300_si_d394_in_lei(firma):
    cl = _client()
    _emite_eur(cl, firma)
    d300 = declaratie(firma, "d300")
    assert _R(d300, "R9_1") == 5000, "D300 R9_1=%r (asteptat 5000 lei)" % _R(d300, "R9_1")
    assert _R(d300, "R9_2") == 1050, "D300 R9_2=%r (asteptat 1050 lei)" % _R(d300, "R9_2")
    d394 = declaratie(firma, "d394")
    # rezumat2 pe cota 21: bazaL = 5000, tvaL = 1050
    r2 = getattr(d394, "rezumat2", {})
    bazaL = sum(float(v.get("bazaL", 0)) for v in r2.values())
    assert bazaL == 5000.0, "D394 bazaL=%r (asteptat 5000 lei); rezumat2=%r" % (bazaL, r2)
