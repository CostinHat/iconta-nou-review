# -*- coding: utf-8 -*-
"""scripts/amprenta_productie.py — amprenta bazei de PRODUCTIE, ca sa se poata DOVEDI ca o rulare
n-a schimbat-o.

Ceruta de arhitect (11.09.2026, §9): `PRODUCTION_DB_BEFORE_FINGERPRINT` /
`PRODUCTION_DB_AFTER_FINGERPRINT` / `PRODUCTION_DB_CHANGED_BY_SUITE`.

**De ce nu poate face asta suita insasi.** Dupa R68, rolul suitei nu are `CONNECT` pe productie —
deci nici n-ar putea citi amprenta. E bine asa: instrumentul care DOVEDESTE ca nu s-a atins nimic
nu trebuie sa aiba el insusi mana acolo. Se ruleaza separat, cu acreditarile de productie, si face
NUMAI `SELECT`.

**Pe tabel, nu pe total.** O amprenta globala care se schimba spune doar «ceva s-a mutat», si atunci
urmeaza o ora de cautat. Pe tabel, schimbarea se numeste singura. Tabelele care cresc de la trafic
real (`audit_log`) se vad separat de cele care n-ar avea de ce sa se miste.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys

#: Peste atatea randuri nu se mai calculeaza md5 pe continut, doar numarul — iar tabelul
#: poarta `md5_omis=True`, ca limita sa se vada in artefact. Un STEAG, nu o propozitie:
#: o cheie `motiv` intr-un dictionar e citita de garda afirmatiilor tipate drept afirmatie
#: despre datele unei firme, si nu e — e o nota despre propria masuratoare.
PRAG_CONTINUT = 200000


def _tabele(cur):
    cur.execute(
        "SELECT table_schema, table_name FROM information_schema.tables "
        " WHERE table_type='BASE TABLE' "
        "   AND (table_schema = 'public' OR table_schema ~ '^tenant_[0-9]+$') "
        " ORDER BY 1, 2")
    return [(r[0], r[1]) if not isinstance(r, dict) else (r["table_schema"], r["table_name"])
            for r in cur.fetchall()]


def _unu(r):
    return list(r.values())[0] if isinstance(r, dict) else r[0]


def amprenta(cur):
    """{`schema.tabela`: {randuri, md5|None, motiv}}. Numai SELECT."""
    out = {}
    for schema, tabela in _tabele(cur):
        cheie = "%s.%s" % (schema, tabela)
        cur.execute('SELECT count(*) FROM "%s"."%s"' % (schema, tabela))
        n = int(_unu(cur.fetchone()))
        if n > PRAG_CONTINUT:
            out[cheie] = {"randuri": n, "md5": None, "md5_omis": True}
            continue
        # ordonarea pe textul randului intreg: nu presupune ca exista o cheie primara utilizabila
        cur.execute('SELECT md5(coalesce(string_agg(t::text, %s ORDER BY t::text), %s)) '
                    'FROM "%s"."%s" t' % ("%s", "%s", schema, tabela), ("|", ""))
        out[cheie] = {"randuri": n, "md5": _unu(cur.fetchone()), "md5_omis": False}
    return out


def globala(a):
    """Un singur sir, pentru raport. Derivata din cea pe tabel, nu masurata separat."""
    h = hashlib.sha256()
    for cheie in sorted(a):
        h.update(("%s|%s|%s\n" % (cheie, a[cheie]["randuri"], a[cheie]["md5"])).encode("utf-8"))
    return h.hexdigest()


def compara(a, b):
    """(schimbate, aparute, disparute) — fiecare cu ce s-a mutat."""
    schimbate, aparute, disparute = [], [], []
    for cheie in sorted(set(a) | set(b)):
        if cheie not in a:
            aparute.append((cheie, b[cheie]["randuri"]))
        elif cheie not in b:
            disparute.append((cheie, a[cheie]["randuri"]))
        elif a[cheie]["randuri"] != b[cheie]["randuri"] or a[cheie]["md5"] != b[cheie]["md5"]:
            schimbate.append((cheie, a[cheie]["randuri"], b[cheie]["randuri"],
                              a[cheie]["md5"], b[cheie]["md5"]))
    return schimbate, aparute, disparute


def _citeste(cale):
    return json.load(io.open(cale, encoding="utf-8"))


def main(argv):
    if len(argv) >= 3 and argv[1] == "compara":
        a, b = _citeste(argv[2]), _citeste(argv[3])
        schimbate, aparute, disparute = compara(a["tabele"], b["tabele"])
        print("INAINTE: %s" % a["globala"])
        print("DUPA   : %s" % b["globala"])
        print("SCHIMBAT: %s" % ("NU" if not (schimbate or aparute or disparute) else "DA"))
        for cheie, na, nb, ma, mb in schimbate:
            print("  ~ %-46s randuri %d -> %d%s" % (cheie, na, nb,
                  "" if ma == mb else "   (si continutul)"))
        for cheie, n in aparute:
            print("  + %-46s %d randuri" % (cheie, n))
        for cheie, n in disparute:
            print("  - %-46s avea %d randuri" % (cheie, n))
        return 0 if not (schimbate or aparute or disparute) else 1

    if len(argv) < 3 or argv[1] != "scrie":
        print("folosire: amprenta_productie.py scrie <fisier> | compara <a> <b>")
        return 2

    sys.path.insert(0, ".")
    import psycopg2
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("PICAT: DATABASE_URL lipseste — nu ghicesc baza")
        return 2
    # conexiune READ-ONLY, declarata la nivel de sesiune: instrumentul nu poate scrie nici din
    # greseala, nici daca cineva adauga cod aici maine.
    conn = psycopg2.connect(url, connect_timeout=10)
    conn.set_session(readonly=True, autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database()")
            baza = _unu(cur.fetchone())
            a = amprenta(cur)
    finally:
        conn.close()
    doc = {"baza": baza, "tabele": a, "globala": globala(a)}
    io.open(argv[2], "w", encoding="utf-8", newline="").write(
        json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True))
    print("baza: %s" % baza)
    print("tabele: %d" % len(a))
    print("amprenta: %s" % doc["globala"])
    print("scris: %s" % argv[2])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
