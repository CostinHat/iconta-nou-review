# -*- coding: utf-8 -*-
"""[lotul 12, C101] Panou Admin numără la „facturi emise” și emiterile REFUZATE.

Găsită de Code la comanda 11.4 pct.2: `repo_admin.activitate_pe_cabinete` număra rândurile de audit `…/facturi/emite` fără starea
răspunsului (pe producție, 23.10.2026: 25 numărate, 11 cu răspuns 422). Clasa: TOATE contoarele de rezultat din Panou Admin care numără
rânduri de audit — „facturi emise”, „declarații depuse” (`/coada/{id}/depune`), „recomandări” (`POST /recomanda`) —, pe bara de sus
(`navigator.js`, suma pe cabinete) și pe fișa cabinetului (`admin_activitate.js`), toate din aceeași interogare. Acum: numai 2xx.
Activitatea (ultima acțiune, numărul de acțiuni) rămâne pe toate rândurile.

Temei: N/A — indicator intern al platformei (nu regulă fiscală).
"""
import json

import pytest

from core import db as _db
from core import repo_admin


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def cur():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    c = conn.cursor()
    try:
        yield c
    finally:
        conn.rollback()
        p.putconn(conn)


def _cabinet_cu_audit(cur, randuri):
    cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT C101 Contoare') RETURNING id")
    fid = cur.fetchone()[0]
    cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                "VALUES ('zt.c101@iconta.test','x','ZT','C101','admin_firma',%s,true) RETURNING id", (fid,))
    uid = cur.fetchone()[0]
    for actiune, status in randuri:
        cur.execute("INSERT INTO public.audit_log (user_id, actiune, detalii) VALUES (%s, %s, %s)",
                    (uid, actiune, json.dumps({"status": status}) if status is not None else None))
    return fid


def _randul(cur, fid):
    for r in repo_admin.activitate_pe_cabinete(cur):
        if r[0] == fid:
            return dict(zip([d[0] for d in cur.description], r))
    raise AssertionError("cabinetul sintetic lipsește din activitate")


def test_def_c101_refuzurile_nu_sunt_numarate_ca_facturi_emise(cur):
    fid = _cabinet_cu_audit(cur, [
        ("POST /tenants/1/facturi/emite", 200), ("POST /tenants/1/facturi/emite", 200),
        ("POST /tenants/1/facturi/emite", 422), ("POST /tenants/1/facturi/emite", 422), ("POST /tenants/1/facturi/emite", 422),
        ("POST /tenants/1/facturi/emite", 500), ("POST /tenants/1/facturi/emite", None),
    ])
    r = _randul(cur, fid)
    assert r["nr_facturi"] == 2            # numai cele două emiteri reușite (2xx)
    assert r["nr_actiuni"] == 7            # activitatea: toate cererile, și cele refuzate


def test_def_c101_clasa_declaratii_si_recomandari_numai_reusite(cur):
    fid = _cabinet_cu_audit(cur, [
        ("POST /coada/5/depune", 200), ("POST /coada/6/depune", 409), ("POST /coada/7/depune", 422),
        ("POST /recomanda", 201), ("POST /recomanda", 422), ("POST /recomanda", 429),
    ])
    r = _randul(cur, fid)
    assert r["nr_declaratii"] == 1
    assert r["nr_recomandari"] == 1
