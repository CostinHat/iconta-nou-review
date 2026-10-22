# -*- coding: utf-8 -*-
"""[lotul 11, decizia Costin 10.3 pct.4, verbatim în DECIZII „Comanda 10.3”: „declarațiile citesc din fișă când factura nu are”] Proba de
comportament a rutelor fișei furnizorului — POST /tenants/{tenant_id}/furnizori (`furnizor_creeaza`) și PUT
/tenants/{tenant_id}/furnizori/{furnizor_id} (`furnizor_actualizeaza`), corpurile lor din `uc_tenants` — până în sursa din care declarațiile
își iau județul / localitatea partenerului (`clienti_api.sql_camp_fisa`, citită de `repo_d394` / D406): o factură primită fără județ ia
județul din fișa scrisă de rută, iar corectura fișei se vede la următoarea generare. Plus 444: butonul „Actualizează fișa cu numele de la
ANAF” trimite numai `nume` — celelalte câmpuri ale fișei rămân.
(`scripts/scan_rute_fara_proba.py`: rutele scriu în tabele citite de generatoare — `core/test_rute_probate.py`.)
Temei: N/A — sursa județului e decizia lui Costin 10.3; codul județului e nomenclatorul aplicației (`factura_pdf.JUDETE_NUME`).
Schemă efemeră din template, în tranzacție anulată."""
import contextlib
import io
import types

import pytest
from psycopg2.extras import RealDictCursor

from core import db as _db, tenant_provisioning as _tprov
from core.test_418_import_efactura import _ConnProxy, _db_ok


def _corp(**k):
    return types.SimpleNamespace(model_dump=lambda: dict(k))


@contextlib.contextmanager
def _firma(monkeypatch):
    _db.init_pool()
    SCH = "efemer_p2_fisa_furnizor"
    c = _db.pool().getconn()
    try:
        with c.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('EF P2 FZ') RETURNING id"); fid = cur.fetchone()["id"]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                        "VALUES ('ef_p2_fz@invalid','x','N','N','admin_firma',%s,true) RETURNING id", (fid,)); uid = cur.fetchone()["id"]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET LOCAL search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'F1 SRL','9010105',%s,true) RETURNING id", (SCH, fid)); tid = cur.fetchone()["id"]
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)", (uid, tid))

        @contextlib.contextmanager
        def _fake(schema=None):
            with c.cursor() as cc:
                cc.execute('SET LOCAL search_path TO "%s", public' % schema if schema else "SET LOCAL search_path TO public")
            yield _ConnProxy(c)
        monkeypatch.setattr(_db, "get_conn", _fake)
        yield {"c": c, "sch": SCH, "tid": tid, "ctx": {"uid": uid, "rol": "admin_firma", "accounting_firm_id": fid, "firm": fid}}
    finally:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.rollback()
        _db.pool().putconn(c)


def _judet_si_oras_citite(f, fid):
    from core import clienti_api
    with f["c"].cursor() as cur:
        cur.execute('SET LOCAL search_path TO "%s", public' % f["sch"])
        cur.execute("SELECT " + clienti_api.sql_camp_fisa("judet") + ", " + clienti_api.sql_camp_fisa("oras") + " FROM facturi f WHERE f.id = %s",
                    (fid,))
        return cur.fetchone()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fisa_scrisa_de_rute_ajunge_in_judetul_citit_de_declaratii(monkeypatch):
    from core import uc_tenants
    with _firma(monkeypatch) as f:
        with f["c"].cursor() as cur:
            cur.execute('SET LOCAL search_path TO "%s", public' % f["sch"])
            # factura primită de la un furnizor fără județ pe document (CUI 14399840 — cifra de control verificată)
            cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_cui, tert_nume, status) "
                        "VALUES ('P2-FZ-1', '2026-09-10', 'primita', 121, 21, '14399840', 'DANTE SRL', 'primita') RETURNING id")
            fact = cur.fetchone()[0]
        assert _judet_si_oras_citite(f, fact) == (None, None)   # fără fișă: nimic de citit (generatorul refuză, cu ecranul fișei)
        r = uc_tenants.furnizor_creeaza(f["tid"], _corp(nume="DANTE SRL", cui="RO 14399840", oras="Cluj-Napoca", judet="CJ"), f["ctx"])
        fz = r.get("furnizor_id") or r.get("id")
        assert r.get("ok") is not False and fz, r
        # decizia 10.3: „declarațiile citesc din fișă când factura nu are” — și CUI-ul scris cu „RO ” se potrivește (forma păstrată)
        assert _judet_si_oras_citite(f, fact) == ("CJ", "Cluj-Napoca")
        r = uc_tenants.furnizor_actualizeaza(f["tid"], fz, _corp(oras="București", judet="B"), f["ctx"])
        assert r["ok"] is True, r
        assert _judet_si_oras_citite(f, fact) == ("B", "București")   # corectura fișei se vede la următoarea generare
        # 444: „Actualizează fișa cu numele de la ANAF” trimite numai numele; localitatea și județul fișei rămân
        r = uc_tenants.furnizor_actualizeaza(f["tid"], fz, _corp(nume="DANTE INTERNATIONAL SA"), f["ctx"])
        assert r["ok"] is True, r
        with f["c"].cursor() as cur:
            cur.execute('SET LOCAL search_path TO "%s", public' % f["sch"])
            cur.execute("SELECT nume, cui, oras, judet FROM furnizori WHERE id = %s", (fz,))
            assert cur.fetchone() == ("DANTE INTERNATIONAL SA", "14399840", "București", "B")
