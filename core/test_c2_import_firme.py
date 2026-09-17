# -*- coding: utf-8 -*-
"""[C2, 17.09.2026] Import în masă de firme: răspunsul „creat" corespunde bazei.

Constatarea C2: bucla `provision_tenant` rula într-o SINGURĂ tranzacție; o eroare psycopg2 (denumire
prea lungă) aborta tranzacția, firmele următoare picau cu „current transaction is aborted", iar la
ieșirea din `with`, commitul pe tranzacție abortată = ROLLBACK tăcut — răspunsul spunea „creat", baza
nu conținea nimic. Reparația: SAVEPOINT per firmă (prin `core.tranzactie`) + validare lungime. Proba
importă 4 firme, a treia cu denumire de 300 de caractere; verifică pe o conexiune PROASPĂTĂ (deci doar
date COMISE) că firmele valide EXISTĂ. PICĂ pe codul de dinainte (rollback tăcut), TRECE după.

Nu folosește monkeypatch de conexiune: ruta scrie prin pool-ul real (commituri per `with get_conn`),
iar proba verifică datele comise. Tenanții sintetici se șterg în teardown.
"""
from __future__ import annotations

import pytest

from core import auth_api, uc_comun as _uc_comun
from core import db as _db

_CUI = ["2000007", "2000015", "2000031"]   # valide; a patra de sub e lungă


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def cabinet(monkeypatch):
    monkeypatch.setattr(_uc_comun, "_TENANT_TEMPLATE",
                        open("tenant_template.sql", encoding="utf-8").read())
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    with conn.cursor() as cur:
        # idempotent: curăță resturi de la o rulare anterioară întreruptă (email unic)
        cur.execute("SELECT accounting_firm_id FROM public.users WHERE email='zt_c2@invalid'")
        for (fv,) in cur.fetchall():
            if fv:
                cur.execute("SELECT schema_name FROM public.tenants WHERE accounting_firm_id=%s", (fv,))
                for (s,) in cur.fetchall():
                    if s:
                        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % s)
                cur.execute("DELETE FROM public.tenants WHERE accounting_firm_id=%s", (fv,))
        cur.execute("DELETE FROM public.users WHERE email='zt_c2@invalid'")
        cur.execute("DELETE FROM public.accounting_firms WHERE nume='ZT C2'")
        # [C2] provision_tenant avansează IREVERSIBIL secvența de scheme (non-tranzacțională); o salvăm
        # și o restaurăm în teardown, ca proba să nu bumpuiască permanent contorul (altfel blocul de
        # cifre-date din PREDARE_LANT.md, care îl citește, devine stale după fiecare rulare).
        cur.execute("SELECT last_value, is_called FROM public.tenant_schema_seq")
        _seq_before = cur.fetchone()
        cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT C2') RETURNING id")
        firm = cur.fetchone()[0]
        cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                    "accounting_firm_id,activ) VALUES "
                    "('zt_c2@invalid','x','N','N','admin_firma',%s,true) RETURNING id", (firm,))
        uid = cur.fetchone()[0]
    conn.commit()
    p.putconn(conn)
    try:
        yield {"firm": firm, "pool": p,
               "tok": auth_api.emite_token({"id": uid, "rol": "admin_firma",
                                            "accounting_firm_id": firm})}
    finally:
        # teardown COMPLET: dropez schemele + șterg TOATE tabelele public cu tenant_id ale tenanților
        # creați (altfel provision_tenant lasă orfani în audit_log/firma_sursa_versiune/... — prinși de
        # test_tenant_stergere). Lista tabelelor din sursa unică `tenant_stergere.TABELE_TENANT`.
        from core.tenant_stergere import TABELE_TENANT
        c = p.getconn()
        try:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("SELECT id, schema_name FROM public.tenants WHERE accounting_firm_id=%s", (firm,))
                rows = cur.fetchall()
                for (tid, s) in rows:
                    if s:
                        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % s)
                    for t in TABELE_TENANT:
                        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema='public' "
                                    "AND table_name=%s AND column_name='tenant_id'", (t,))
                        if cur.fetchone():
                            cur.execute("DELETE FROM public.%s WHERE tenant_id=%%s" % t, (tid,))
                cur.execute("DELETE FROM public.tenants WHERE accounting_firm_id=%s", (firm,))
                cur.execute("DELETE FROM public.users WHERE accounting_firm_id=%s", (firm,))
                cur.execute("DELETE FROM public.accounting_firms WHERE id=%s", (firm,))
                # [C2] restaurez secvența la valoarea de dinainte de probă (schemele create au fost drop-ate)
                if _seq_before is not None:
                    cur.execute("SELECT setval('public.tenant_schema_seq', %s, %s)",
                                (_seq_before[0], _seq_before[1]))
            c.commit()
        finally:
            p.putconn(c)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_import_partial_raspunsul_corespunde_bazei(cabinet):
    cl = _client()
    lung = "X" * 300
    r = cl.post("/migrare/importa", headers={"Authorization": "Bearer " + cabinet["tok"]}, json={
        "firme": [
            {"cui": _CUI[0], "denumire": "FIRMA UNU SRL"},
            {"cui": _CUI[1], "denumire": "FIRMA DOI SRL"},
            {"cui": "40372003", "denumire": lung},          # CUI valid; denumire prea lungă -> respinsă
            {"cui": _CUI[2], "denumire": "FIRMA PATRU SRL"},
        ]})
    assert r.status_code == 200, r.text
    j = r.json()
    creat = j.get("creat") or []
    cuiuri_create = {str(c.get("cui")) for c in creat}
    # verificăm pe o conexiune PROASPĂTĂ (doar date COMISE)
    cv = cabinet["pool"].getconn()
    try:
        cv.rollback()
        with cv.cursor() as cur:
            cur.execute("SELECT cui FROM public.tenants WHERE accounting_firm_id=%s", (cabinet["firm"],))
            in_baza = {str(row[0]) for row in cur.fetchall()}
    finally:
        cabinet["pool"].putconn(cv)
    # cele trei valide sunt COMISE în bază; cea lungă NU
    for c in _CUI:
        assert c in in_baza, "firma validă %s LIPSEȘTE din bază (rollback tăcut?): în bază=%r" % (c, in_baza)
    assert "40372003" not in in_baza, "firma cu denumire prea lungă a intrat în bază"
    # răspunsul „creat" nu minte
    assert cuiuri_create <= in_baza, "răspunsul spune «creat» firme care NU sunt în bază: creat=%r bază=%r" % (cuiuri_create, in_baza)
