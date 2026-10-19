# -*- coding: utf-8 -*-
"""scripts/valideaza_note_interne_pfa.py — validarea UNICĂ a ciornelor de dinainte de lotul 9 ale firmelor în partidă simplă (PFA / II / IF).

Decizia Costin 19.10.2026 (verbatim în DECIZII „Închiderea lotului 9: poarta, producția, ciornele PFA vechi”): „Da, o dată, la publicare,
cu backup. În raport doar numărul de note validate și refuzate și motivele, fără nume de firme sau alte date ale cabinetului.”

De acum înainte notele PFA se validează automat la scriere (`uc_coada.note_interne`, deficiența 368); ciornele scrise înainte nu.
Scriptul le trece o dată pe ACELAȘI drum (`jurnal_api.valideaza_interne`: toate regulile validării — R3, casa sub zero, Z-ul
nedescărcat, perioada blocată; fiecare notă în punctul ei de salvare). O notă refuzată rămâne ciornă. Nu e o migrare: o migrare schimbă
schema, iar notele se ating numai pe drumul validării (`core/test_migrari_registru.py::test_nicio_migrare_noua_nu_scrie_*`).

Ieșirea: numai numărători — firme în partidă simplă, note validate, note refuzate pe FELUL refuzului (codul regulii). Niciun nume de
firmă, nicio schemă, nicio dată, sumă sau etichetă de notă (textul motivului le cuprinde, deci nu se tipărește).
Uz (o dată, la publicare, după backup): ./venv/bin/python scripts/valideaza_note_interne_pfa.py [--productie] [--proba]
  --proba: totul într-o tranzacție anulată (nimic scris) — aceleași numărători."""
import collections
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)


def valideaza_schema(conn, schema):
    """Ciornele unei firme în partidă simplă, pe drumul validării interne. -> (validate: int, refuzuri: Counter pe cod) sau None la o
    firmă în partidă dublă. Tranzacția e a apelantului."""
    from core import coada_api, jurnal_api
    with conn.cursor() as cur:
        if not coada_api.partida_simpla(cur):
            return None
        cur.execute("SELECT id FROM inregistrari WHERE status = 'ciorna'")
        ids = [r[0] for r in cur.fetchall()]
    if not ids:
        return 0, collections.Counter()
    v, rf = jurnal_api.valideaza_interne(conn, schema, ids, cu_cod=True)
    return len(v), collections.Counter(cod for _n, _m, cod in rf)


def main(argv):
    proba = "--proba" in argv
    if "--productie" in argv:
        from core import mediu_test
        os.environ["DATABASE_URL"] = mediu_test.dsn_productie()
    from core import db
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
        scheme = [r[0] for r in cur.fetchall()]
    firme, validate, refuzuri, sarite = 0, 0, collections.Counter(), 0
    for s in scheme:
        with db.get_conn() as conn, conn.cursor() as cur:   # o schemă fără tabelele firmei (nefinalizată) nu oprește trecerea
            cur.execute("SELECT to_regclass(%s) IS NOT NULL AND to_regclass(%s) IS NOT NULL", (s + ".inregistrari", s + ".firma_profil"))
            if not cur.fetchone()[0]:
                sarite += 1
                continue
        with db.get_conn(s) as conn:
            rez = valideaza_schema(conn, s)
            if rez is not None:
                firme += 1
                validate += rez[0]
                refuzuri.update(rez[1])
            conn.rollback() if proba else conn.commit()
    print("firme in partida simpla: %d (scheme fara tabelele firmei, sarite: %d)" % (firme, sarite))
    print("note validate ca interne: %d" % validate)
    print("note refuzate (raman ciorne): %d" % sum(refuzuri.values()))
    for cod, n in sorted(refuzuri.items()):
        print("  %s: %d" % (cod, n))
    print("(proba: nimic scris)" if proba else "(scris)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
