# -*- coding: utf-8 -*-
"""[lotul 13, pachetul `ops`] Schema efemeră pe care rulează probele operațiunilor speciale (`uc_tenants`), în tranzacție anulată.

Aceeași formă ca probele lotului 12 (`core/test_lot12_migr_c116_reevaluare.py`): schema din `tenant_template.sql`, conexiunea testului
fără commit (use-case-ul comite la final, iar proba rămâne în tranzacția anulată), luna deschisă. Date sintetice pe 2026 într-o schemă
sintetică (`ztest_lot13_ops`), deci nicio coliziune cu datele firmelor.

`schema_ops(monkeypatch)` -> (conexiunea, cursorul pe schemă, uc_tenants). Funcțiile de mai jos scriu datele de pornire: un salariat cu CNP
valid (cifra de control verificată cu algoritmul oficial), o notă validată, o notă ciornă."""
import contextlib
import os

import pytest

from core import db as _db

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "ztest_lot13_ops"


def cnp_valid(baza12):
    """Cifra de control a CNP-ului (algoritmul oficial: ponderile 279146358279, rest 10 -> 1)."""
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    s = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    return baza12 + str(1 if s == 10 else s)


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, k):
        return getattr(self._c, k)


@contextlib.contextmanager
def schema_ops(monkeypatch):
    try:
        _db.init_pool()
    except Exception:
        pytest.skip("DB indisponibil")
    from core import tenant_provisioning as _tp, uc_tenants, uc_comun
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            # [lotul 13, 519 / 522] structura mijlocului fix pe activ (`core/migrare_mf_note.py`): până la integrarea peticului în
            # `tenant_template.sql` se aplică aici; după, e idempotentă
            from core import migrare_mf_note
            migrare_mf_note.aplica_ddl(c, SCH)
            fc = _FaraCommit(c)

            @contextlib.contextmanager
            def _gc(schema=None):
                yield fc
            monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
            monkeypatch.setattr(uc_tenants.auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
            monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda conn, schema, data: None)
            with c.cursor() as cur:
                yield c, cur, uc_tenants
        finally:
            c.rollback()


def salariat(cur, nume="Ionescu", prenume="Vasile", baza12="185010140001", salariu=6000, din="2026-01-01"):
    cur.execute("INSERT INTO salariati (nume, prenume, cnp, data_angajare) VALUES (%s, %s, %s, %s) RETURNING id",
                (nume, prenume, cnp_valid(baza12), din))
    sid = cur.fetchone()[0]
    cur.execute("INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) VALUES (%s, %s, %s)", (sid, din, salariu))
    return sid


def nota(cur, data, linii, status="validata", descriere="nota de pornire", partener=None):
    """O notă cu rândurile [(debit, credit, suma)]; `partener` = (cif, nume) pe toate rândurile."""
    cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, %s, 'manual', %s, 'Doc proba') "
                "RETURNING id", (data, descriere, status))
    nid = cur.fetchone()[0]
    for d, c_, s in linii:
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma, partener_cui, partener_nume) "
                    "VALUES (%s, %s, %s, %s, %s, %s)", (nid, d, c_, s, *(partener or (None, None))))
    return nid


def linii(cur, nid):
    cur.execute("SELECT cont_debit, cont_credit, suma::text, partener_nume FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY id",
                (nid,))
    return [tuple(r) for r in cur.fetchall()]


CTX = {"uid": 1}


def test_schema_ops_se_creeaza(monkeypatch):
    with schema_ops(monkeypatch) as (c, cur, uc):
        sid = salariat(cur)
        cur.execute("SELECT cnp FROM salariati WHERE id = %s", (sid,))
        from core.identitate import valideaza_cnp
        assert valideaza_cnp(cur.fetchone()[0])[0]
