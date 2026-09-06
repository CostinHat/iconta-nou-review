# -*- coding: utf-8 -*-
"""REPROBARE R43 — pe ruta PUBLICĂ reală, prin HTTP, cu două firme.

`POST /public/plata/{ref}/confirma` e **neautentificată**, deci se poate apăsa exact cum ar apăsa
clientul: o cerere HTTP, fără sesiune. Asta e proba pe care o cere restanța.

**Datele le construiesc EU** (regula 3 de conducere): două scheme efemere, `ztest_r43_a` și
`ztest_r43_b`, fiecare cu o factură emisă și neplătită. Nicio factură din portofoliu nu se atinge —
iar amprenta portofoliului se citește înainte și după, ca să nu fie o afirmație.

**Cele patru întrebări, în ordinea în care contează:**
  1. o referință **necunoscută** → 404, și nimic nu se scrie nicăieri;
  2. referința firmei A → firma A e marcată;
  3. **firma B rămâne neatinsă** — asta e izolarea;
  4. marca de simulare (`plata_confirmata_de='mock'`) e pe factură, ca `platita_la` să nu treacă
     drept bani intrați.

Rulare:  PROBA_BAZA=http://127.0.0.1:8015 ./venv/bin/python frontend_test/proba_r43_izolare_plata.py
"""
import json
import os
import sys
import urllib.error
import urllib.request

_H = os.path.dirname(os.path.abspath(__file__))
_R = os.path.abspath(os.path.join(_H, ".."))
sys.path.insert(0, _R)

from core import db  # noqa: E402
from core import plati as _pl  # noqa: E402
from core import tenant_provisioning as _tp  # noqa: E402
from core import migrare_plata_referinte as _mig  # noqa: E402

BAZA = os.environ.get("PROBA_BAZA", "http://127.0.0.1:8015")
A, B = "ztest_r43_a", "ztest_r43_b"


def post(cale):
    cerere = urllib.request.Request(BAZA + cale, data=b"", method="POST")
    try:
        with urllib.request.urlopen(cerere, timeout=20) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, (e.read().decode()[:120] if e.fp else "")


def seed(conn, schema, numar):
    sablon = open(os.path.join(_R, "tenant_template.sql"), encoding="utf-8").read()
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
        cur.execute(_tp.parametrizeaza_template(sablon, schema))
        cur.execute(f"""INSERT INTO {schema}.facturi
            (numar, data_emitere, directie, status, total, moneda, tert_nume)
            VALUES (%s, '2026-09-01', 'emisa', 'emisa', 250, 'RON', 'Client proba R43')
            RETURNING id""", (numar,))
        fid = cur.fetchone()[0]
    conn.commit()
    return fid


def stare(conn, schema, fid):
    with conn.cursor() as cur:
        cur.execute(f"SELECT platita_la, plata_confirmata_de FROM {schema}.facturi WHERE id=%s", (fid,))
        return cur.fetchone()


def amprenta_portofoliu(conn):
    """Câte facturi din PORTOFOLIU poartă `platita_la`. Trebuie să nu se miște."""
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants ORDER BY id")
        n = 0
        for (s,) in cur.fetchall():
            try:
                cur.execute("SELECT count(*) FROM %s.facturi WHERE platita_la IS NOT NULL" % s)
                n += cur.fetchone()[0]
            except Exception:  # noqa: BLE001
                conn.rollback()
    return n


def main():
    db.init_pool()
    conn = db.get_conn().__enter__()
    inainte = amprenta_portofoliu(conn)
    fa, fb = seed(conn, A, "R43-A"), seed(conn, B, "R43-B")
    _mig.aplica(conn, scheme=[A, B])
    rez = {"baza": BAZA, "portofoliu_platite_inainte": inainte}

    try:
        # (1) referință necunoscută
        cod, corp = post("/public/plata/pl_nu_exista_nicaieri/confirma")
        rez["necunoscuta"] = {"status": cod}
        print("1. referință necunoscută        -> HTTP %s" % cod)

        # linkul firmei A, pe drumul aplicației
        r = _pl.genereaza_link(conn, A, fa, BAZA, tenant_id=-1)
        assert r.get("ref"), r
        rez["ref"] = r["ref"]

        # (2)+(3) confirmarea, prin HTTP
        cod2, corp2 = post("/public/plata/%s/confirma" % r["ref"])
        rez["confirmare"] = {"status": cod2, "corp": corp2}
        print("2. confirmare pe firma A        -> HTTP %s %s" % (cod2, corp2))

        pa, ca = stare(conn, A, fa)
        pb, cb = stare(conn, B, fb)
        rez["firma_a"] = {"platita_la": str(pa), "confirmata_de": ca}
        rez["firma_b"] = {"platita_la": str(pb), "confirmata_de": cb}
        print("3. firma A: platita_la=%s · confirmata_de=%r" % (pa is not None, ca))
        print("   firma B: platita_la=%s · confirmata_de=%r  <- trebuie NEATINSĂ" % (pb is not None, cb))

        dupa = amprenta_portofoliu(conn)
        rez["portofoliu_platite_dupa"] = dupa
        print("4. facturi plătite în PORTOFOLIU: %d -> %d" % (inainte, dupa))

        with open(os.path.join(_H, "proba_r43_izolare_plata.json"), "w", encoding="utf-8") as f:
            json.dump(rez, f, ensure_ascii=False, indent=1)

        assert cod == 404, "o referință necunoscută trebuie refuzată, am primit %s" % cod
        assert cod2 == 200, "confirmarea firmei A a eșuat: %s" % cod2
        assert pa is not None and ca == "mock", "firma A: %r / %r" % (pa, ca)
        assert pb is None and cb is None, "IZOLARE CĂZUTĂ — firma B a fost atinsă: %r / %r" % (pb, cb)
        assert dupa == inainte, "s-a atins portofoliul: %d -> %d" % (inainte, dupa)
        print("\nOK: o firmă atinsă, cealaltă nu, referința necunoscută refuzată, "
              "plata poartă marca de simulare.")
    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM public.plata_referinte WHERE schema_name IN (%s, %s)", (A, B))
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % A)
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % B)
        conn.commit()
        print("(schemele efemere și perechile lor, șterse)")


main()
