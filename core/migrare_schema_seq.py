# -*- coding: utf-8 -*-
"""core/migrare_schema_seq.py — R79/T1: contorul de nume de schemă, care nu coboară.

DE CE EXISTĂ. `urmator_schema_name` lua `max(NNN)+1` peste firmele **vii**. Când cea mai mare era
ștearsă, maximul cobora și numărul se **refolosea** — măsurat pe date: `tenant_019` a fost, în
aceeași zi, numele a două firme diferite. Decizia lui Costin, 28.08.2026: **oprim reciclarea.**

DE UNDE PORNEȘTE CONTORUL, și de ce nu de la maximul firmelor vii: de la **maximul istoric** —
`public.tenants` ∪ `public.firme_scoase`. Dacă ar porni de la cel viu, primul nume generat ar fi
chiar unul deja folosit de o firmă scoasă, adică fix reciclarea pe care o repară.

DE CE O SECVENȚĂ, nu un rând cu maximul: `nextval` **nu se întoarce la rollback**. Un provisioning
eșuat arde un număr, ceea ce e exact ce vrem; un contor într-un rând ar fi întors odată cu
tranzacția și ar putea da același nume de două ori.

Idempotentă: `CREATE SEQUENCE IF NOT EXISTS` + `setval` la maximul istoric, **numai dacă** secvența
e în urmă. O a doua rulare nu mișcă nimic.

  python3 -m core.migrare_schema_seq
"""
import re
import sys

from core import db

SECVENTA = "public.tenant_schema_seq"
_RE = re.compile(r"^tenant_(\d+)$")


def maxim_istoric(conn):
    """Cel mai mare NNN văzut vreodată: firme vii + firme scoase + scheme existente în bază.

    Toate trei, nu doar prima. `firme_scoase` ține numele firmelor șterse — chiar mulțimea pe care
    calculul vechi o pierdea. Iar `information_schema` prinde o schemă rămasă fără rând, dacă a
    existat vreodată una.
    """
    n = 0
    with conn.cursor() as cur:
        for sql in ("SELECT schema_name FROM public.tenants",
                    "SELECT schema_name FROM public.firme_scoase",
                    "SELECT schema_name FROM information_schema.schemata"):
            cur.execute(sql)
            for (s,) in cur.fetchall():
                m = _RE.match(s or "")
                if m:
                    n = max(n, int(m.group(1)))
    return n


def aplica(conn):
    istoric = maxim_istoric(conn)
    with conn.cursor() as cur:
        cur.execute("CREATE SEQUENCE IF NOT EXISTS %s AS bigint MINVALUE 1" % SECVENTA)
        cur.execute("SELECT last_value, is_called FROM %s" % SECVENTA)
        last, chemat = cur.fetchone()
        curent = last if chemat else last - 1
        if curent < istoric:
            cur.execute("SELECT setval(%s, %s, true)", (SECVENTA, istoric))
            mutat = True
        else:
            mutat = False
    conn.commit()
    return istoric, curent, mutat


def main():
    db.init_pool()
    with db.get_conn() as conn:
        istoric, curent, mutat = aplica(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT last_value FROM %s" % SECVENTA)
            acum = cur.fetchone()[0]
    print("maxim istoric: tenant_%03d · contor era la %d · acum la %d%s"
          % (istoric, curent, acum, " (mutat)" if mutat else " (neschimbat)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
